# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'resume_parser.py' file to write the logic for resume parsin. 
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.


# When user upload the resume, our backend will not receive the nicely structured document or data but actually received the bytes or stream of data actually
# So backend will not have anu idea that the received data is pdf or doc or etc, so for that we need to make use of io and magic to determine that
# So this resume_parser file will acts as the gateway between the input resume file & the backend & through this we will identify the type of file & other things.

import io
import logging


import glob
import magic    # it is used to check the type of file like whether the uploaded pdf file is actually pdf or not
# Actual pdf files internally in backend starts with %pdf sign

# Explicitly load libmagic from system path
def get_magic():
    # Find the shared library
    lib_candidates = glob.glob("/usr/lib/**/libmagic.so*", recursive=True)
    if not lib_candidates:
        raise RuntimeError("libmagic shared library not found")

    # Find the magic database file (*.mgc)
    mgc_candidates = glob.glob("/usr/share/misc/magic.mgc")
    if not mgc_candidates:
        raise RuntimeError("magic.mgc database file not found")

    print("Using libmagic at:", lib_candidates[0])
    print("Using magic.mgc at:", mgc_candidates[0])

    # Bind both
    return magic.Magic(mime=True, magic_file=mgc_candidates[0])


magic_instance = get_magic()



from typing import Tuple, Optional
# here we are importing these Tuple, Optional from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.


# A library specialized for extracting text, tables, and metadata from PDF files.
import pdfplumber     # it will be used to parse the pdf
# Comes from the python-docx package. Lets you read and write Microsoft Word .docx files.
from docx import Document    # it will be used to parse the document
import PyPDF2     # it will also be used to parse the pdf
# here we are using two pdf package because we want that if something is missed by pdfplumber, then that can be parse by this PyPDF2, so it will act as the fallback actually
# Another PDF library, but more general-purpose. Can split, merge, rotate, encrypt, and extract metadata from PDFs.
# Its text extraction is less sophisticated than pdfplumber, but it’s reliable as a fallback.


# here we are importing all these from the file_utils file
from backend.utils.file_utils import(
    FileParsingError,
    TextExtractionError,
    FileUploadError,
    log_error,
    log_warning,
    log_info,
    with_fallback
)


# MIME type is a standard that indicates the nature and format of a file. It is used to identify the type of file being uploaded or processed. In our case, we will be accepting resumes in PDF, DOC, and DOCX formats. So we need to define the supported MIME types for these file formats and their corresponding short names. This way we can easily identify the type of file being uploaded and process it accordingly.
from backend.core.config import(
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    SUPPORTED_MIME_TYPES      # this actually show the allowed file types which we mention in config file
)

logger = logging.getLogger('ats_resume_scorer')



# Both inherit from Python’s built‑in Exception class.
# By subclassing Exception, you create specialized error types that can be raised and caught separately.
# The pass keyword means they don’t add any new behavior — they’re just distinct names for different error conditions.
# Instead of raising a generic Exception, you can raise a specific one that tells you exactly what went wrong.
# FileParsingError → something failed while parsing the file (e.g., corrupted PDF, unreadable DOCX).
# FileValidationError → the file failed validation checks (e.g., wrong format, unsupported type).

# so we are using these two separate classes to differentiate these two types of error here 

class FileParsingError(Exception):
    pass


class FileValidationError(Exception):
    pass




# The purpose of this fn is to check whether an uploaded file is valid (correct type, not corrupted, etc.).
# here we are taking file_data as input of type bytes :- The raw binary content of the file (e.g., what you get when a user uploads a resume).
# Using bytes means the function can handle any file type (PDF, DOCX, etc.).
# filename: str :- The name of the file (e.g., "resume.pdf"). Useful for checking the extension or logging errors.
# The function returns a tuple with three values. And this Optional[str] → MIME type (or None)
def validate_file(file_data: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
    file_size_bytes = len(file_data)
    log_info(f'Validating uploaded file {filename} ({file_size_bytes} bytes)', context='validate_file')
    # This variable holds the raw binary content of the file (e.g., a PDF or DOCX resume).Typically obtained by reading a file in binary mode.
    # Since file_data is a bytes object, len(file_data) gives the number of bytes in the file. This is effectively the file siz
    # e.g file_data = b"Hello World", then file_size_bytes = len(file_data), so this print(file_size_bytes)  # Output: 11


    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        size_mb = file_size_bytes / (1024 * 1024)

        return False, (
            f'File size ({size_mb:.2f} MB) exceeds the maximum of {MAX_FILE_SIZE_MB} MB. '
            'Please upload a smaller file or compress your resume.' 
        ), None
    # size_mb:.2f → formatted to 2 decimal places.
    

    if file_size_bytes==0:
        return False, 'Uploaded file is empty. Please check the file you have uploaded and try again'
    

    # As File type detection can fail (corrupted file, unsupported format, or library error).so that's why we are using try except block here
    try:
        # Uses magic to inspect the raw file bytes (file_data) and determine the MIME type (e.g., "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document").
        # This is more reliable than just checking the file extension.
        # mime_type = magic.from_buffer(file_data, mime=True)
        mime_type = magic_instance.from_buffer(file_data)
        log_info(f'Detected MIME type {mime_type} for file {filename}', context='validate_file')
    except Exception as e:
        log_error(e, context='validate_file')
        return False, f"error in determining the file type : {e}", None
    

    if mime_type not in SUPPORTED_MIME_TYPES:
        # here we are building a string of supported file types for the error message.
        supported = ', '.join(SUPPORTED_MIME_TYPES.keys()).upper()

        log_warning(f'Unsupported MIME type {mime_type} for file {filename}', context='validate_file')
        return False, (
            f'Unsupported file type: {mime_type}. '
            f'Please upload one of: {supported}.'
        ), None
    

    return True, '', SUPPORTED_MIME_TYPES[mime_type]
    # Looks up the detected MIME type in your dictionary of supported types & also return that here.



# In Python, putting an underscore (_) at the front of a function name (like _get_headers) is a naming convention that signals: Private / internal use
# It tells other developers: “This function is meant for internal use inside this module/class, not part of the public API.”
# Python doesn’t enforce strict privacy (like private in Java or C++), but the underscore is a strong hint.
# public_api_call() is the function you expect other modules or users to call.
# If someone imports your module with from mymodule import *, _get_headers will not be imported automatically because of the underscore.

# In Resumes, we actually have two types of layers :-
# visible layer : which contains sections, titles, project headings, experience titles, etc
# annotation layer : which contains hyperlinks i.e linkedin link, portfolio link, etc
# so extraction of these hyperlinks are not simple & normal extraction will only copy the link as normal sentence or word only & not consider them as actual link.
# So we need to handle this hyperlink extract separately using this fn.
# here return type of this fn will be string actually
def _extract_pdf_hyperlinks(file_data: bytes) -> str:
    urls = []

    # here we are using try except block because PDFs can be messy: broken annotations, missing fields, or unexpected structures. Without try/except, one bad annotation would crash the entire extraction.
    # Also get_object() can fail if the reference is broken. Accessing dictionary keys like page['/Annots'] or annot.get('/A') can throw exceptions if the structure isn’t what we expect.
    try: 
        # file_data is the raw binary content of the uploaded file (e.g., a PDF resume). io.BytesIO creates an in‑memory file‑like object from those bytes. It behaves just like a file opened with open("resume.pdf", "rb"), but without writing anything to disk.
        # PdfReader is a class from the PyPDF2 library that reads and parses PDF files. It expects a file path or a file‑like object. By passing io.BytesIO(file_data), you’re telling PyPDF2: “Here’s a PDF stored in memory — treat it like a file and parse it.
        reader = PyPDF2.PdfReader(io.BytesIO(file_data))
        
        for page in reader.pages:
            # Checks if the page has annotations (/Annots). Annotations are things like links, comments, highlights.
            if '/Annots' not in page:
                continue

            for annot_ref in page['/Annots']:
                try:
                    # In a PDF, things like links, highlights, or comments are stored as annotations. When you access page['/Annots'], you don’t immediately get the full annotation data.
                    # Instead, you often get indirect references (pointers) to objects inside the PDF file structure.
                    # annot_ref.get_object() follows that pointer and retrieves the actual annotation dictionary.
                    # This dictionary contains all the properties of the annotation, such as:
                    # /Subtype → type of annotation (e.g., /Link for hyperlinks).
                    # /A → action dictionary (what happens when clicked).
                    # /URL → the actual web address if it’s a link.
                    annot = annot_ref.get_object()

                    if annot.get('/Subtype') != '/Link':
                        continue

                    # In PDF specs, /A stands for the Action dictionary — it describes what happens when you click the annotation.
                    # For link annotations, /A usually contains details like:
                    # {
                    #     '/S': '/URI',          # Action type: URI (web link)
                    #     '/URI': 'https://example.com'
                    # }
                    action = annot.get('/A', {})
                    url = action.get('/URL', '')

                    if url and isinstance(url, (str, bytes)):    # Ensures url is either a string or raw byt
                        # PyPDF2 may return bytes for URL values
                        if isinstance(url, bytes):
                            # if URL is bytes, then this decodes it into a proper UTF‑8 string.
                            url = url.decode('utf-8', errors='ignore')
                        
                        url = url.strip()

                        if url.startswith('http'):
                            urls.append(url)
                            # Only accepts URLs that start with "http" (covers both http:// and https://).
                            #This filters out non‑web links (like mailto: or internal PDF references).
                except Exception:
                    pass

    except Exception:
        pass

    return '\n'.join(urls)




def _extract_pdf_with_pdfplumber(file_data: bytes) -> str:
    text = ''

    # file_data is raw binary content of the PDF. io.BytesIO(file_data) wraps those bytes into a file‑like object (so you don’t need to save it to disk). pdfplumber.open(...) opens the PDF for reading.
    # The with block ensures the file is closed automatically after use.
    with pdfplumber.open(io.BytesIO(file_data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + '\n'

    
    if not text.strip():
        raise TextExtractionError(
            'pdfplumber extracted no text',
            user_message='No text could be extracted from the PDF.'
        )
    

    hyperlinks = _extract_pdf_hyperlinks(file_data)

    if hyperlinks:
        text = text.strip() + '\n' + hyperlinks

    return text.strip()




def _extract_pdf_with_pypdf2(file_data: bytes) -> str:
    text = ''

    # file_data is the raw binary content of the uploaded PDF file.
    # io.BytesIO wraps those raw bytes into a file‑like object that behaves like a real file opened in binary mode. This is important because PyPDF2 expects either:
    # A file path ("resume.pdf")
    # Or a file‑like object (something with .read() and .seek() methods).
    # PdfReader is the class in PyPDF2 that parses and loads the PDF structure.
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))


    for page in pdf_reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + '\n'

    
    if not text.strip():
        raise TextExtractionError(
            'PyPDF2 extracted no text',
            user_message='No text could be extracted from the PDF.'
        )
    

    hyperlinks = _extract_pdf_hyperlinks(file_data)

    if hyperlinks:
        text = text.strip() + '\n' + hyperlinks

    return text.strip()



# This function is your main PDF text extraction pipeline.
def extract_text_from_pdf(file_data: bytes) -> str:
    try:
        log_info('Extracting text from PDF', context='resume_parser')
        result, used_fallback = with_fallback(
            _extract_pdf_with_pdfplumber,
            _extract_pdf_with_pypdf2,
            file_data,
            log_fallback=True
        )

        if used_fallback:
            log_info('PDF extraction succeeded using the PyPDF2 fallback', context='resume_parser')
        else:
            log_info('PDF extraction succeeded using pdfplumber', context='resume_parser')

        return result
    
    # It is the error‑handling section of your PDF text extraction function.
    except Exception as e:
        log_error(e, context='extract_text_from_pdf')
        logger.error('PDF extraction failed: %s', e)

        raise FileParsingError(
            'Failed to extract text from PDF using both pdfplumber and PyPDF2. '
            'The PDF may be corrupted, password-protected, or contain only scanned images. '
            'Please ensure it contains selectable text.'
        ) from e
        # from e preserves the original exception as the cause. This means debugging tools can still trace back to the root error.
    


# It is defining a helper function that extracts text from a Word .docx file.
def extract_text_from_docx(file_data: bytes) -> str:
    try:
        # file_data → raw binary content of the uploaded .docx file. io.BytesIO(file_data) → wraps those bytes into an in‑memory file‑like object (so you don’t need to save the file to disk).
        # Document(...) → loads the DOCX file using python-docx. This gives you a Document object that represents the entire Word file.
        # From here, you can access:
        # doc.paragraphs → all paragraphs in the document.
        # doc.tables → all tables in the document.
        # doc.core_properties → metadata (author, title, etc.).
        doc = Document(io.BytesIO(file_data))

        text_parts = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)

        text = '\n'.join(text_parts)

        if not text.strip():
            raise FileParsingError(
                'No text could be extracted from the document. '
                'The document may be empty or corrupted.'
            )
        

        try:
            # A DOCX file is essentially a ZIP archive with XML parts. 
            # doc.part.rels → gives you all relationships defined in the document.
            # Relationships describe links between parts of the document (e.g., images, styles, hyperlinks). 
            # .values() → iterates over all relationship objects.
            for rel in doc.part.rels.values():
                # Each relationship has a reltype (relationship type). If it contains "hyperlink", this relationship points to an external URL.
                if 'hyperlink' in rel.reltype.lower():
                    url = rel._target

                    if isinstance(url, str) and url.startswith('http'):
                        text += '\n' + url
        except Exception:
            pass

        log_info(f'Extracted {len(text)} chars from DOCX', context='resume_parser')
        logger.info('DOCX extraction succeeded; total chars=%d', len(text))

        return text.strip()
    
    # Catch cases where a FileParsingError was already raised earlier
    # Re-raise it unchanged to preserve the original error message and context
    except FileParsingError:
        raise    # Re-raise unchanged — don't wrap in another FileParsingError

    # Catch any other unexpected exceptions (e.g., ValueError, OSError, KeyError)
    except Exception as e:
        log_error(e, context='extract_text_from_docx')

        # Wrap the unexpected error in a custom FileParsingError
        raise FileParsingError(
            'Failed to extract text from DOCX. '
            'The document may be corrupted or in an unsupported format. '
            'Please try re-saving or converting to PDF.'
        ) from e
    


def extract_text_from_doc(file_data: bytes) -> str:
    raise FileParsingError(
        'Legacy .doc format is not supported. '
        'Please convert your document to .docx or .pdf and try again. '
        'You can convert using Microsoft Word, Google Docs, or online tools.'
    )



# So this fn will acts as the orchestrator for all the specialized parsing functions & controls all these functions
def extract_text(file_data: bytes, file_type: str) -> str:
    logger.info('Extracting text for file_type=%s', file_type)
    if file_type=='pdf':
        return extract_text_from_pdf(file_data)
    elif file_type=='docx':
        return extract_text_from_docx(file_data)
    elif file_type=='doc':
        return extract_text_from_doc(file_data)
    else:
        logger.error('Unsupported file type requested: %s', file_type)
        raise FileValidationError(
            f'Invalid file type: {file_type}. Supported types are: pdf, docx and doc'
        )



# This fn is defining the main entry point for handling uploaded resume files.
# This function returns a tuple with two parts:  str → The extracted text content of the resume. And dict → Metadata or structured information about the file.
# This dict Could include fields like:
# "filename" → original file name.
# "filetype" → detected type (pdf, docx).
# "pages" → number of pages (for PDFs).
# "extraction_method" → which parser was used (pdfplumber, PyPDF2, python-docx)
def parse_resume_file(file_data: bytes, filename: str) -> Tuple[str, dict]:
    logger.info('Starting parse_resume_file for %s', filename)
    log_info(f'Parsing file: {filename}', context='parse_resume_file')

    # Phase 1 : validate file :-
    try:
        is_valid, error_msg, file_type = validate_file(file_data, filename)

        if not is_valid:
            log_warning(f'Validation failed for file {filename}: {error_msg}', context='parse_resume_file')

            raise FileValidationError(error_msg)

        log_info(f'File validated as {file_type} for {filename}', context='parse_resume_file')
    
    except FileValidationError as e:
        raise 

    except Exception as e:
        log_error(e, context='parse_resume_file_validation')

        raise FileValidationError(
            'Could not validate the uploaded file. Please ensure it is a valid PDF or DOCX.'
        ) from e
    

    # Phase 2 : extraction of file :-
    try:
        log_info(f'Starting text extraction for {filename} using type {file_type}', context='parse_resume_file')
        text = extract_text(file_data, file_type)

        log_info(f'Extracted {len(text)} chars from {filename}', context='parse_resume_file')

    except FileParsingError:
        log_warning(f'File parsing failed for {filename}', context='parse_resume_file')
        raise   # Re-raise unchanged

    except Exception as e:
        log_error(e, context='parse_resume_file_extraction')

        raise FileParsingError(
            'An unexpected error occurred while processing the file. '
            'Please try again or contact support if the problem persists.'
        ) from e
    
    metadata = {
        'filename': filename,
        'file_type': file_type,
        'file_size_bytes': len(file_data),
        'text_length': len(text),
        'success': True,
    }

    logger.info('Finished parse_resume_file for %s file_type=%s text_length=%d', filename, file_type, len(text))
    return text, metadata
       


# How raise error handled if there is not except block :-
# If no code handles the error at any level which is raise, Python eventually stops the program and prints a traceback showing:
# The type of exception (e.g., FileParsingError).
# The error message you passed.
# The call stack (where the error originated).




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# io (built‑in Python module) :-
# Part of Python’s standard library.
# Provides tools for working with streams of data (text or binary).
# Commonly used classes/functions:
# io.StringIO → in‑memory text stream (acts like a file but stores strings).
# io.BytesIO → in‑memory binary stream (acts like a file but stores bytes).
# Useful when you want to handle data without writing to disk.


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# magic (third‑party library, usually python-magic) :-
# A wrapper around the libmagic library (used by the Unix file command).
# Its job: detect the type of a file based on its content, not just its extension.
# Helps validate uploaded files (e.g., ensuring a .pdf really is a PDF).

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Why they’re used together in our ATS project :-
# io → handles in‑memory streams (like resumes uploaded via web forms).
# magic → inspects those streams or files to determine their type (PDF, DOCX, etc.).
# Together, they let you:
# Accept a resume upload.
# Store it temporarily in memory (io.BytesIO).
# Verify its format using magic.
# Pass it safely to your parsing libraries (pdfplumber, python-docx, etc.).

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


