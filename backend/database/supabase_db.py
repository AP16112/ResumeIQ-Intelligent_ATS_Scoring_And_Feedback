# here inside this database folder, we will create this supabase_db.py file to write the code to connect our FastAPI backend with Supabase database (i.e memory for our project).
# In this we will write all of our database related logic for our project.
# This file will contain the code to perform CRUD operations on the database. This way we can keep our code organized and modular.

# In this file, we will write all the queries required to call the database and to interact with the database in our project, so that we can keep all the database related code in one file and can easily import this file wherever we want to interact with the database in our project, so that we can keep our code clean and organized.

import logging   # it is used for logging the errors and other information in our application. It helps us to keep track of the errors and other important information in our application. We can use it to log the errors, warnings, and other information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application. We will write all the logging related code in this file only, so that we can keep our code organized and modular.

# here we are importing httpx and not request because:-
# requests :- Synchronous HTTP client (blocking). Simple, widely used for quick API calls.
# The program waits until the request finishes before moving on.
# httpx :- Modern HTTP client that supports both sync and async usage.
# Built to integrate with Python’s asyncio, so you can make multiple requests concurrently without blocking.
# Much faster when you need to handle many API calls (like Supabase queries or Groq LLM requests) because it doesn’t block the event loop.
import httpx
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict
# here we are importing these List, Dict, Optional from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.


# Here we are defining the name  of our logger as 'ats_resume_scorer', so that we can easily identify the logs related to our application in the log files. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the logs. We will use this logger to log the errors and other important information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application.
logger = logging.getLogger('ats_resume_scorer')

from backend.core.config import SUPABASE_URL, SUPABASE_KEY


# In Python, putting an underscore (_) at the front of a function name (like _get_headers) is a naming convention that signals: Private / internal use
# It tells other developers: “This function is meant for internal use inside this module/class, not part of the public API.”
# Python doesn’t enforce strict privacy (like private in Java or C++), but the underscore is a strong hint.
# public_api_call() is the function you expect other modules or users to call.
# If someone imports your module with from mymodule import *, _get_headers will not be imported automatically because of the underscore.

# This helper function _get_headers() builds the HTTP request headers needed to talk to Supabase’s REST API.
def _get_headers():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    
    return {
        "apikey": SUPABASE_KEY,     # Supabase requires the API key in the header for authentication.
        "Authorization": f"Bearer {SUPABASE_KEY}",   # Standard bearer token format. Supabase accepts either apikey or Authorization, so both are included for compatibility.
        "Content-Type": "application/json",   # Ensures the request body is treated as JSON.
        "Prefer": "return=representation"
        # Tells Supabase to return the full row(s) after an insert/update, not just a success status.
        # Example: when you insert a resume record, Supabase will return the inserted row with its ID.
    }



# This function save_analysis is an async helper that takes a user’s resume analysis result and saves it into Supabase via its REST API
# here it is a async function because we don't want that when user data is being saved, at that our app must not stuck there only, and it must perform other operations
# so due to which we make this async, so that this saving operations will happening in the background & at the same time, other operations will also performed.
# Return type: Optional[str]  --> Means the function will return either:
# A str → the ID of the newly inserted record in Supabase (success case).
# None → if saving fails (missing headers, error response, exception).
async def save_analysis(user_id: str, filename: str, analysis_result: Dict) -> Optional[str]:
    headers = _get_headers()  # Calls _get_headers() to build Supabase authentication headers.

    if not headers:
        return None
    

    # Ensures complex objects (like Pydantic models) can be converted to JSON. 
    # Falls back to str(o) if no model_dump method exists.
    # That helper function _json_default(o) is designed to make non‑standard Python objects JSON‑serializable when you call json.dumps.
    def _json_default(o):
        if hasattr(o, 'model_dump'):
            return o.model_dump()
        # Many modern libraries (like Pydantic v2) provide a .model_dump() method that converts a model into a plain Python dict. If the object supports this, _json_default calls it, returning a JSON‑friendly dict.

        return str(o)  # If the object doesn’t have model_dump, it falls back to converting it into a string. This ensures something is returned, even if it’s not structured data.
    
    # Why this _json_default fn needed :-
    # The built‑in json.dumps() can only handle basic types: dicts, lists, strings, numbers, booleans, and None.
    # If you pass in a custom object (like a Pydantic model, datetime, or other class instance), json.dumps will raise a TypeError.
    # To fix this, you can provide a default function that tells json.dumps how to convert unknown objects into something serializable. _json_default is exactly that.
    

    # THis json.dumps() convert analysis_result (which may contain complex objects like Pydantic models, datetimes, or custom classes) into a JSON string.
    # If json.dumps encounters an object it doesn’t know how to serialize, it calls _json_default(o).
    serializable_result = json.loads(json.dumps(analysis_result, default=_json_default))
    # This json.loads(...) takes the JSON string produced by json.dumps() and converts it back into a plain Python dict/list structure.
    # Why? Because Supabase expects a native JSON object (dict) in the request body, not a string.


    # That doc dictionary is the payload you’re preparing to send to Supabase’s REST API. It represents one record of a resume analysis. 
    doc = {
        "user_id": user_id,    # Identifies which user this analysis belongs to.
        "filename": filename,
        "ats_score": serializable_result.get("ats_score", 0),    # Pulls the ATS score from the analysis result. Defaults to 0 if missing. 
        "keyword_match": serializable_result.get("keyword_match", 0),
        "missing_keywords": serializable_result.get("missing_keywords", []),
        "created_at": datetime.now(timezone.utc).isoformat(),    # Timestamp (in UTC, ISO 8601 format) marking when the analysis was saved. Ensures records are time‑stamped consistently. e.g "2026-06-09T13:22:45+00:00"
        "analysis_result": serializable_result,
    }


    # Builds the REST endpoint for the analysis table in Supabase.
    # rstrip('/') ensures no duplicate slashes if SUPABASE_URL already ends with /.
    # Final URL looks like :-  https://<project>.supabase.co/rest/v1/analysis
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1.analysis"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=doc)
            # Uses httpx.AsyncClient for non‑blocking HTTP calls. Sends a POST request to Supabase with:
            # headers → authentication (apikey, Authorization, etc.).
            # json=doc → the payload (resume analysis record).
            
            response.raise_for_status() # If Supabase returns an error status (4xx or 5xx), this raises an exception immediately. Prevents silently continuing with bad data.
            data = response.json()
            # Supabase returns the inserted row(s) as JSON (because of "Prefer": "return=representation" in headers).

            if data and len(data) > 0:   # Checks if Supabase returned at least one row.
                inserted_id = str(data[0].get("id"))   # Pulls out the id of the newly inserted record.
                logger.info(f"Saved analysis for user {user_id}: {inserted_id}")   # Logs a success message.

                return inserted_id      # Returns the ID so the caller knows which record was saved.
            
            return None
    except Exception as exc:
        logger.error(f"Failed to save analysis to Supabase: {exc}")

        return None
    


# Here we are defining an asynchronous function that will fetch all past analysis records for a given user from Supabase.
async def get_user_history(user_id: str) -> List[Dict]:
    headers = _get_headers()

    if not headers:
        return []
    
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"

    try: 
        async with httpx.AsyncClient() as client:
            # await :- Used inside an async function to pause execution until the awaited task finishes. While waiting, Python can switch to other tasks (like handling another user’s request).
            # Once the awaited task completes, execution resumes right after the await.
            response = await client.get(     #             Sends a GET request to Supabase REST API.
                url,
                headers=headers,
                params={
                    # Supabase’s REST API uses PostgREST syntax for query parameters:
                    # field=eq.value → filters rows where field equals value. Other operators exist too: lt (less than), gt (greater than), like, etc.
                    "user_id": f"eq.{user_id}",       # filters rows where user_id equals the given user.
                    "order": "created_at.desc"        # sorts results by created_at in descending order (most recent first).
                }
            )


            response.raise_for_status()
            docs = response.json()    # Supabase returns a list of rows (each row is a dict).

            results = []

            for doc in docs:
                results.append({
                    "id": str(doc.get("id")),
                    "filename": doc.get("filename", "resume"),    # defaults to "resume".
                    "resume_name": doc.get("filename", "resume"),
                    "job_title": "Software Engineer",
                    "ats_score": doc.get("ats_score", 0),
                    "keyword_match": doc.get("keyword_match", 0),
                    "missing_keywords": doc.get("missing_keywords", []),
                    "date": doc.get("created_at", ""),
                    "created_at": doc.get("created_at", ""),
                    "analysis_result": doc.get("analysis_result", {}),
                })
            # Iterates through each row (doc) and builds a normalized dictionary. Ensures defaults if fields are missing:

            return results
    except Exception as exc:
        logger.error(f"Failed to fetch history from Supabase: {exc}")
        return []
    


# asynchronous function that will delete a specific resume analysis record from Supabase.
# analysis_id: str → The unique ID of the analysis record you want to delete. 
# user_id: str → The ID of the user who owns that record (used for safety checks).
# Return type: bool → Returns True if deletion succeeds, False if it fails.
async def delete_analysis(analysis_id: str, user_id: str) -> bool:
    headers = _get_headers()

    if not headers:
        return False

    # Builds the REST endpoint for the analyses table in Supabase.
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analyses"

    try: 
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params={
                    "id": f"eq.{analysis_id}",
                    "user_id": f"eq.{user_id}"
                }
            )

            response.raise_for_status()
            return True
    except Exception as exc:
        logger.error(f"Failed to delete analysis {analysis_id}: {exc}")
        return False
    





# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Supabase :-
# We will use this as database here.
# Supabase is an open‑source backend platform built on PostgreSQL that provides developers with a ready‑to‑use database, authentication, APIs, storage, and real‑time features — essentially a Firebase alternative but powered by Postgres. 
# It’s designed to let you spin up a backend in minutes and scale to millions of users without managing servers.

# Supabase itself is not a database but it provides the instance of p sql i.e (PostgreSQL) database to the developers, so that they can use that database for their projects without worrying about the backend part of it. It also provides some other features like authentication, APIs, storage, real-time features, etc which are required in the backend of any project, so that developers can focus on the frontend part of their project and can easily integrate this supabase with their frontend without worrying about the backend part of it.
# PostgreSQL and MySQL are almost same but PostgreSQL is more advanced and has more features than MySQL, so it is more preferred by developers. Supabase provides the instance of PostgreSQL database to the developers, so that they can use that database for their projects without worrying about the backend part of it. It also provides some other features like authentication, APIs, storage, real-time features, etc which are required in the backend of any project, so that developers can focus on the frontend part of their project and can easily integrate this supabase with their frontend without worrying about the backend part of it.


# Core Features of Supabase :-
# Postgres Database  :- Every project comes with a full PostgreSQL instance, one of the most trusted relational databases.
# Authentication  :- Built‑in user sign‑ups and logins with support for email, OAuth, and Row Level Security (RLS).
# Instant APIs  :- Auto‑generated REST and GraphQL APIs for your database tables.
# Realtime Subscriptions  :- Enables live data sync for apps like chat, dashboards, or multiplayer games.
# Edge Functions  :- Serverless functions you can deploy without managing infrastructure.
# Storage  :- Manage and serve large files (images, videos, documents).
# Vector Embeddings  :- Store and query ML embeddings for AI applications (integrates with OpenAI, Hugging Face, LangChain).


# JSONB format in PostgreSQL :-
# JSONB is a data type in PostgreSQL that allows you to store JSON (JavaScript Object Notation) data in a binary format. It provides efficient storage and querying capabilities for JSON data, making it ideal for applications that need to handle semi-structured or unstructured data. With JSONB, you can easily store and manipulate complex data structures without needing to define a rigid schema, while still benefiting from indexing and fast access.
# JSONB is a PostgreSQL data type that stores JSON (JavaScript Object Notation) data in a binary format rather than plain text.


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# httpx :-
# Modern async HTTP client for Python.
# Used to make REST API calls efficiently (non‑blocking).
# In your case: acts as the Supabase REST client, letting you query Supabase tables, auth, and storage asynchronously.


