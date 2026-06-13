# Here inside this api folder, we will create this routes.py file to define the API endpoints for our project.
# API endpoints are the points of entry or access to a resource or service. They are the URLs that we will use to access the resources or services provided by our API.


# Python’s built-in logging framework for tracking events, errors, and debug information.
# Key uses:
# Helps you record messages at different severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
# Useful for debugging and monitoring applications without using print() everywhere.
import logging
from time import perf_counter

# here we are importing this Dict, Optional from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import List, Optional

# Here we are importing several FastAPI components that are commonly used when building API endpoints.
# APIRouter :- Lets you organize your API into modular route groups. Useful for splitting endpoints by feature (e.g., users, auth, resume).
# e.g router = APIRouter(prefix="/resume", tags=["resume"])
# Depends :- FastAPI’s dependency injection system.
# Allows you to declare functions or classes that should run before your endpoint logic (e.g., authentication, database session).
# File :- Used to declare that an endpoint expects a file upload.
# Works with UploadFile to handle file inputs.
# Form :- Used to declare form-data fields in requests (like HTML form submissions).
# HTTPException :- Lets you raise HTTP errors with status codes and messages.
# Request :- Gives access to the raw incoming request object. Useful for headers, cookies, client info, etc.
# UploadFile :- A special class for handling uploaded files efficiently.
# Unlike File(bytes), it doesn’t load the entire file into memory — it streams it.
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from backend.api.auth import get_current_user

from backend.models.schemas import AnalysisResponse, ComponentScores, JDComparison, SkillValidationDetails

from backend.utils.file_utils import (
    get_default_grammar_results,
    get_default_location_results,
    get_default_skill_validation_results,
)


# Here we are defining the name  of our logger as 'ats_resume_scorer', so that we can easily identify the logs related to our application in the log files. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the logs. We will use this logger to log the errors and other important information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application.
logger = logging.getLogger('ats_resume_scorer')


# It is setting up a FastAPI router with some configuration.
# APIRouter :- A FastAPI class that lets you group related endpoints together.
# It’s like creating a mini‑application inside your main FastAPI app, useful for modular design.
router = APIRouter(prefix='/api/v1', tags=['Analysis'])
# prefix='/api/v1' :- Every route registered under this router will automatically start with /api/v1.
# Example: if you define @router.get("/score"), the actual endpoint becomes /api/v1/score. This is a common way to version APIs (v1, v2, etc.).
# tags=['Analysis'] :- Tags are metadata labels for endpoints.
# They show up in the OpenAPI docs (Swagger UI) to group endpoints visually.
# Here, all routes in this router will be grouped under the “Analysis” section in the docs.



# This function is a text cleaner that strips certain emoji prefixes and trims whitespace:
def _clean(text: str) -> str:
    for prefix in ('✅', '🌟', '❌', '⚠️', '📝', '🔴', '🟡', '🟢', '🟠', '👍'):
        # Iterates over a tuple of emoji symbols commonly used as markers (checkmarks, stars, warnings, traffic-light colors, thumbs up).
        # For each emoji, it calls text.lstrip(prefix):
        # lstrip() removes the given prefix only if it appears at the start of the string.
        # Example: "✅ Passed" → " Passed".
        text = text.lstrip(prefix)

    return text.strip()




# Here we are defining the FastAPI endpoint for analyzing resume.
# Here we are using this decorator.
# Registers a POST endpoint at /api/v1/analyze-resume (since the router has prefix /api/v1).
# response_model=AnalysisResponse → FastAPI will validate and serialize the response into the AnalysisResponse schema (likely a Pydantic model).
# async def analyze_resume(...): :- Declares an asynchronous endpoint function.
# Async allows non-blocking operations (e.g., file I/O, database queries, ML model inference).
# request: Request :- Gives access to the raw HTTP request object (headers, client info, etc.).
#  resume: UploadFile = File(..., description='Resume file — PDF or DOCX, max 5 MB') :- Expects a file upload (resume).
# UploadFile streams the file efficiently (better than loading into memory).
# File(...) marks it as required.
# Description helps auto-generated docs (Swagger UI).
# job_description: str = Form('', description='Job description text (optional)') :- Accepts an optional text field from form-data.
# Form('') marks it as optional.
# Defaults to an empty string if not provided. Useful for comparing the resume against a job description.
# user_id: str = Depends(get_current_user) :- Uses FastAPI’s dependency injection (Depends).
# Calls get_current_user (likely an authentication function) to retrieve the current user’s ID.
# Ensures only authenticated users can analyze resumes.
@router.post('/analyze-resume', response_model=AnalysisResponse)
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(..., description='Resume file — PDF or DOCX, max 5 MB'),
    job_description: str = Form('', description='Job description text (optional)'),
    user_id: str = Depends(get_current_user),
):
    request_started = perf_counter()
    
    # Initializes an empty list of strings called warnings.
    # This will likely be used to collect cautionary messages during resume analysis (e.g., “File too large”, “Missing job description”, “Low keyword match”).
    warnings: List[str] = []


    # request.app.state :- In FastAPI, app.state is a place to store global objects that should be accessible across requests.
    # You can attach things like database connections, ML models, or configuration objects to app.state when the app starts.
    # nlp = request.app.state.nlp :- Retrieves the NLP pipeline (probably a spaCy model or similar) from the app’s global state.
    # This allows you to run text processing (tokenization, named entity recognition, etc.) on resumes or job descriptions without reloading the model for every request
    nlp  = request.app.state.nlp
    embedder = request.app.state.embedder


    try:
        # resume is an UploadFile object from FastAPI. .read() asynchronously reads the entire file into memory as raw bytes.
        # file_bytes now contains the binary content of the uploaded resume (PDF or DOCX).
        file_bytes = await resume.read()
        filename = resume.filename or 'resume'    # Retrieves the original filename from the upload. If no filename is provided, defaults to "resume".

        from backend.services.resume_parser import (
            FileParsingError,
            FileValidationError,
            parse_resume_file,
        )

        parse_started = perf_counter()
        resume_text, _metadata = parse_resume_file(file_bytes, filename)
        
        logger.info(f"Parsed '{filename}': {len(resume_text)} chars extracted")
        logger.info("Resume parsing finished in %.2fs", perf_counter() - parse_started)

    except Exception as exc:
        # Records the error in your application logs with severity ERROR.
        # This helps developers/admins see what went wrong (e.g., “File parsing failed: PDF is corrupted”).
        logger.error(f'File parsing failed: {exc}')

        # Converts the Python exception into a proper HTTP response for the client.
        # status_code=422 → “Unprocessable Entity” (used when the server understands the request but cannot process the content).
        # detail → human-readable explanation sent back to the client (e.g., “Could not read or parse the resume: PDF is encrypted”).
        raise HTTPException(
            status_code=422,
            detail=f'Could not read or parse the resume: {exc}',
        )


    # Full Analysis Pipeline :- 
    try:
        from backend.services.resume_analyzer import analyze_full_resume
        
        analysis_started = perf_counter()
        result = analyze_full_resume(
            resume_text=resume_text,
            nlp=nlp,
            embedder=embedder,
            job_description=job_description
        )
        logger.info("Full analysis finished in %.2fs", perf_counter() - analysis_started)
    except Exception as exc:
        logger.error(f'Full analysis pipeline failed: {exc}')

        raise HTTPException(status_code=500, detail=f'Analysis pipeline failed: {exc}')


    from backend.models.schemas import ComponentScores

    # Extract jd_comparison details
    jd_comparison_result = None

    if result.get('jd_comparison'):
        jd_comparison_result = JDComparison(
            match_percentage = round(float(result['jd_comparison'].get('match_percentage', 0.0)), 1),
            semantic_similarity = round(float(result['jd_comparison'].get('semantic_similarity', 0.0)), 3),
            matched_keywords = result['jd_comparison'].get('matched_keywords', [])[:20],
            missing_keywords = result['jd_comparison'].get('missing_keywords', [])[:15],
            skills_gap = result['jd_comparison'].get('skills_gap', [])[:10],
        )

    # Convert detailed_feedback objects from prediction into what schema expects
    detailed_fb = result.get('detailed_feedback', [])
    
    svd_raw = result.get('skill_validation_details') or {}

    skill_val_details = SkillValidationDetails(
        validated  = svd_raw.get('validated', []),
        unvalidated = svd_raw.get('unvalidated', []),
        total = svd_raw.get('total', 0),
        validated_count = svd_raw.get('validated_count', 0),
        validation_pct  = svd_raw.get('validation_pct', 0.0),
    )

    response = AnalysisResponse(
        ATS_score = result['ats_score'],
        # ComponentScores is a Pydantic model (defined earlier in your project).
        # The ** operator unpacks the dictionary into keyword arguments.
        component_scores = ComponentScores(**result['component_scores']),
        issues_summary = result['issues_summary'],
        detailed_feedback = detailed_fb,
        jd_match_analysis = jd_comparison_result,
        skill_validation_details = skill_val_details,

        # Retro-compatibility fields
        ats_score = result['ats_score'],
        keyword_match = jd_comparison_result.match_percentage if jd_comparison_result else 0.0,
        missing_keywords = result.get('missing_keywords', []),
        matched_keywords = result.get('matched_keywords', []),
        skills = list(result.get('skills', [])[:20]),
        jd_comparison = jd_comparison_result,
        interpretation = result.get('interpretation', '')
    )


    try:
        from backend.database.supabase_db import save_analysis

        save_started = perf_counter()
        await save_analysis(user_id, filename, result)
        logger.info("History save finished in %.2fs", perf_counter() - save_started)
    except Exception as exc:
        logger.warning(f'History save failed (non-blocking): {exc}')

    logger.info("Analyze resume request finished in %.2fs", perf_counter() - request_started)

    return response




# This defines a health check endpoint in FastAPI that confirms whether your API is ready to serve requests:
# It Accepts the Request object, giving access to the app’s state.
@router.get('/health')
async def health_check(request: Request):
    # Docstring (""" ... """) :- Placed inside a function, class, or module.
    # Describes what the function/class/module does. Accessible at runtime via .__doc__ (e.g., health_check.__doc__).
    # Used by tools like FastAPI, Sphinx, or IDEs to generate documentation.
    """Health check — confirms models are loaded and the API is ready."""
    
    return {
        'status': 'healthy',
        'nlp_loaded':  request.app.state.nlp is not None,     #  Checks if the NLP model (stored in app.state.nlp) is loaded.
        'embedder_loaded': request.app.state.embedder is not None,
    }




# This defines a FastAPI endpoint that returns a user’s past resume analyses from the database, with error handling built in.
# Declares an asynchronous function (non-blocking).
# user_id: str = Depends(get_current_user): Uses FastAPI’s dependency injection.
# Calls get_current_user (likely a JWT authentication helper).
# Extracts the user’s identity from the token and passes it into the function.
@router.get('/history')
async def get_history(user_id: str = Depends(get_current_user)):
    """Return the signed-in user's past analyses (identity comes from the JWT)."""
    
    from backend.database.supabase_db import get_user_history
    
    try:
        return await get_user_history(user_id)
    except Exception as exc:
        logger.error(f'History fetch failed: {exc}')

        raise HTTPException(status_code=500, detail=f'Could not load history: {exc}')




# This defines a FastAPI endpoint that lets a signed‑in user delete one of their past resume analyses from the database
# Registers a DELETE endpoint at /api/v1/history/{analysis_id}.
# {analysis_id} is a path parameter representing the ID of the analysis record to delete.
# analysis_id: str → The ID of the analysis to delete, taken from the URL.
# user_id: str = Depends(get_current_user) → Uses FastAPI’s dependency injection to fetch the current user’s ID from the JWT (authentication).
@router.delete('/history/{analysis_id}')
async def delete_history_entry(
    analysis_id: str,
    user_id: str = Depends(get_current_user),
):
    
    """Delete one analysis from the signed-in user's history."""
    
    from backend.database.supabase_db import delete_analysis
    
    try:
        success = await delete_analysis(analysis_id, user_id)

        if not success:
            raise HTTPException(status_code=404, detail='Analysis not found or not owned by this user.')
        
        return {'status': 'deleted', 'id': analysis_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f'History delete failed: {exc}')
        
        raise HTTPException(status_code=500, detail=f'Could not delete: {exc}')
    



# This defines a FastAPI endpoint that generates a PDF report from an analysis result and returns it as a downloadable file
# data: AnalysisResponse → The request body must match the AnalysisResponse Pydantic model (structured resume analysis results).
# user_id: str = Depends(get_current_user) → Injects the authenticated user’s ID via JWT.
@router.post('/generate-pdf')
async def generate_pdf(
    data: AnalysisResponse,
    user_id: str = Depends(get_current_user),
):
    
    from backend.services.report_generator import generate_html_reports
    from backend.services.pdf_export import generate_combined_pdf

    # Response: FastAPI’s raw response class, used to return binary content.
    from fastapi.responses import Response

    try:
        # data.model_dump() → Converts the Pydantic model into a plain dictionary.
        html_docs = generate_html_reports(data.model_dump())
        pdf_bytes = generate_combined_pdf(html_docs)

        # Returns the PDF as a binary response.
        # media_type="application/pdf" → Tells the client it’s a PDF file.
        # Content-Disposition: attachment; filename=ats_report.pdf → Forces download with the given filename.
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=ats_report.pdf"
            }
        )
    except Exception as e:
        logger.error(f'Failed to generate PDF: {e}')
        
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")
    



# This defines a FastAPI endpoint that lets a signed‑in user download a PDF version of one of their past resume analyses
# analysis_id: str → The ID of the analysis to export.
# user_id: str = Depends(get_current_user) → Injects the authenticated user’s ID from JWT.
@router.get('/history/{analysis_id}/pdf')
async def generate_history_pdf(
    analysis_id: str,
    user_id: str = Depends(get_current_user),
):
    
    from backend.database.supabase_db import get_user_history
    from backend.services.report_generator import generate_html_reports
    from backend.services.pdf_export import generate_combined_pdf
    from fastapi.responses import Response

    history = await get_user_history(user_id)
    
    # Iterates through the user’s history. Finds the record whose id matches analysis_id.
    # Extracts its analysis_result (the structured analysis data).
    # If not found, sets analysis_data = None.
    analysis_data = next((item["analysis_result"] for item in history if item["id"] == analysis_id), None)
    # next(...) :- Takes the first value produced by the generator. If no match is found, returns the default (None).
    # next() Stops searching as soon as the first match is found (no need to scan the whole list).

    if not analysis_data:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        html_docs = generate_html_reports(analysis_data)
        pdf_bytes = generate_combined_pdf(html_docs)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=ats_report_{analysis_id}.pdf"
            }
        )
    except Exception as e:
        logger.error(f'Failed to generate PDF for history: {e}')
        
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")


