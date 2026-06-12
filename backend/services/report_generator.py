# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'report_generator.py' file to provide the user with the pdf report to improve the resume
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.


# Loads Python’s built‑in OS (Operating System) module. Provides functions for interacting with the operating system:
# File and directory operations (os.path, os.makedirs, os.remove)
# Environment variables (os.getenv, os.environ)
# Process management (os.system, os.getpid)
import os

from datetime import datetime

# Here we are importing two key components from the Jinja2 templating engine
from jinja2 import Environment, FileSystemLoader
# Jinja2 :- Jinja2 is a powerful templating engine for Python, often used with frameworks like Flask.
# It allows you to write HTML templates with placeholders ({{ variable }}) and logic ({% for item in list %}).
# Environment :- The central object in Jinja2.
# It manages:
# Template loading
# Global variables
# Filters and extensions
# Think of it as the “workspace” where templates live and are rendered.
# FileSystemLoader :- A loader that tells Jinja2 where to find template files on your filesystem.
# You pass it a directory path (e.g., "templates").
# When you call get_template("index.html"), Jinja2 looks inside that folder.


## here we are importing this Dict from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import Dict


# Here we are setting up where Jinja2 should look for templates and creating the environment to load them
# os.path.dirname(__file__) :- __file__ is a special variable in Python that holds the path of the current file.
# os.path.dirname(__file__) → gets the directory containing the current Python script.
# Example: If your script is at /home/user/project/src/app.py, then this returns /home/user/project/src.
# os.path.join(..., '..', 'templates') :- Joins paths safely across operating systems.
# '..' means “go up one directory” (the parent folder).
# 'templates' is the folder name where your HTML templates are stored.
# So if your script is in /home/user/project/src/app.py, this resolves to: /home/user/project/templates.
# Final result: TEMPLATE_DIR points to the templates folder relative to your script.
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
# Environment(loader=FileSystemLoader(TEMPLATE_DIR)) :- Creates a Jinja2 environment.
# FileSystemLoader(TEMPLATE_DIR) tells Jinja2 to load templates from the templates directory.
# With this environment, you can fetch and render templates dynamically.
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))



# This function is a date formatter utility — it takes an ISO‑style timestamp string and converts it into a human‑readable format.
def format_date(value, fmt='%B %d, %Y at %I:%M %p'):
    """Convert ISO timestamp string → human-readable date string."""
    if not value:
        return ''
    
    try:
        # ISO timestamps often end with "Z" (Zulu time = UTC).
        # datetime.fromisoformat doesn’t understand "Z", so it’s replaced with "+00:00" (UTC offset).
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        # Converts the datetime object into a string using the format specified.
        # Example: "2026-06-12T09:53:00Z" → "June 12, 2026 at 09:53 AM".
        return dt.strftime(fmt)
    except Exception:
        return value     # If parsing fails (e.g., invalid timestamp string), return the original value unchanged.
    
# value: the timestamp string (usually ISO 8601 format, e.g., "2026-06-12T09:53:00Z").
# fmt: optional format string for output. Default is '%B %d, %Y at %I:%M %p'.
# %B → full month name (e.g., June)
# %d → day of the month (e.g., 12)
# %Y → 4‑digit year (e.g., 2026)
# %I:%M %p → 12‑hour time with AM/PM (e.g., 09:53 AM)
# So the default output looks like: "June 12, 2026 at 09:53 AM".



# This line is registering a custom filter in Jinja2 so you can use your format_date function directly inside templates
env.filters['format_date'] = format_date
# env.filters :- env is your Jinja2 Environment object (created earlier with Environment(loader=FileSystemLoader(...))).
# .filters is a dictionary where you can register custom functions that templates can call as filters.
# Jinja2 already has built‑in filters (like upper, lower, replace), but you can add your own.
# This means whenever you use | format_date in a template, Jinja2 will call your Python function with the value being piped in.


# This function is meant to generate HTML reports from structured analysis data.
# analysis_data: Dict → a dictionary containing structured resume analysis results (scores, issues, recommendations, etc.).
def generate_html_reports(analysis_data: Dict) -> Dict[str, str]:
    # Extract timestamp :- 
    # datetime.now() :- Gets the current local date and time from your system clock. Example: datetime(2026, 6, 12, 10, 02, 15, 123456) → represents June 12, 2026, 10:02:15.123456 AM.
    # .isoformat() :- Converts the datetime object into a string using the ISO 8601 standard. ISO 8601 is a widely used format for timestamps in APIs, databases, and logs.
    # Default output includes:
    # Date (YYYY-MM-DD)
    # Time (HH:MM:SS)
    # Fractional seconds (microseconds) if present
    # Example: "2026-06-12T10:02:15.123456"
    now = datetime.now().isoformat()

    # Overall score + interpretation :-
    overall_score = analysis_data.get('ATS_score', 0) or analysis_data.get('ats_score', 0)
    interpretation = analysis_data.get('interpretation') or ''

    cs = analysis_data.get('component_scores') or {}

    # Checks if cs has a __dict__ attribute. Why? Because if component_scores was stored as a Pydantic model object (like ComponentScores), it won’t be a plain dictionary.
    # Pydantic models (and many Python objects) store their fields in .__dict__.
    # cs = cs.__dict__ :- Converts the object into a plain dictionary by accessing its internal __dict__.
    # This makes it easier to serialize into JSON or pass around without worrying about object methods.
    if hasattr(cs, '__dict__'):      # handle Pydantic model objects
        cs = cs.__dict__


    component_scores = {
        'formatting': float(cs.get('formatting', 0)),
        'keywords':  float(cs.get('keywords', 0)),
        'content': float(cs.get('content', 0)),
        'skill_validation': float(cs.get('skill_validation', 0)),
        'ats_compatibility': float(cs.get('ats_compatibility', 0)),
    }

    # Progress-bar percentages (used in Report 1's visual breakdown) :-
    def pct(score, max_score):
        return min(100, max(0, round(score / max_score * 100)))


    component_pct = {
        'formatting':  pct(component_scores['formatting'], 20),
        'keywords': pct(component_scores['keywords'], 25),
        'content': pct(component_scores['content'], 25),
        'skill_validation': pct(component_scores['skill_validation'], 15),
        'ats_compatibility': pct(component_scores['ats_compatibility'], 15),
    }

    raw_feedback = analysis_data.get('detailed_feedback', [])

    # Normalise: each item may be a dict or an IssueDetail Pydantic object :-
    # This helper function is designed to normalize items so that whether they’re already dictionaries or Pydantic model objects, you always end up with a plain dictionary representation
    def to_dict(item):
        if isinstance(item, dict):
            return item    # If the item is already a dictionary, just return it as‑is.
        
        # item.model_dump() :- If the item is a Pydantic model (like IssueDetail), it usually has a .model_dump() method.
        # This method converts the model into a dictionary with all its fields.
        # If the object doesn’t have .model_dump(), fall back to its __dict__.
        # __dict__ is a built‑in attribute that stores an object’s fields as a dictionary.
        return item.model_dump() if hasattr(item, 'model_dump') else item.__dict__
    

    detailed_feedback = [to_dict(fb) for fb in raw_feedback]

    high_priority   = [fb for fb in detailed_feedback if fb.get('severity_level', '').lower() in ('high')]
    
    medium_priority = [fb for fb in detailed_feedback if fb.get('severity_level', '').lower() in ('moderate', 'medium')]
    
    low_priority    = [fb for fb in detailed_feedback if fb.get('severity_level', '').lower() in ('low', 'info')]

    strengths = analysis_data.get('strengths', [])

    svd_raw = analysis_data.get('skill_validation_details') or {}
    
    if hasattr(svd_raw, 'model_dump'):
        svd_raw = svd_raw.model_dump()


    validated_skills = svd_raw.get('validated', [])    # [{'skill', 'projects'}]
    unvalidated_skills = svd_raw.get('unvalidated', [])  # ['Flask', ...]
    total_skills = svd_raw.get('total', len(validated_skills) + len(unvalidated_skills))
    validated_count = svd_raw.get('validated_count', len(validated_skills))
    validation_pct = svd_raw.get('validation_pct', 0.0)

    # JD comparison (for Report 3) :-
    jd_raw = analysis_data.get('jd_match_analysis') or analysis_data.get('jd_comparison')
    
    if hasattr(jd_raw, 'model_dump'):
        jd_raw = jd_raw.model_dump()


    # Score colour (green / orange / red) :-
    if overall_score >= 80:
        score_color = '#16a34a'   # green
    elif overall_score >= 60:
        score_color = '#d97706'   # amber
    else:
        score_color = '#dc2626'   # red


    # Build shared context dict passed to every template :-
    context = {
        'timestamp':   now,
        'overall_score': overall_score,
        'score_color':  score_color,
        'interpretation': interpretation,
        'component_scores': component_scores,
        'component_pct': component_pct,
        'strengths': strengths,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'all_feedback':  detailed_feedback,
        # Skill validation
        'validated_skills': validated_skills,
        'unvalidated_skills': unvalidated_skills,
        'total_skills':  total_skills,
        'validated_count': validated_count,
        'validation_pct': validation_pct,
        # JD analysis
        'jd_analysis': jd_raw,
    }

    # Here we are returning a dictionary of rendered HTML reports, each generated from a different Jinja2 template
    # env.get_template('...') :- Uses the Jinja2 environment (env) to load a specific HTML template file. Example: summary.html, action_items.html, etc. These templates live in your templates directory.
    # .render(**context) :- Renders the template into a final HTML string.
    # context is a dictionary of data passed into the template (e.g., scores, issues, recommendations).
    # The **context syntax unpacks the dictionary so template variables can be accessed directly.
    # Example: if context = {"ats_score": 85}, then inside the template you can use {{ ats_score }}.
    return {
        'summary':  env.get_template('summary.html').render(**context),
        'skill_report': env.get_template('action_items.html').render(**context),
        'jd_report':  env.get_template('quick_actions.html').render(**context),
        'recommendations': env.get_template('jd_comparison.html').render(**context),
    }