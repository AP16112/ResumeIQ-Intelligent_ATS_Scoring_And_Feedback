# Here in this services, we will actually write the logic or code which is used to connect the backend part with the frontend actually
# This file is setting up a frontend service layer that connects your Streamlit app to a FastAPI backend over HTTP
# It acts as a service layer: the frontend (Streamlit) doesn’t directly import backend code.
# Instead, it communicates with the backend via HTTP requests.
# Each function here will be a “thin wrapper” around one FastAPI endpoint (e.g., /auth/login, /resume/score).

# This file will acts as HTTP client for the FastAPI backend

# Every function here is a thin wrapper around one backend endpoint.
# The frontend never imports backend modules - it only talks to the backend over HTTP through this file.

# Authenticated endpoints expect a Supabase access token;
# callers pass it as 'access_token=' and we forward it as 'Authorization: Bearer <token>' .


from typing import Any, Dict, List

import requests

import streamlit as st


# If no custom backend URL is configured, the app assumes the backend is running locally on port 8000.
DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


# Accessing Dynamic backend URL :-
def _backend_url() -> str:
    try:
        # Tries to read the backend URL from st.secrets (Streamlit’s secure config). If not found, falls back to the default (http://localhost:8000).
        # This makes deployment flexible: Local dev → localhost:8000 And Production → a real API URL stored in secrets.toml.
        return st.secrets["backend"]["url"]
    except (KeyError, FileNotFoundError):
        return DEFAULT_BACKEND_URL
    
# st.secrets :- Streamlit provides a special dictionary called st.secrets for storing sensitive values (like API keys, database URLs, or backend endpoints).
# These values are defined in a file called secrets.toml (or in Streamlit Cloud’s Secrets Manager).
# Example secrets.toml:
# [backend]
# url = "https://resumeiq-api.example.com"
# st.secrets["backend"] → retrieves the whole backend section (a dictionary).
# st.secrets["backend"]["url"] → retrieves the specific key url inside that section.



# This function builds the Authorization header for authenticated HTTP requests
def _auth_headers(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}

# Why “Bearer”? :-
# In HTTP authentication, a Bearer token is a standard way to pass access tokens.
# The word “Bearer” tells the server: “This request is authorized using the following token.”
# Supabase (and most modern APIs) expect this format in the header.

# How it’s used :-
# When making requests with requests, you pass this dictionary as headers:
# headers = _auth_headers(access_token)
# response = requests.get(f"{_backend_url()}/resume/score", headers=headers)
# The backend checks the token, verifies it, and allows or denies access.



# This function is a health check client — it lets your Streamlit frontend call the FastAPI backend’s /api/v1/health endpoint and return its status
# Returns a dictionary (Dict[str, Any]) — the parsed JSON response from the backend.
def health_check() -> Dict[str, Any]:
    # Calls the backend’s health endpoint. _backend_url() resolves to either your configured API URL (from st.secrets) or the default http://localhost:8000.
    # Appends /api/v1/health to form the full URL.
    # timeout=10 ensures the request fails if the backend doesn’t respond within 10 seconds (avoids hanging).
    response = requests.get(f"{_backend_url()}/api/v1/health", timeout=10)
    
    # Raises an exception if the HTTP status code is not 200 (i.e ok) (e.g., 404, 500).
    # This prevents silently returning bad responses and makes debugging easier.
    response.raise_for_status()
    
    # Converts the backend’s JSON response into a Python dictionary.
    return response.json()




# This function is the frontend wrapper for our backend’s resume analysis endpoint. It uploads a resume file, optionally includes a job description, and returns the backend’s JSON analysis
# resume_file: the uploaded file object from Streamlit (st.file_uploader).
# access_token: Supabase access token for authentication.
# job_description: optional string, defaults to empty.
# Returns: a dictionary (Dict[str, Any]) containing the backend’s JSON response.
def analyze_resume(resume_file, access_token: str, job_description: str = "") -> Dict[str, Any]:
    # Builds a multipart upload for the resume.
    # Includes:
    # resume_file.name → original filename.
    # resume_file.getvalue() → raw file bytes.
    # resume_file.type → MIME type (e.g., "application/pdf").
    files = {
        "resume": (resume_file.name, resume_file.getvalue(), resume_file.type),
    }

    data = {"job_description": job_description}


    # Calls the backend endpoint /api/v1/analyze-resume.
    # files=files → sends the resume file.
    # data=data → sends the job description.
    # headers=_auth_headers(access_token) → adds Authorization: Bearer <token>.
    # timeout=240 → allows up to 4 minutes (useful for heavy NLP/ML processing)
    response = requests.post(
        f"{_backend_url()}/api/v1/analyze-resume",
        files=files,
        data=data,
        headers=_auth_headers(access_token),
        timeout=240,
    )

    response.raise_for_status()

    return response.json()




# This function is a frontend helper that retrieves a user’s past resume analyses (history) from the backend
def get_history(access_token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{_backend_url()}/api/v1/history",
        headers=_auth_headers(access_token),
        timeout=30,    # ensures the request fails if the backend doesn’t respond within 30 seconds.
    )

    response.raise_for_status()

    # Converts the backend’s JSON response into Python objects.
    # Typically, this will be a list of history entries.
    return response.json()

# json
# [
#   {
#     "analysis_id": "abc123",
#     "resume_name": "Arpit_Resume.pdf",
#     "job_title": "Data Scientist",
#     "ats_score": 82,
#     "created_at": "2026-06-10T14:32:00"
#   },
#   {
#     "analysis_id": "def456",
#     "resume_name": "Arpit_Resume_v2.pdf",
#     "job_title": "Software Engineer",
#     "ats_score": 90,
#     "created_at": "2026-06-11T09:15:00"
#   }
# ]




# This function is the frontend helper for deleting a specific resume analysis record from the backend
def delete_history_entry(analysis_id: str, access_token: str) -> None:
    response = requests.delete(
        f"{_backend_url()}/api/v1/history/{analysis_id}",
        headers=_auth_headers(access_token),
        timeout=30,
    )

    response.raise_for_status()



# This function is the frontend helper for generating a PDF report from resume analysis data via the backend
# Returns: raw PDF bytes (bytes), which can be saved or streamed to the user.
def generate_pdf(analysis_data: Dict[str, Any], access_token: str) -> bytes:
    response = requests.post(
        f"{_backend_url()}/api/v1/generate-pdf",
        json=analysis_data,    # Sends analysis_data as JSON in the request body.
        headers=_auth_headers(access_token),
        timeout=60,
    )

    response.raise_for_status()

    # Returns the raw binary content of the PDF file. Unlike .json(), .content is used because the backend sends a PDF file, not JSON.
    # The frontend can then:
    # Save it to disk.
    # Stream it to the user as a download.
    # Attach it to an email.
    return response.content




def get_history_pdf(analysis_id: str, access_token: str) -> bytes:
    response = requests.get(
        f"{_backend_url()}/api/v1/history/{analysis_id}/pdf",
        headers=_auth_headers(access_token),
        timeout=60,
    )

    response.raise_for_status()

    return response.content
