# Here inside this core folder, we create this config.py file to store the configuration settings for our project.
# This file will contain the settings for our database, API keys, and other configuration settings that we need for our project like constants. This way we can keep all the configuration settings in one place and easily manage them.


import os
from pathlib import Path
# Here we are using the 'dotenv' library to load the environment variables from the .env file. This way we can access the environment variables in our code using 'os.getenv()' method.
# Here we need this os library to access the environment variables from the .enf file. And this Path library from pathlib is used to get the path of the .env file.

# Now if this .env file is missing or if we are not able to load the environment variables from the .env file, then we will get an error. So to avoid that error, we will check if the .env file is present in the project or not. If it is present, then we will load the environment variables from the .env file using 'dotenv' library. So we will use try and except block to handle that error.

try:
    from dotenv import load_dotenv
    load_dotenv()
    # Here we are using the 'load_dotenv()' method to load the environment variables from the .env file suring the first loading of this config file & later we can easily access them. This method will read the .env file and set the environment variables in the system. So after calling this method, we can access the environment variables using 'os.getenv()' method.
except ImportError:
    pass     # If the 'dotenv' library is not installed, we will just pass and continue with the code execution. This way we can avoid the error if the 'dotenv' library is not installed.



# api metadata 
APP_TITLE = "ResumeIQ - Intelligent ATS Scoring & Feedback"
APP_VERSION = "1.0.0"   
APP_DESCRIPTION = "Analyse resumes against job description using NLP + ML"


# Allowed origins for CORS (Cross-Origin Resource Sharing)
# CORS is a security feature implemented by web browsers to restrict web applications running on one origin (domain) from interacting with resources from a different origin. This is done to prevent malicious websites from making unauthorized requests to other websites on behalf of the user.
# In our case, we will be running our frontend (React) on a different port (5173) than our backend (FastAPI) which is running on port 8000. So we need to allow the requests from our frontend to our backend by adding the frontend URL in the allowed origins list. This way we can enable CORS for our frontend and allow it to make requests to our backend without any issues.
# For example, if our backend server is running on http://localhost:8000 & we don't have CORS enabled, then any frontend application can make a call or request to our backend server, but if we have CORS enabled and we have added the frontend URL in the allowed origins list, then only that frontend application can make a call or request to our backend server. This way we can restrict the access to our backend server and only allow the requests from our frontend application.
# If any frontend those URL is not added in this allowed origins list, then that frontend will not be able to make a call or request to our backend server and it will get an error. This way we can ensure that only our frontend application can access our backend server and other applications cannot access it.
ALLOWED_ORIGINS = [
    # Here these are the URLs of our frontend applications which will be making requests to our backend server. So we need to add those URLs in this allowed origins list to enable CORS for those frontend applications.
    "http://localhost:5173",            # vite dev server (React)
    "http://localhost:3000",            # Create React App fallback
    # Here this is react app fallback URL, it means that if we are using Create React App for our frontend development, then it will run on port 3000 by default. So we need to add this URL in the allowed origins list to enable CORS for our Create React App frontend application.
    "http://127.0.0.1:5173",
]


# file
MAX_FILE_SIZE_MB=5
MAX_FILE_SIZE_BYTES=MAX_FILE_SIZE_MB*1024*1024


# Supported MIME types and their short names
# MIME type is a standard that indicates the nature and format of a file. It is used to identify the type of file being uploaded or processed. In our case, we will be accepting resumes in PDF, DOC, and DOCX formats. So we need to define the supported MIME types for these file formats and their corresponding short names. This way we can easily identify the type of file being uploaded and process it accordingly.
SUPPORTED_MIME_TYPES = {
    'application/pdf': "pdf",
    'application/msword': "doc",
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': "docx",
}


SUPPORTED_EXTENSIONS = {'.pdf', '.doc', '.docx'}

# Here this is primary and secondary spacy models, we will use the primary model for better accuracy and if there is any issue with the primary model, then we will use the secondary model as a fallback. This way we can ensure that our application is working smoothly without any issues. And also we can easily switch between the models if we want to improve the accuracy or if we want to use a different model in the future.
SPACY_MODEL_PRIMARY="en_core_web_md"      # better accuracy
SPACY_MODEL_SECONDARY="en_core_web_sm"

# Here this os.getenv() method is used to get the value of the environment variable 'SENTENCE_TRANSFORMER_MODEL' from the .env file. If this environment variable is not set in the .env file, then it will use the default value 'all-MiniLM-L6-v2'. This way we can easily switch between different models by just changing the value of the environment variable in the .env file without changing the code. This makes our code more flexible and easier to maintain in the future.
# So here it will use this 'all-MiniLM-L6-v2' model only if we don't have any other model specified in the .env file. If we have any other model specified in the .env file, then it will use that model instead of this default model. This way we can easily switch between different models by just changing the value of the environment variable in the .env file without changing the code. This makes our code more flexible and easier to maintain in the future.
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
# So here we are using transformers actually.


# Score component weights - this is business logic treated as config
# here this bussiness login, we are writting here in config file because we want that if we want to change the weights of the score components in the future, then we can easily change them from this config file without changing the code. This way we can easily maintain and update our code in the future without worrying about breaking other parts of the code. This is one of the main principles of software development which is separation of concerns. By keeping our code organized and modular, we can ensure that our code is maintainable and scalable in the future.
SCORE_WEIGHTS = {
    "formatting": 20, "keywords": 25, "content": 25,
    "skill_validation": 15, "ats_compatibility": 15,
}


JD_KEYWORD_WEIGHT=0.6
JD_SEMANTIC_WEIGHT=0.4


# Here this Tries to read the environment variable named GROQ_API_KEY. If it exists, the value (your actual API key string) is returned. If it doesn’t exist, it falls back to an empty string ('').
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')