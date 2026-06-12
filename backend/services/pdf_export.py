# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'pdf_export.py' file to provide the user with the pdf report to improve the resume
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.


# Provides tools for working with streams of data in memory (instead of files on disk).
# Key uses:
# io.StringIO → behaves like a file but stores text in memory.
# io.BytesIO → behaves like a file but stores binary data (e.g., images, audio) in memory.
import io

# Python’s built-in logging framework for tracking events, errors, and debug information.
# Key uses:
# Helps you record messages at different severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
# Useful for debugging and monitoring applications without using print() everywhere.
import logging



# The code attempts to import HTML and CSS classes from the WeasyPrint library.
# If the library is installed, the import succeeds and WEASYPRINT_INSTALLED is set to True.
# If the library is not installed, Python raises an ImportError, and the code catches it, setting WEASYPRINT_INSTALLED = False.
# This is a graceful fallback: the program can check later whether WeasyPrint is available before trying to generate PDFs.
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_INSTALLED = True
except ImportError:
    WEASYPRINT_INSTALLED = False


# Creates (or retrieves) a named logger instance called "ats_resume_scorer".
# This logger is used to record messages (info, warnings, errors) specifically for the ATS Resume Scorer module.
# Having a named logger helps organize logs by component, instead of dumping everything into the root logger.
logger = logging.getLogger('ats_resume_scorer')




# This defines a helper function for generating a combined PDF from multiple HTML documents, but it also includes a safety check to ensure WeasyPrint is available.
def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    if not WEASYPRINT_INSTALLED:
        raise ImportError("WeasyPrint is not installed. PDF generation unavailable.")
        
    documents = []
    
    # Render all 3 HTML strings to WeasyPrint Document objects
    # HTML(string=html_str).render() converts each HTML string into a WeasyPrint Document object (not yet a PDF, but a structured representation with pages).
    # Appends each rendered document to the documents list.
    for name, html_str in html_docs.items():
        doc = HTML(string=html_str).render()
        documents.append(doc)
    
    # Merge them into the first document
    # Merge all documents into one
    first_doc = documents[0]

    for other_doc in documents[1:]:
        # For each, loops through its pages and appends them to first_doc.pages. This effectively merges all pages into one continuous document.
        for page in other_doc.pages:
            first_doc.pages.append(page)
            
    # Write combined PDF bytes
    # Calls .write_pdf() on the merged document. Produces raw PDF data (bytes) in memory.
    # Returns it, so the caller can save it to a file or send it over a network.
    pdf_bytes = first_doc.write_pdf()

    return pdf_bytes




#------------------------------------------------------------------------------------------------------------------------------------------------------------
# WeasyPrint :-
# WeasyPrint is a Python library that converts HTML and CSS into beautifully formatted PDF documents, making it ideal for generating reports, invoices, tickets, or any printable content directly from web-style layouts. It’s free, open-source, and designed to follow web standards for printing

# Key Features of WeasyPrint :-
# HTML + CSS to PDF: Renders web pages into paginated PDF files.
# Web Standards Support: Handles modern CSS features like flexbox, grid, and media queries.
# Python-based: Written entirely in Python, easy to integrate into Django, Flask, or FastAPI projects.
# No Browser Engine: Unlike wkhtmltopdf (which uses WebKit), WeasyPrint has its own CSS layout engine.
# Free & Open Source: Licensed under BSD, actively maintained by Kozea and CourtBouillon.