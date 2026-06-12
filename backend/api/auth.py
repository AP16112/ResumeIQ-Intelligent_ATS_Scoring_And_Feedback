# Here inside this api folder, we will create this routes.py & auth.py files to define the API endpoints & their authentication logic for our project.
# API endpoints are the points of entry or access to a resource or service. They are the URLs that we will use to access the resources or services provided by our API.

# This file is essentially our authentication layer for the FastAPI backend.
# It defines API authentication logic using JWT tokens issued by Supabase.
# Ensures that only signed‑in users can access protected endpoints.
# Provides helper functions to verify tokens and extract the current user’s identity


# JWT :-
# JWT (JSON Web Token) is a compact, secure way to transmit identity and claims between parties, often used for authentication and authorization in APIs. 
# It encodes user information as a JSON object, digitally signed (and sometimes encrypted) so the recipient can trust its integrity.



# Python’s built-in logging framework for tracking events, errors, and debug information.
# Key uses:
# Helps you record messages at different severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
# Useful for debugging and monitoring applications without using print() everywhere.
import logging


# It is simply importing the PyJWT library into your Python file so you can work with JSON Web Tokens (JWTs).
# jwt refers to the PyJWT package, a popular Python library for encoding and decoding JWTs.
# Once imported, you can use functions like:
# jwt.encode(payload, secret, algorithm="HS256") → creates a JWT.
# jwt.decode(token, secret, algorithms=["HS256"]) → verifies and decodes a JWT.
# jwt.get_unverified_header(token) → inspects the header without verifying.
# jwt.PyJWKClient(url) → fetches public keys (JWKS) for verifying asymmetric JWTs.
import jwt
# Our auth.py file uses jwt to:
# Verify tokens issued by Supabase.
# Decode payloads to extract the user ID (sub claim).
# Handle different signing algorithms (HS256, RS256, ES256).
# Without import jwt, none of those token verification functions would work.


# here we are importing three important utilities from FastAPI that are commonly used in API route definitions
# HTTPException :- Used to raise HTTP errors inside route handlers.
# Lets you return proper status codes and error messages when something goes wrong.
# status :- Provides constants for HTTP status codes (instead of hardcoding numbers).
from fastapi import Depends, HTTPException, status

# Here we are importing two security utilities from FastAPI’s security module that are used for handling Bearer token authentication.
# HTTPAuthorizationCredentials :- A data class that represents the credentials extracted from the Authorization header.
# When a client sends:
# Authorization: Bearer <token>
# FastAPI parses this into an HTTPAuthorizationCredentials object with:
# .scheme → "Bearer"
# .credentials → the actual token string
# HTTPBearer :- A security scheme class that tells FastAPI to expect a Bearer token in the Authorization header.
# It validates that the header is present and properly formatted.
# Often used with Depends to inject the token into route handlers.
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


# Secret used to verify JWT access tokens issued by Supabase Auth. Ensures that tokens presented by users are valid and signed correctly. Used in backend authentication flows.
from backend.core.config import SUPABASE_JWT_SECRET, SUPABASE_URL

# Here we are defining the name  of our logger as 'ats_resume_scorer', so that we can easily identify the logs related to our application in the log files. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the logs. We will use this logger to log the errors and other important information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application.
logger = logging.getLogger('ats_resume_scorer')


# HTTPBearer is FastAPI’s security class that expects an Authorization: Bearer <token> header.
# By default, if the header is missing or invalid, it raises an error automatically.
# Here, auto_error=False means:
# It won’t immediately throw an error if the header is missing.
# Instead, it will return None, and your code can handle the error manually.
# This gives you more control over how to respond (e.g., custom error messages, logging).
_bearer_scheme = HTTPBearer(auto_error=False)


# This is a list of JWT signing algorithms that use asymmetric cryptography:
# RS256 → RSA with SHA‑256
# ES256 → ECDSA (Elliptic Curve) with SHA‑256
# Asymmetric algorithms use a public/private key pair:
# The server signs the token with its private key.
# Clients (or other servers) verify the token using the public key.
# In your project, these are supported algorithms for verifying Supabase JWTs via JWKS (JSON Web Key Set).
_ASYMMETRIC_ALGS = ['ES256', 'RS256']



# Here we are setting up a global variable that will hold a JWKS client for verifying JWTs.
# _jwks_client :- The variable name starts with _, which is a convention meaning “internal/private use.” It will store an instance of jwt.PyJWKClient.
# Type hint: jwt.PyJWKClient | None :- This means _jwks_client can either be:
# A PyJWKClient object (used to fetch and cache JSON Web Keys from a JWKS endpoint).
# Or None (when not initialized yet).
# The | None part is Python’s way of saying “optional.”
_jwks_client: jwt.PyJWKClient | None = None



# This function is responsible for initializing and caching a JWKS client that can fetch public keys used to verify JWTs from Supabase
# Returns either a jwt.PyJWKClient object or None. This client is used to fetch and cache JSON Web Keys (JWKS).
def _get_jwks_client() -> jwt.PyJWKClient | None:
    # Refers to the global variable _jwks_client defined earlier. Ensures the function modifies and reuses the same client instance across calls.
    global _jwks_client

    if _jwks_client is not None:
        return _jwks_client
    
    # If there’s no Supabase project URL, the client cannot be built. Returns None to signal misconfiguration.
    if not SUPABASE_URL:
        return None
    
    # Constructs the endpoint where Supabase publishes its JWKS (public keys).
    # .rstrip('/') :- Removes any trailing / from the Supabase URL. Ensures you don’t accidentally end up with double slashes (//) when concatenating paths.
    # /auth/v1/.well-known/jwks.json :- This is the standard endpoint where Supabase publishes its JWKS.
    # JWKS = JSON Web Key Set → a JSON document containing public keys.
    # These keys are used to verify JWTs signed with asymmetric algorithms (RS256, ES256).
    jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"


    # Here we are creating a JWKS client that knows how to fetch and cache public keys for verifying JWTs
    # PyJWKClient is a helper class from the PyJWT library. It connects to a JWKS (JSON Web Key Set) endpoint — in your case, Supabase’s: https://<your-supabase-url>/auth/v1/.well-known/jwks.json
    # That endpoint publishes the public keys Supabase uses to sign JWTs with asymmetric algorithms (RS256, ES256).
    # The client can then fetch the correct key for a given token and use it to verify the signature.
    # cache_keys=True :- Enables caching of the JWKS keys locally.Prevents repeated network calls for every token verification. Improves performance and reduces latency.
    # lifespan=3600 :- Sets the cache lifespan to 3600 seconds (1 hour). After this time, the client will refresh the keys from Supabase. Ensures you don’t use stale keys if Supabase rotates them.
    _jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
    
    return _jwks_client





# Defines a private helper function (_verify_token) that takes a JWT string (token) as input. Returns a decoded payload (dict) if verification succeeds.
def _verify_token(token: str) -> dict:
    # jwt.get_unverified_header(token) :- Extracts the header part of the JWT without verifying the signature.
    # The header contains metadata about the token, such as:
    # alg → the signing algorithm (e.g., HS256, RS256, ES256).
    # typ → the type of token (JWT).
    header = jwt.get_unverified_header(token)

    # Retrieves the alg (algorithm) value from the header. This tells the backend how the token was signed.
    # The code later uses this to decide:
    # If it’s asymmetric (RS256, ES256) → verify using JWKS public keys.
    # If it’s symmetric (HS256) → verify using the shared secret (SUPABASE_JWT_SECRET).
    # If unsupported → raise an error.
    alg = header.get('alg')


    # It is handling JWT verification when the token uses an asymmetric algorithm (RS256 or ES256)
    # These are asymmetric algorithms (RSA/ECDSA) that require a public/private key pair
    if alg in _ASYMMETRIC_ALGS:
        # Calls the helper function to fetch or reuse a cached JWKS client. JWKS (JSON Web Key Set) is a published list of public keys from Supabase.
        jwks_client = _get_jwks_client()

        if jwks_client is None:
            raise jwt.InvalidTokenError(
                'SUPABASE_URL not configured — cannot fetch JWKS to verify token'
            )
        
        # Uses the JWKS client to find the correct public key for this token.
        # Each JWT has a kid (key ID) in its header that matches a key in the JWKS.
        # Retrieves the actual public key needed to verify the signature.
        signing_key = jwks_client.get_signing_key_from_jwt(token).key


        # Verifies the token’s signature using the public key. Ensures the algorithm is one of the supported asymmetric ones.
        # Checks that the aud (audience) claim matches "authenticated". Returns the decoded payload (claims) as a dictionary.
        return jwt.decode(
            token,
            signing_key,
            algorithms=_ASYMMETRIC_ALGS,
            audience='authenticated',
        )


    # It is handling JWT verification when the token uses the symmetric algorithm HS256
    # If the JWT header says the token was signed with HS256 (HMAC using SHA‑256), then this branch runs. HS256 is a symmetric algorithm: the same secret key is used to both sign and verify the token.
    if alg == 'HS256':
        if not SUPABASE_JWT_SECRET:
            raise jwt.InvalidTokenError(
                'HS256 token received but SUPABASE_JWT_SECRET is not configured'
            )
        
        # Uses the shared secret (SUPABASE_JWT_SECRET) to verify the token’s signature. Ensures the algorithm is HS256.
        # Checks that the aud (audience) claim matches "authenticated". Returns the decoded payload (claims) as a dictionary.
        return jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=['HS256'],
            audience='authenticated',
        )

    raise jwt.InvalidTokenError(f'Unsupported JWT algorithm: {alg}')




# This function’s job is to extract and verify the current user from the request’s Bearer token.
# Type: HTTPAuthorizationCredentials | None :- Either an HTTPAuthorizationCredentials object (if a token is provided). Or None (if no token is present).
# This object contains:
# .scheme → "Bearer"
# .credentials → the actual JWT string.
# Depends(_bearer_scheme) :- FastAPI’s dependency injection system.
# _bearer_scheme is an instance of HTTPBearer(auto_error=False).
# This tells FastAPI:
# Look for an Authorization: Bearer <token> header in the request. If found, inject it into creds.
# If missing, inject None (because auto_error=False).
def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme) ) -> str:
    # It is the case where the Authorization header is missing or invalid
    if creds is None or not creds.credentials:
        # headers={'WWW-Authenticate': 'Bearer'} :- Adds a WWW-Authenticate header to the response.
        # This is part of the HTTP standard, telling the client it must use Bearer authentication.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing Authorization: Bearer <token> header',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if not SUPABASE_URL and not SUPABASE_JWT_SECRET:
        logger.error('Neither SUPABASE_URL (for JWKS) nor SUPABASE_JWT_SECRET configured — cannot verify tokens')
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Auth not configured on the server',
        )


    try:
        # Calls _verify_token with the JWT string (creds.credentials).
        # If the token is valid, it returns the decoded payload (claims). If invalid or expired, exceptions are raised.
        payload = _verify_token(creds.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired — sign in again',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid token: {exc}',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception as exc:
        # PyJWKClient can raise network errors fetching JWKS; surface them as 401
        # so a misconfigured backend doesn't look like a 500 to the user.
        # If the JWKS client fails to fetch keys (e.g., Supabase URL misconfigured, network down), it would normally throw a generic exception.
        # Instead of returning a 500 Internal Server Error (which implies a server bug), the code surfaces it as a 401 Unauthorized.
        # This makes it clear to the client: “Your token couldn’t be verified,” not “The server crashed.”
        logger.warning(f'JWT verification failed: {exc}')

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Token verification failed: {exc}',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    
    # If verification succeeded, the decoded payload is available.
    # Retrieves the sub (subject) claim, which is the user ID.
    user_id = payload.get('sub')

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token missing subject claim',
        )
    

    return user_id



