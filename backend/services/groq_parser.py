# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'groq_parser.py' file to write the logic for parsing the unstructured text which we get from resume_parser file, to get the structured text for ATS scoring. 
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.


# When user upload the resume, our backend will not receive the nicely structured document or data but actually received the bytes or stream of data actually
# So backend will not have any idea that the received data is pdf or doc or etc, so for that we need to make use of io and magic to determine that
# So the resume_parser file will acts as the gateway between the input resume file & the backend & through this we will identify the type of file & other things.

# But this resume_parser will give us the long large block of unstructured text only after performing the raw parsing & to get the structured text like in which we know where name is , where projects are, etc, we will perform parsing of this using Groq LLM here
# Although we can also use regex i.e regular expression to get the structured text from this unstructured text but problem with that is we need to define manual regrex expression for each type of resume.
# Regex is Precise but rigid. Needs manual rules for each resume format. Breaks easily if formatting changes.
# And if 100 users upload 100 types of resumes, then we need to define manual rules to parse them using regex.
# That's why it is not suitable now-a-days and it's better to use LLM for that.

# LLM (Groq, GPT, etc.): Learns patterns across resumes. Can infer “this looks like a project section” even if headings differ.
# Handles messy text, typos, and variations.Produces structured output reliably.
# So we will fetch the parsed text from the LLM in the form of JSON dictionary actually.

# LLM Parsing (here we will use Groq LLM) gives structured JSON (in which contact, skills, experience are easily readable)

import os    # here we are importing the os module to use the os.path.join to create the log directory and also to create the log file in that directory. This way we can keep our logs organized in a separate directory and also we can easily identify the logs related to our application by looking at the log files in that directory. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the log files in that directory. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
import json 
import logging    # it is used for logging the errors and other information in our application. It helps us to keep track of the errors and other important information in our application. We can use it to log the errors, warnings, and other information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application. We will write all the logging related code in this file only, so that we can keep our code organized and modular.

from typing import Dict
# here we are importing this Dict from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.

from groq import Groq

# Here we are defining the name of our logger as 'ats_resume_scorer', so that we can easily identify the logs related to our application in the log files. This way we can keep track of the logs related to our application and also we can easily debug our application by looking at the logs. We will use this logger to log the errors and other important information in our application. This way we can easily debug our application and also we can keep track of the errors and other important information in our application.
logger = logging.getLogger('ats_resume_scorer')

GROQ_MODEL = 'llama-3.3-70b-versatile'     # we will use this LLM model of Groq here


# In Python, putting an underscore (_) at the front of a function name (like _get_headers) is a naming convention that signals: Private / internal use
# It tells other developers: “This function or variable is meant for internal use inside this module/class, not part of the public API.”
# Python doesn’t enforce strict privacy (like private in Java or C++), but the underscore is a strong hint.
# _client is the variable you expect other modules or users to call.
# If someone imports your module with from this, import *, _client will not be imported automatically because of the underscore.
_client = None


# Here it defines a private helper function. And The expected output will be Groq client object
def _get_client() -> Groq:
    # Refers to the module‑level variable _client. Ensures the function modifies the shared _client instead of creating a local one.
    global _client

    if _client is None:
        api_key = os.getenv('GROQ_API_KEY')

        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Now we will create this Groq LLM client here to use the groq LLM actually
        # Instantiates the Groq client using the API key. Stores it in _client for reuse.
        _client = Groq(api_key=api_key)

    return _client



# This defines how our system i.e LLM should behave before it receives the data
# It contains instructions that will be sent to the LLM (Groq, GPT, etc.) as the system role prompt. This sets the behavior of the model before it sees any user input.
RESUME_SYSTEM_PROMPT = (
    "You are a resume parser. Extract information from the resume "
    "and return ONLY a valid JSON object. No explanation, no markdown."
)


# Here this is the user prompt which user is giving to LLM. So that LLM works in the given way only for the input data & also give output in this given JSON object only
# This line defines the user prompt that will be sent to the LLM (Groq, GPT, etc.) along with the raw resume text. It’s essentially the instruction template telling the model exactly what structured information to extract and how to format it.
# It uses triple quotes (""") so the prompt can span multiple lines.
# In Python, when you use f‑strings or .format(), single curly braces { } are placeholders for variables.
# But sometimes you want to include literal curly braces in your string (for example, when showing a JSON schema).
# To escape them, you use double curly braces {{ }}. Python will render them as single { } in the final string.
# Without doubling them, Python would think {} is a variable placeholder and try to substitute something.
# e.g template = "Here is JSON: {{ 'key': 'value' }}", then  Output: Here is JSON: { 'key': 'value' }
# here along with the prompt, we will also pass the raw_text which we get from resume_parser inside the placeholder {} here
RESUME_USER_PROMPT = """Extract the following from this resume and return as JSON:
{{
    "name": "full name",
    "email": "email address",
    "phone": "phone number",
    "linkedin": "LinkedIn URL if present, otherwise null",
    "github": "GitHub URL if present, otherwise null",
    "professional_summary": "the full text of the Summary, Profile, About Me, Objective, or Professional Summary section at the top of the resume. Copy the ENTIRE paragraph exactly as written. If no such section exists, return an empty string.",
    "skills": ["list", "of", "skills"],

    "experience": [
    {{
        "job_title": "",
        "company": "",
        "start_date": "",
        "end_date": "",
        "duration_months": 0,
        "description": ""
    }}
    ],

    "education": [
    {{
        "degree": "",
        "institution": "",
        "year": ""
    }}
    ],

    "certifications": ["list of certifications"],

    "projects": [
    {{
        "title": "project name",
        "description": "what the project does and how it was built",
        "technologies": ["tech", "used"]
    }}
    ],

    "action_verbs": ["strong action verbs used in bullet points, e.g. developed, implemented, designed"],
    "keywords": ["important keywords and phrases from the resume for ATS matching"]
}}

Important instructions:
- For duration_months, calculate the number of months between start_date and end_date. If end_date is "Present" or "Current", calculate from start_date to now.
- For skills, extract ALL technical and soft skills mentioned anywhere in the resume.
- For action_verbs, find verbs that start bullet points or describe achievements.
- For keywords, extract noun phrases and technical terms relevant to ATS matching.
- Return ONLY valid JSON. No markdown code fences, no explanation.

Resume Text:
{raw_text}"""



# SO we will perform the actual Groq API calling using this fn
# This function is the core wrapper that actually calls the Groq LLM to parse resumes (or perform any structured task).
# client: Groq → The Groq client object (already initialized with API key).
# Return type: str → Returns the model’s output as plain text (in this case, JSON).
def _call_groq(client: Groq, system_prompt: str, user_prompt: str) -> str:

    response = client.chat.completions.create(
        model=GROQ_MODEL, 
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.0,
        max_tokens=4096       # which is roughly around 3000 words
    )

    # response.choices[0] → Takes the first generated completion.
    # .message.content → Extracts the actual text output (the JSON string).
    # .strip() → Removes leading/trailing whitespace, ensuring clean JSON.
    return response.choices[0].message.content.strip()

# client.chat.completions.create(...) :-
# Calls Groq’s API to generate a chat completion.
# Similar to OpenAI’s ChatCompletion.create.
# Parameters:
# model=GROQ_MODEL → The specific Groq LLM you want to use (e.g., "llama-3.3-70b-versatile").
# messages=[...] → Defines the conversation context:
# system → Sets the role/behavior (resume parser).
# user → Provides the actual resume text + extraction instructions.
# temperature=0.0 → Makes output deterministic (no randomness). Perfect for structured JSON.
# max_tokens=4096 → Limits the length of the output. Ensures large resumes can be parsed fully.

# Response object :-
# Groq returns a structured response with multiple choices (like OpenAI).
# Each choice contains a message with role and content.




# This function is a helper utility that tries to safely convert a string into a Python dictionary by parsing it as JSON.
# text: str → A string that is expected to contain JSON (for example, the LLM’s output).
# Return tyep :- dict | None → Either a Python dictionary (if parsing succeeds) or None (if parsing fails).
def _try_parse_json(text: str) -> dict | None:
    # Strip markdown code fences if present
    cleaned = text.strip()   # .strip() removes leading/trailing whitespace.

    # LLMs often wrap JSON in markdown fences like: 
    # ```json
    # { "name": "Arpit" }
    # ```
    if cleaned.startswith("```"):
        # Remove opening fence
        # If the text starts with triple backticks (```), it finds the first newline. Everything after that newline is kept (removing the opening fence).
        # If cleaned = "```json\n{ \"name\": \"Arpit\" }\n```", Then cleaned[first_newline+1:] → "{ \"name\": \"Arpit\" }\n```"
        first_newline = cleaned.index("\n") if "\n" in cleaned else len(cleaned)
        
        cleaned = cleaned[first_newline + 1 : ]

        # Remove closing fence
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]    # means: take the string cleaned and return everything except the last 3 characters.

        cleaned = cleaned.strip()

    try:
        # json.loads(...) is Python’s built‑in method to convert a JSON string into a Python dictionary.
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # If the string is not valid JSON (e.g., malformed, missing quotes, trailing commas), json.loads raises a JSONDecodeError.
        # Instead of crashing the program, the function catches this error. And It then returns None to signal “parsing failed.”
        return None



# This function parse_resume is the main orchestrator of your resume parsing pipeline. It ties together the Groq client, the system/user prompts, JSON parsing, error handling, and validation.
# It takes raw_text → the resume text (plain string) which is get from resume_parser file.
# Output: A Python dictionary (Dict) containing structured resume data (name, skills, experience, etc.).
def parse_resume(raw_text: str) -> Dict:
    client = _get_client()

    # Fills the RESUME_USER_PROMPT template with the actual resume text. This creates a complete instruction string for the LLM, including the JSON schema and the resume content.
    prompt = RESUME_USER_PROMPT.format(raw_text=raw_text)

    # Returns the raw output (expected to be JSON).
    raw_response = _call_groq(client, RESUME_SYSTEM_PROMPT, prompt)

    # Attempts to parse the raw response into a Python dictionary. If parsing succeeds → result is a dict. If parsing fails → result is None.
    result = _try_parse_json(raw_response)

    if result is not None:
        return _validate_resume_result(result)

    logger.warning("Groq resume parse: first attempt returned invalid JSON, retrying...")

    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt
    )

    raw_response = _call_groq(client, RESUME_SYSTEM_PROMPT, strict_prompt)

    result = _try_parse_json(raw_response)

    if result is not None:
        return _validate_resume_result(result)

    raise ValueError(
        # If parsing still fails → raises a ValueError with the first 500 characters of the raw response for debugging.
        f"Groq returned unparseable response after retry. Raw response:\n{raw_response[:500]}"
    )




# This defines how our system i.e LLM should behave before it receives the data of JD
# It contains instructions that will be sent to the LLM (Groq, GPT, etc.) as the system role prompt. This sets the behavior of the model before it sees any user input JD.
JD_SYSTEM_PROMPT = (
    "You are a job description parser. Extract information and "
    "return ONLY a valid JSON object. No explanation, no markdown."
)



# Here this is the user prompt which user is giving to LLM. So that LLM works in the given way only for the input data & also give output in this given JSON object only
# This line defines the user prompt that will be sent to the LLM (Groq, GPT, etc.) along with the raw resume text. It’s essentially the instruction template telling the model exactly what structured information to extract and how to format it.
# It uses triple quotes (""") so the prompt can span multiple lines.
# In Python, when you use f‑strings or .format(), single curly braces { } are placeholders for variables.
# But sometimes you want to include literal curly braces in your string (for example, when showing a JSON schema).
# To escape them, you use double curly braces {{ }}. Python will render them as single { } in the final string.
# Without doubling them, Python would think {} is a variable placeholder and try to substitute something.
# e.g template = "Here is JSON: {{ 'key': 'value' }}", then  Output: Here is JSON: { 'key': 'value' }
# here along with the prompt, we will also pass the raw_text which we get from resume_parser inside the placeholder {} here
JD_USER_PROMPT = """Extract the following from this job description and return as JSON:
{{
  "job_title": "",
  "required_skills": ["list of must-have skills"],
  "preferred_skills": ["list of nice-to-have skills"],
  "experience_required": "",
  "education_required": "",
  "key_responsibilities": ["list of responsibilities"],
  "keywords": ["important keywords and phrases for ATS matching"]
}}

Important instructions:
- required_skills: skills explicitly stated as required or must-have.
- preferred_skills: skills stated as preferred, nice-to-have, or bonus.
- keywords: extract ALL important terms an ATS system would match against, including skills, technologies, certifications, and domain terms.
- Return ONLY valid JSON. No markdown code fences, no explanation.

Job Description Text:
{raw_text}"""




# This function parse_job_description is the job description counterpart to our parse_resume pipeline. It follows the same structure but is tailored to extracting structured information from a job description.
def parse_job_description(raw_text: str) -> Dict:
    client = _get_client()

    prompt = JD_USER_PROMPT.format(raw_text=raw_text)

    raw_response = _call_groq(client, JD_SYSTEM_PROMPT, prompt)

    result = _try_parse_json(raw_response)

    if result is not None:
        return _validate_jd_result(result)

    logger.warning("Groq JD parse: first attempt returned invalid JSON, retrying...")
    
    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt
    )

    raw_response = _call_groq(client, JD_SYSTEM_PROMPT, strict_prompt)

    result = _try_parse_json(raw_response)

    if result is not None:
        return _validate_jd_result(result)

    raise ValueError(
        f"Groq returned unparseable response after retry. Raw response:\n{raw_response[:500]}"
    )



#it will make sure, that the parse json has all the valid fields we expect
# Output: A cleaned dictionary with guaranteed keys and valid types.
def _validate_jd_result(result: dict) -> dict:
    # This dictionary defines the expected schema for a job description.
    # These defaults values act as fallbacks if the LLM output is missing or invalid.
    defaults = {
        "job_title": "",
        "required_skills": [],
        "preferred_skills": [],
        "experience_required": "",
        "education_required": "",
        "key_responsibilities": [],
        "keywords": [],
    }

    for key, default in defaults.items():
        # If the key doesn’t exist in result, or its value is None, set it to the default. Example: If Groq forgot "preferred_skills", it gets added as [].
        if key not in result or result[key] is None:
            result[key] = default

        # If the default is a list (e.g., required_skills) but the value in result isn’t a list, reset it to the default. Example: If Groq mistakenly outputs "required_skills": "Python, FastAPI" (string instead of list), this code replaces it with [].
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default

    return result




# To make sure the parse json has all the valid json fields
def _validate_resume_result(result: dict) -> dict:
    defaults = {
        "name": "",
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "professional_summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
        "action_verbs": [],
        "keywords": [],
    }

    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
            
        # Ensure list fields are actually lists
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default

    #Validate experience entries
    for exp in result.get("experience", []):
        # If an entry isn’t a dictionary (e.g., Groq mistakenly outputs a string), skip it. Prevents runtime errors
        if not isinstance(exp, dict):
            continue

        # dict.setdefault(key, default) → ensures the key exists. If the key is missing, it adds it with the default value.
        # So it only Set default values for missing keys
        exp.setdefault("job_title", "")
        exp.setdefault("company", "")
        exp.setdefault("start_date", "")
        exp.setdefault("end_date", "")
        exp.setdefault("duration_months", 0)
        exp.setdefault("description", "")


        #Ensure duration_months is an int
        try:
            exp["duration_months"] = int(exp["duration_months"])
        except (ValueError, TypeError):
            # If it fails (e.g., "five months" or None), sets it to 0.
            exp["duration_months"] = 0

    # Validate project entries
    for proj in result.get("projects", []):
        if not isinstance(proj, dict):
            continue

        proj.setdefault("title", "")
        proj.setdefault("description", "")
        proj.setdefault("technologies", [])

    return result







#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Tokenization in NLP :- 
# Tokenization in NLP is the process of breaking text into smaller units called tokens (words, subwords, or characters), which are the fundamental building blocks for analysis and model training. It’s the first and most critical step in preparing text for tasks like classification, sentiment analysis, or language modeling.
# e.g “Tokenization is crucial for NLP.” → ["Tokenization", "is", "crucial", "for", "NLP", "."]


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# NER in NLP :-
# Named Entity Recognition (NER) in NLP is the task of automatically identifying and classifying entities in text—such as names of people, organizations, locations, dates, and more—into predefined categories. It transforms unstructured text into structured information, making it essential for applications like search engines, chatbots, and information extraction.
# Input: “Arpit Pal studies at Manipal Institute of Technology in Bengaluru.”  
# Output: Arpit Pal → PERSON
# Manipal Institute of Technology → ORGANIZATION
# Bengaluru → LOCATION


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Embeddings And cosine similarity :- 
# An embedding is a numerical vector representation of text (word, sentence, or document).
# Captures semantic meaning so that similar texts have similar vectors.
# So we will use Transformer models (BERT, SentenceTransformers) to create them.

# Cosine Similarity is a metric to measure how similar two vectors are, based on the angle between them.
# 1 → vectors point in the same direction (high similarity).
# 0 → vectors are orthogonal (no similarity).
# -1 → vectors point in opposite directions (rare in embeddings).
# cosine similarity(𝐴,𝐵) = (𝐴 ⋅ 𝐵) / ∥ 𝐴 ∥ ⋅ ∥ 𝐵 ∥


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# singelton patter in GROQ :-
# The Singleton Pattern in the context of your Groq client creation means: only one instance of the Groq client will ever exist in your application, and all parts of your code will reuse that same instance.

# Why Singleton for Groq Client? :-
# Avoid multiple connections → Creating a new client for every request wastes resources and can hit API limits.
# Consistency → All requests share the same configuration (API key, base URL, etc.).
# Performance → Reusing one client avoids repeated initialization overhead.
# Centralized control → Easier to manage retries, logging, and error handling.


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
