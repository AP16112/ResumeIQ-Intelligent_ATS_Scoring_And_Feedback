# Here in this services, we will actually write the logic or code which is used to connect the backend part with the frontend actually
# This file actually directly communicates with the supabase for auth, sign in & sign up, sign out, etc.



# import os is a Python import statement that loads the built‑in os module, which provides functions for interacting with the operating system.
# The os module is part of Python’s standard library and gives you tools to:
# Work with file paths and directories.
# Create, remove, or rename files and folders.
# Read and set environment variables.
# Run system commands.
# Get information about the operating system (like current working directory, process ID, etc.).
import os
import logging

# pathlib is a modern library for working with filesystem paths.
# Path is its main class, representing a file or directory path.
# It’s more powerful and readable than using raw strings or os.path
from pathlib import Path

from typing import Any, Dict
import streamlit as st


# Client :- This is the class definition for the Supabase client.
# It represents a connection object that knows how to talk to your Supabase project.
# Once instantiated, it exposes methods for:
# Database operations (.table("...").select(), .insert(), etc.)
# Authentication (.auth.sign_in_with_password(), .auth.sign_up(), etc.)
# Storage (upload/download files)
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Here, supabase is an instance of the Client class.
# create_client :- This is a helper function provided by the SDK.
# It takes two arguments:
# SUPABASE_URL → the unique API URL for your Supabase project.
# SUPABASE_KEY → the API key (either anon/public or service role).
# It returns a Client object that you can use throughout your app.
from supabase import Client, create_client


logger = logging.getLogger('ats_resume_scorer')


try:   # Wraps the code in a try block so that if the dotenv package isn’t installed, the program won’t crash.
    from dotenv import load_dotenv

    # Path(__file__).resolve().parents[2] / '.env' :- Uses pathlib.Path to construct the path to the .env file. 
    # __file__ → the current Python file.
    # .resolve() → gets the absolute path.
    # .parents[2] → goes two directories up from the current file’s location.
    # / '.env' → appends .env to that path.
    load_dotenv(Path(__file__).resolve().parents[2] / '.env')
    # load_dotenv(...) :- Loads the .env file found at that path.
    # Makes variables like SUPABASE_URL, SUPABASE_KEY, DATABASE_URL available via os.getenv("SUPABASE_URL").
except ImportError:
    pass




# This helper function is designed to safely fetch secrets or environment variables for our app
# key: str → the name of the secret you want (e.g., "SUPABASE_URL").
# section: str = 'supabase' → optional section name in st.secrets (defaults to "supabase").
# Returns: a string (the secret value), or an empty string if not found.
def _secret(key: str, section: str = 'supabase') -> str:
    """Read from env first, then fall back to st.secrets[section][key]."""
    
    val = os.getenv(key, '')
    
    if val:
        return val
    
    # If not found in environment variables, tries to read from st.secrets.
    # st.secrets is Streamlit’s secure configuration system (values stored in secrets.toml or Streamlit Cloud).
    try:
        return st.secrets[section][key]
    except (KeyError, FileNotFoundError, AttributeError):
        return ''



SUPABASE_URL = _secret('SUPABASE_URL')
SUPABASE_ANON_KEY = _secret('SUPABASE_ANON_KEY')


# It is defining the OAuth redirect URL for our app, with a clear priority order
OAUTH_REDIRECT_URL = (
    os.getenv('AUTH_REDIRECT_URL')   # First, it checks if an environment variable named AUTH_REDIRECT_URL is set.
    or _secret('redirect_uri', 'google_oauth')  # If the environment variable isn’t set, it falls back to your _secret helper. _secret looks inside Streamlit’s secrets.toml (or environment variables again). It specifically checks the google_oauth section for a key named redirect_uri.
    or 'http://localhost:8501'    # This is the standard local development URL for Streamlit apps.
)



# This helper function checks whether your Supabase client is properly configured, and returns a warning message if not.
def _missing_config() -> str | None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return 'Supabase is not configured — set SUPABASE_URL and SUPABASE_ANON_KEY in .env or .streamlit/secrets.toml'
    
    return None



# This function is a cached singleton initializer for your Supabase client in Streamlit
# @st.cache_resource decorator :- Streamlit reruns your script every time the user interacts with the UI.
# Without caching, the Supabase client would be recreated on every rerun.
# @st.cache_resource ensures the client is created once and reused across reruns.
# This is crucial for PKCE (Proof Key for Code Exchange) in OAuth flows, because the state must persist across reruns while the user completes login.
@st.cache_resource
def get_client() -> Client | None:
    """Cached singleton — preserves PKCE state across Streamlit reruns."""
    if _missing_config():
        return None
    
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)



# This function is a helper that converts a Supabase session + user object into a simple dictionary that your Streamlit app can store and use
# session: the Supabase session object (contains tokens).
# user: the Supabase user object (contains user info).
def _session_dict(session, user) -> Dict[str, Any]:
    return {
        # access_token → short‑lived JWT token used to authenticate API requests.
        # refresh_token → longer‑lived token used to get a new access token when it expires.
        'access_token':  session.access_token,
        'refresh_token': session.refresh_token,
        'user_id': user.id,
        'email': user.email,
    }




def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    err = _missing_config()

    if err:
        return {'error': err}
    
    try:
        # Uses the cached Supabase client (get_client()). Calls Supabase Auth’s sign_in_with_password method with the provided email and password.
        # resp contains both session (tokens) and user (profile info).
        resp = get_client().auth.sign_in_with_password(
            {'email': email, 'password': password}
        )

        if not resp.session or not resp.user:   # If login fails (wrong email/password), Supabase may return no session or user.
            return {'error': 'Invalid credentials'}
        
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.warning(f'sign_in_with_password failed: {exc}')
        return {'error': _humanize(exc)}




def sign_up_with_password(email: str, password: str) -> Dict[str, Any]:
    err = _missing_config()

    if err:
        return {'error': err}
    
    try:
        resp = get_client().auth.sign_up({'email': email, 'password': password})
        
        if resp.session and resp.user:
            # If Supabase returns both a session and user, sign‑up is complete and the user is logged in.
            # Returns a dictionary with access_token, refresh_token, user_id, and email.
            return _session_dict(resp.session, resp.user)
        
        if resp.user:
            # Supabase often requires email verification.
            # In this case, a user object exists but no session yet.
            # Returns a dictionary indicating confirmation is pending.
            return {'pending_confirmation': True, 'email': email}
        
        return {'error': 'Sign-up failed'}
    except Exception as exc:
        logger.warning(f'sign_up failed: {exc}')

        return {'error': _humanize(exc)}




# This function is the helper for generating a Google OAuth login URL via Supabase, with error handling built in
def google_oauth_url() -> Dict[str, Any]:
    err = _missing_config()

    if err:
        return {'error': err}
    
    try:
        # Calls sign_in_with_oauth with:
        # provider: 'google' → specifies Google as the OAuth provider.
        # options: {'redirect_to': OAUTH_REDIRECT_URL} → tells Google where to send the user back after login (your app’s redirect URI).
        resp = get_client().auth.sign_in_with_oauth({
            'provider': 'google',
            'options': {'redirect_to': OAUTH_REDIRECT_URL},
        })

        return {'url': resp.url}   # Supabase returns an object containing the generated login URL.
    except Exception as exc:
        logger.warning(f'oauth url generation failed: {exc}')
        return {'error': _humanize(exc)}




# This function is the final step in the Google OAuth login flow — it exchanges the temporary auth_code (sent back by Google after login) for a full Supabase session.
def exchange_code_for_session(auth_code: str) -> Dict[str, Any]:
    """Called once after the OAuth provider redirects back with `?code=...`."""
    
    err = _missing_config()
    
    if err:
        return {'error': err}
    
    client = get_client()
    
    try:
        # PKCE (Proof Key for Code Exchange) requires a code_verifier that was stored earlier when the OAuth URL was generated.
        # This retrieves it from the client’s internal storage. If not found, defaults to an empty string.
        storage_key = f'{client.auth._storage_key}-code-verifier'
        code_verifier = client.auth._storage.get_item(storage_key) or ''
        
        # Sends the auth_code (from Google redirect), the code_verifier, and the redirect URI to Supabase.
        # Supabase validates the code and returns a session + user object.
        resp = client.auth.exchange_code_for_session({
            'auth_code': auth_code,
            'code_verifier': code_verifier,
            'redirect_to': OAUTH_REDIRECT_URL,
        })
        
        if not resp.session or not resp.user:
            return {'error': 'OAuth exchange returned no session'}
        
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.warning(f'exchange_code_for_session failed: {exc}')
        return {'error': _humanize(exc)}



def sign_out() -> None:
    if _missing_config():
        return
    
    try:
        get_client().auth.sign_out()
    except Exception as exc:
        logger.warning(f'sign_out failed: {exc}')



# This helper function translates raw Supabase/SDK exceptions into user‑friendly error messages so your app can show clear feedback instead of cryptic technical strings
def _humanize(exc: Exception) -> str:
    msg = str(exc)

    # supabase errors arrive as "<status>: {json blob}" — surface the human bit
    if 'invalid_grant' in msg.lower() or 'invalid login' in msg.lower():
        return 'Wrong email or password'
    
    if 'user already registered' in msg.lower() or 'already been registered' in msg.lower():
        return 'An account with this email already exists — try signing in'
    
    if 'password should be at least' in msg.lower():
        return 'Password too short (Supabase default is 6 characters)'
    
    return msg


