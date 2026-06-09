#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Project :- ResumeIQ - "Intelligent ATS scoring & feedback"

# ResumeIQ – Intelligent ATS Scoring & Feedback is an AI‑powered web application that evaluates resumes against job descriptions, providing ATS compatibility scores along with clear, actionable feedback. 
# Built with FastAPI, Streamlit, and NLP models like BERT and spaCy, it helps candidates optimize their resumes to improve job search success.

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# In this file, we will write the logic of FastAPIs
# So this file will acts as the gateway or main entry point for our backend i.e FastAPI backend.
# Whenever user sends the request to our API, then that request will be received by this file and then we will process that request and send the response back to the user.


# Here to use FastAPI, we need to import it first
# And we also need to import 'uvicorn' to run our API server
# SO we will use :- pip install fastapi uvicorn
 
# FastAPI is a modern, fast (high-performance) python based web framework for building APIs with Python 3.6+ based on standard Python type hints.

# So here FastAPI will handdle the server and API endpoints, and we will write the logic of our model in the API endpoints.
# It means that server side programming will be handled by FastAPI.

# Whenever user sends the request using UI to our API or server, then that request is received by a special layer called as 'API endpoint' and then that API endpoint will process the request and send the response back to the user.
# API = Application Programming Interface
# Endpoint = A point of entry or access to a resource or service

# And FastAPi helps us to create API endpoints easily and efficiently. It also provides automatic documentation for our API using Swagger UI and ReDoc.
# uvicorn is a lightning-fast ASGI web server implementation, using uvloop and httptools. It is designed to be easy to use and deploy, and it is compatible with a wide range of web frameworks, including FastAPI.


import logging   # it is used for logging the errors and other information in our application. It helps us to keep track of the errors and other important information in our application. We can use it to log the errors, warnings, and other information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from contextlib import asynccontextmanager
# here this asynccontextmanager is a context manager for asynchronous code. It allows us to define a context manager that can be used in an asynchronous context. This is useful for managing resources that need to be cleaned up after use, such as database connections or file handles, in an asynchronous environment.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# here we are importing the CORSMiddleware from fastapi.middleware.cors to enable CORS (Cross-Origin Resource Sharing) for our API. 
# CORS is a security feature implemented by web browsers to restrict web applications running on one origin (domain) from interacting with resources from a different origin. By enabling CORS, we can allow our frontend application (which is running on a different port) to make requests to our backend API without any issues.
# CORS is made up of three things i.e protocol, domain, and port. So if any of these three things are different between the frontend and backend, then we need to enable CORS to allow the requests from the frontend to the backend. In our case, our frontend is running on port 5173 and our backend is running on port 8000, so we need to enable CORS to allow the requests from the frontend to the backend.
# By default, CORS is disabled in FastAPI, so we need to enable it by adding the CORSMiddleware to our FastAPI application and specifying the allowed origins, methods, and headers. This way we can ensure that our frontend application can communicate with our backend API without any issues.


# Here we are importing all these things which we define inside config.py file, so that we can use them here
from backend.core.config import(
    ALLOWED_ORIGINS,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    SPACY_MODEL_PRIMARY,
    SPACY_MODEL_SECONDARY,
    SENTENCE_TRANSFORMER_MODEL
)

# Here we are importing the router from the routes.py file which is inside the api folder, so that we can include that router in our FastAPI application and use the API endpoints defined in that router. This way we can keep our code organized and modular by separating the API endpoints into different files and then including them in our main application file.
from backend.api.routes import router
 

# Here we are defining the name  of our logger as 'ats_resume_scorer', so that we can easily identify the logs related to our application in the log files. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the logs. We will use this logger to log the errors and other important information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application.
logger = logging.getLogger('ats_resume_scorer')
# Logging is the automated process of recording events, errors and system actions in real time.
# Here this logging.getLogger(name) :-
# Retrieves (or creates) a logger object identified by the string name.
# In this case, the name is 'ats_resume_scorer', which is like a label for all log messages coming from your ATS Resume Scorer project.
# logger :- This variable now holds the logger object.
# You’ll use it to log messages at different levels:
# logger.debug("Debugging info")
# logger.info("App started")
# logger.warning("Potential issue detected")
# logger.error("Error occurred")
# logger.critical("Critical failure")


# Define lifespan event handler for FastAPI using async context manager
# Here this lifespan fn is used to run some code during the startup and shutdown of the FastAPI application. It allows us to perform any necessary setup (like loading models) before the API starts serving requests, and also to perform any cleanup when the API is shutting down. This way we can ensure that our models are loaded and ready to serve requests before the API starts serving requests, and also we can log a message when the API is shutting down.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log startup message
    logger.info('Starting ResumeIQ - Intelligent ATS scoring & feedback API...')

    # Log which spaCy model is being loaded
    logger.info(f'Loading spaCy NLP model: {SPACY_MODEL_PRIMARY}')

    import spacy

    try:
        # Attempt to load the primary spaCy model and store it in app state
        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
        logger.info(f'Loaded {SPACY_MODEL_PRIMARY}')
    except OSError:
        # If primary model not found, fall back to secondary model
        logger.warning(f'{SPACY_MODEL_PRIMARY} not found - falling back to {SPACY_MODEL_SECONDARY}')
        app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)
        logger.info(f'Loaded {SPACY_MODEL_SECONDARY} (fallback)')

    # Log which SentenceTransformer model is being loaded
    logger.info(f'Loading SentenceTransformer : {SENTENCE_TRANSFORMER_MODEL}')

    from sentence_transformers import SentenceTransformer
    
    # Load SentenceTransformer model and store it in app state
    app.state.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    logger.info(f'Loaded {SENTENCE_TRANSFORMER_MODEL}')

    # Confirm all models are ready before serving requests
    logger.info('All models loaded. API is ready to serve requests.')

    # Yield control back to FastAPI — app runs and serves requests here
    yield

    # Log shutdown message when API is stopping
    logger.info('Shutting down the api!!')

# Here @asynccontextmanager decorator :-
# Marks the function as an asynchronous context manager.
# FastAPI uses this to run setup code before serving requests and cleanup code when shutting down.

# Function definition: async def lifespan(app: FastAPI) :-
# This is the lifespan handler.
# FastAPI will call it when the app starts and ends.
# The app parameter gives you access to the FastAPI instance.

# yield statement :-
# Marks the point where FastAPI starts serving requests.
# Everything before yield is startup code.
# Everything after yield is shutdown code.
# yield actually handles all the incoming requests to the API, so it is like a gateway for all the incoming requests to the API. It will keep the API running and serving the requests until we stop the API.

# So all the code written before the yield statement will be executed when the API starts i.e when our app starts, and all the code written after the yield statement will be executed when the API is shutting down. This way we can ensure that our models are loaded and ready to serve requests before the API starts serving requests, and also we can log a message when the API is shutting down.
# Because loading these models takes times & we don't want to load them again & agin whenever we want to use them, so that's why we are loading them once only during the startup of our app using this contextmanager and then we can access these models from the app state in our API endpoints whenever we want to use them. This way we can ensure that our models are loaded and ready to serve requests before the API starts serving requests, and also we can log a message when the API is shutting down.



# initializing our fastapi app
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,     # it means that we are using this lifespan function as the lifespan event handler for our FastAPI application, so that we can run some code during the startup and shutdown of the FastAPI application. This way we can ensure that our models are loaded and ready to serve requests before the API starts serving requests, and also we can log a message when the API is shutting down.
    docs_url='/docs',   # this is the URL for the Swagger UI documentation of our API. By default, it is set to '/docs', so we can access the Swagger UI by going to http://localhost:8000/docs in our browser. This way we can easily test our API endpoints and also we can see the interactive documentation for our API.
    redoc_url='/redoc'    # this is the URL for the ReDoc documentation of our API. By default, it is set to '/redoc', so we can access the ReDoc documentation by going to http://localhost:8000/redoc in our browser. This way we can see the alternative documentation for our API which is more detailed and structured than the Swagger UI documentation.
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

# app.add_middleware(CORSMiddleware, ...) :-
# app.add_middleware(...) is a FastAPI method that lets you attach middleware to your application.
# Adds the CORSMiddleware to your FastAPI app.
# This middleware controls which external domains (frontends, clients) can make requests to your API.

# allow_origins=ALLOWED_ORIGINS :-
# Defines which domains are allowed to call your API.
# Example: ["http://localhost:3000", "https://resumeiq.com"]. If a request comes from a domain not in this list, the browser will block it.

# allow_credentials=True :-
# Allows cookies, authentication headers, or other credentials to be sent with cross‑origin requests.
# Useful if your frontend needs to send JWT tokens or session cookies.

# allow_methods=['*'] :-
# Permits all HTTP methods (GET, POST, PUT, DELETE, etc.) from allowed origins.
# You could restrict it to specific methods if needed.

# allow_headers=['*'] :-
# Allows all request headers (like Authorization, Content-Type).
# Ensures your frontend can send custom headers without being blocked.


# Here we are including the router in our FastAPI application, so that we can use the API endpoints defined in that router. This way we can keep our code organized and modular by separating the API endpoints into different files and then including them in our main application file. This way we can easily manage our API endpoints and also we can easily test our API endpoints by using the Swagger UI documentation provided by FastAPI.
app.include_router(router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'backend.main.app',
        host = '0.0.0.0',
        port = 8000,
        reload = True,    # Auto-restart on code changes (dev only)
    )

# Here this  __name__ == '__main__' :-
# Ensures this block only runs when the file is executed directly (python filename.py).
# Prevents accidental execution if the file is imported elsewhere.

# import uvicorn :-
# Uvicorn is an ASGI server used to run FastAPI apps.
# It handles incoming HTTP requests and routes them to your FastAPI application.

# uvicorn.run('backend.main.app', ...) :-
# Starts the server with the app located at backend/main.py and the variable app.
# The string 'backend.main.app' means:
# backend → package name
# main → module (file) name
# app → FastAPI instance inside that file

# Parameters :-
# host='0.0.0.0' → Makes the app accessible from any network interface (not just localhost). Useful for deployment or Docker.
# port=8000 → Runs the server on port 8000 (default for FastAPI).
# reload=True → Enables auto‑reload when code changes. Great for development, but should be disabled in production.


# Here we also need to install spacy & also spacy models :-
# python -m spacy download en_core_web_md
# python -m spacy download en_core_web_sm

# And also we need to install sentence-transformers library to use the SentenceTransformer model :-
# pip install "sentence-transformers>=2.5"



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Now ro run this app, we will use this :-
# And we also need to install fastapi & uvicorn in that env only
# SO we will use :- pip install fastapi uvicorn
# And then use this :-
# python -m uvicorn backend.main:app --reload
# Here python -m ensures that we are using the correct uvicorn i.e the one installed in our current environment. backend.main:app tells uvicorn where to find the FastAPI application instance. --reload enables auto-reloading of the server when code changes, which is useful during development.


# But if we want to run this application on some custom port, then we will use this :-
# python -m uvicorn backend.main:app --reload --port 8000

# To access the swagger UI, just add /docs at the end of your localhost URL in the browser, like this :-
# http://127.0.0.1:8000/docs




# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# In this AI Resume ATS System project, we will use FastAPI for backend :-
# FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.

# Why we are using FastAPI here for backend :-
# 1. Because for ATS system, we want speedy response & FastAPi is Fast.
# 2. It is Asynchronous, so it can handle all the incoming multiple requests in a efficient way.
# 3. Also FastAPI's works very well with AI/ML integration & it works well with python libraries like transformer, BERT etc.
# 4. Also it is very easy to send and receive the JSON with FastAPi
# 5. In other backend technologies, we check API endpoints, we need to use third party tools like POSTMAN, HOPPSCOTCH, etc, but with FastAPI, there is not need of that, as it has its own API endpoints checking system which is using Swagger UI.
# 6. FastAPI uses Pydantic which helps in automatic data validation such as we can define the input type of the data & also what types of output we are expecting. And if the data is not following the specific type defined by us, then we can give error.
# 7. FastAPI also provides automatic interactive API documentation using Swagger UI and ReDoc, which makes it easy to test and debug our API endpoints.
# 8. Also it provides endpoints checking system which is called as 'Swagger UI' which is very useful for testing our API endpoints and also it provides interactive documentation for our API.


# Although we can also use Flask for this project, but we generally use Flask for beginner level projects & not for this major projects
# Flask is also a python framework which we used for beginner level projects.
# Also Flask is by-default synchronous, and to make it Async, we need to write extra code.
# And in Flask, we need to use manual validation.

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Pydantic :-
# pydantic is a data validation and settings management library for Python. It uses Python type annotations to validate and parse data. It is used in FastAPI to define the structure of the request and response data.
# pydantic is a python module which is used to validate the requests.
# Like here we want the input text which is coming from the user to be in a specific format or data type, so we will use pydantic to define that format and validate the input data type.


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
