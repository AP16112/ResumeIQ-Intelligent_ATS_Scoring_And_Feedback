# Here inside this utils folder, we will decide all the logs and error things for our project.

# Not all errors are same, some are critical, some are warnings, some are just info, so we will use different log levels to log different types of errors and information in our application. This way we can easily identify the critical errors and also we can easily identify the warnings and other information in our application. This way we can keep track of the errors and other important information in our application and also we can easily debug our application by looking at the logs.

import logging   # it is used for logging the errors and other information in our application. It helps us to keep track of the errors and other important information in our application. We can use it to log the errors, warnings, and other information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
import sys  # here we are importing the sys module to use the sys.stdout for logging the warnings and other information in our application. This way we can easily identify the warnings and other information in our application by looking at the console output. This way we can keep track of the warnings and other important information in our application and also we can easily debug our application by looking at the console output. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
# stdout means that the logs will be printed in the console, so that we can easily identify the warnings and other information in our application by looking at the console output. This way we can keep track of the warnings and other important information in our application and also we can easily debug our application by looking at the console output. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
import os    # here we are importing the os module to use the os.path.join to create the log directory and also to create the log file in that directory. This way we can keep our logs organized in a separate directory and also we can easily identify the logs related to our application by looking at the log files in that directory. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the log files in that directory. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar
# here we are importing these Any, Callable, Dict, Optional, Tuple, TypeVar from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
# Any means that the variable can be of any type, Callable means that the variable is a function, Dict means that the variable is a dictionary, Optional means that the variable can be of the specified type or it can be None, Tuple means that the variable is a tuple, TypeVar is used to define a generic type variable which can be used in function definitions to indicate that the function can accept arguments of any type and return a value of the same type. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.



LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
# So this will check whether this LOG_DIR exists in our project or not & if not then it will create this directory & add all the logs in that
# But if directory exists already, then it will simply add all the logs in that 

# __file__  :- Refers to the current Python file’s path (e.g., backend/main.py).
# os.path.dirname(__file__)  :- Gets the directory containing the current file (e.g., backend).
# os.path.dirname(os.path.dirname(__file__)) :-  Goes one level higher (the parent directory of backend, e.g., ResumeIQ).
# os.path.join(..., 'logs')  :- Appends 'logs' to that path, so the final directory is something like: C:\Arpit pal\Prime Batch Projects\Project 2 - AI Resume ATS System\ResumeIQ\logs
# os.makedirs(LOG_DIR, exist_ok=True) :-Creates the logs folder if it doesn’t already exist.
# exist_ok=True prevents errors if the folder is already there.


# Here we are defining the name  of our logger as 'ats_resume_scorer', so that we can easily identify the logs related to our application in the log files. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the logs. We will use this logger to log the errors and other important information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application.
logger = logging.getLogger('ats_resume_scorer')
logger.setLevel(logging.INFO)

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

# logger.setLevel(logging.INFO) :-
# Sets the minimum severity level of messages this logger will handle.
# Levels (from lowest to highest):
# DEBUG → detailed developer info
# INFO → general runtime events (startup, shutdown, normal operations)
# WARNING → something unexpected but not fatal
# ERROR → serious problems that prevent part of the program from working
# CRITICAL → severe errors that may crash the program
# By setting INFO, you’ll capture INFO, WARNING, ERROR, and CRITICAL messages, but ignore DEBUG.
# Ensures you only see messages at or above the chosen severity level.


# Simplified file handler - only basic logs
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "ats_scorer.log"))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

# logging.FileHandler(...) :-
# Creates a handler that writes log messages into a file. Here, the file path is LOG_DIR/ats_scorer.log.
# So all logs will be saved in a file named ats_scorer.log inside your logs directory.

# file_handler.setLevel(logging.INFO) :-
# Sets the minimum severity level for this handler. Only messages at INFO or higher (WARNING, ERROR, CRITICAL) will be written to the file.
# DEBUG messages will be ignored.

# file_handler.setFormatter(...) :-
# Defines the format of each log entry. '%(asctime)s - %(levelname)s - %(message)s' means:
# asctime → timestamp (when the log was recorded)
# levelname → severity level (INFO, WARNING, ERROR, etc.)
# message → the actual log message
# e.g 2026-06-09 14:35:12,345 - INFO - Application started



# Simplified console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# logging.StreamHandler(sys.stdout) :-
# Creates a handler that sends log output to the console (standard output). So whenever your app logs something, it will appear in the terminal window.

# console_handler.setLevel(logging.WARNING) :-
# Sets the minimum severity level for this handler. Only messages at WARNING, ERROR, or CRITICAL will be shown in the console.
# Lower‑level INFO or DEBUG messages will be ignored here (but could still be written to a file if you have a file handler).

# console_handler.setFormatter(...) :-
# Defines how the log message will look in the console. '%(levelname)s: %(message)s' means:
# levelname → the severity (e.g., WARNING, ERROR)
# message → the actual log text
# e.g WARNING: Resume missing key skills
# ERROR: Failed to connect to database



# Checks if the logger doesn’t already have any handlers attached. And if not then it will attaches the file handler we created earlier.
# This means logs will be written to logs/ats_scorer.log.
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)



class ATSBaseError(Exception):
    """Simple base class for ATS errors."""

    def __init__(self, message: str, user_message: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.message = message
        self.user_message = user_message or 'An error occured. Please try again.'

# class ATSBaseError(Exception):-
# Defines a base class for all ATS‑related errors. Inherits from Python’s built‑in Exception.
# This makes it easy to catch all ATS errors with one except ATSBaseError: block.

# __init__ method :-
# Accepts two messages:
# message: the internal developer‑oriented error message. This is what you would log for debugging purposes.
# user_message: an optional user‑friendly message.
# If no user_message is provided, it defaults to: "An error occurred. Please try again."
# This separation allows you to log detailed technical errors while showing users a clean, non‑technical message.

# kwargs stands for keyword arguments.
# The double asterisks (**) mean “collect any extra keyword arguments into a dictionary.”
# e.g ATSBaseError("Something broke", user_message="Oops!", code=500, retry=True)
# Here, code=500 and retry=True are not explicitly defined in the __init__ signature, so they get bundled into kwargs:
# kwargs == {"code": 500, "retry": True}
# If later you want to store more attributes (like error codes, context, or request IDs), you can accept them via **kwargs.




class FileUploadError(ATSBaseError):
    pass


class FileParsingError(ATSBaseError):
    pass


class TextExtractionError(ATSBaseError):
    pass

# Here, These are specialized error classes that inherit from ATSBaseError.
# They don’t add new behavior (hence pass), but they give semantic meaning:
# FileUploadError: problems during file upload (e.g., unsupported format).
# FileParsingError: issues while parsing the uploaded file (e.g., corrupted PDF).
# TextExtractionError: failures when extracting text from a document (e.g., OCR errors).


def log_error(error: Exception, context: Optional[str] = None, **kwargs) -> None:
    """Log an error simply."""
    logger.error(f"Error in {context or 'unknown'}: {error}")

# error: Exception → expects an exception object (e.g., ValueError, FileUploadError).
# context: Optional[str] = None → optional string describing where the error happened (e.g., "file upload", "resume parsing"). Defaults to None.
# **kwargs → catch‑all for any extra keyword arguments. Currently unused, but allows flexibility if you want to pass extra metadata later (like user_id=123 or filename="resume.pdf").

# Docstring :- "Log an error simply." → explains the purpose: a lightweight wrapper around logger.error.
# logger.error(...) : Logs the error at ERROR level (so it will be picked up by both file and console handlers if configured).



def log_warning(message: str, context: Optional[str] = None, **kwargs) -> None:
    """Log an warning simply."""
    logger.warning(f"{context}: {message}" if context else message)


def log_info(message: str, context: Optional[str] = None, **kwargs) -> None:
    """Log info simply."""
    logger.info(f"{context}: {message}" if context else message)   

# message: str → the text you want to log.
# context: Optional[str] = None → optional label describing where the log is coming from (e.g., "resume parsing", "file upload").
# **kwargs → catch‑all for extra keyword arguments. Currently unused, but allows future extension (e.g., logging metadata like user_id=123).

# logger.warning(...) / logger.info(...) :-
# Calls the appropriate logging method:
# logger.warning → logs at WARNING level (visible in console if your handler is set to WARNING+).
# logger.info → logs at INFO level (written to file if your file handler is set to INFO+).
# The message format: If context is provided → "context: message"


# TypeVar comes from the typing module. It lets you define a generic type placeholder — a symbol that can stand for any type.
# T here is a variable representing some type that will be decided later when the function or class is used.
T = TypeVar('T')

def with_fallback(primary_func: Callable[..., T], fallback_func: Callable[..., T], *args, log_fallback: bool = True, **kwargs) -> Tuple[T, bool]:
    # Remove error_category if passed by accident
    kwargs.pop('error_category', None)

    try:
        return primary_func(*args, *kwargs), False
    except Exception as primary_error:
        if log_fallback:
            log_warning(f"Primary method failed, trying fallback: {primary_error}")

        try:
            return fallback_func(*args, **kwargs), True
        except Exception as fallback_error:
            log_error(fallback_error, context="fallback")
            raise   # Re‑raises the exception so the caller knows everything failed.

# primary_func: Callable[..., T] → the main function to try first.
# fallback_func: Callable[..., T] → the backup function if the primary fails.
# *args → positional arguments passed to both functions.
# **kwargs → keyword arguments passed to both functions.
# log_fallback: bool = True → whether to log a warning when falling back.
# Returns Tuple[T, bool] → the result of whichever function succeeded, plus a flag (False if primary succeeded, True if fallback was used).

# kwargs.pop('error_category', None) :-
# Removes error_category if it was accidentally passed in.
# This prevents unexpected keyword arguments from breaking the function call.

# return primary_func(*args, *kwargs), False :-
# Calls the primary function with the given arguments.
# If it succeeds, returns the result and False (meaning no fallback was needed).

# def demo(*args, **kwargs):
#     print("args:", args)
#     print("kwargs:", kwargs)

# demo(1, 2, 3, x=10, y=20)
# # Output:
# # args: (1, 2, 3)
# # kwargs: {'x': 10, 'y': 20




def get_default_grammar_results() -> Dict:      # Declares a function that returns a dictionary (Dict type).
    return {
        'total_errors': 0,
        'critical_errors': [],
        'moderate_errors': [],
        'minor_errors': [],
        'grammar_score': 100,
        'penalty_applied': 0,
        'error_free_percentage': 100,
        '_component_status': 'unavailable',    # Internal flag showing grammar checking isn’t active.
        '_note': 'Grammar checking unavailable.'   # Human‑readable note explaining why defaults are returned.
    }


def get_default_location_results() -> Dict:
    return {
        'location_found': False,
        'detected_locations': [],
        'privacy_risk': 'unknown',
        'recommendations': ['Location detection unavailable.'],
        'penalty_applied': 0,
        '_component_status': 'unavailable',
        '_note': 'Location detection unavailable.'
    }


def get_default_skill_validation_results() -> Dict:
    return {
        'validated_skills': [],
        'unvalidated_skills': [],
        'validation_percentage': 0.0,
        'skill_project_mapping': {},
        'validation_score': 0.0,
        '_component_status': 'unavailable',
        '_note': 'Skill validation unavailable.'
    }


def get_default_jd_comparison_results() -> Dict:
    return {
        'semantic_similarity': 0.0,
        'matched_keywords': [],
        'missing_keywords': [],
        'skills_gap': [],
        'match_percentage': 0.0,
        '_component_status': 'unavailable',
        '_note': 'JD comparison unavailable.'
    }