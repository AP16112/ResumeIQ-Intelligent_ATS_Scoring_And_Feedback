# here inside this models folder, we will create this schemas.py file to define the Pydantic models for our project.
# Pydantic is a data validation and settings management library for Python, based on type annotations. It allows us to define data models with type hints and provides automatic validation and parsing of data.

# So how we want to send data to api endpoints & how we want to receive data from api endpoints, that format or structure of data is defined in this schemas.py file using Pydantic models. This way we can ensure that the data we are sending and receiving is in the correct format and type.

# here we are defining the Pydantic models for the request and response data for our API endpoints. For example, we can define a model for the resume analysis request which will contain the resume text and job description text, and we can also define a model for the resume analysis response which will contain the ATS score, feedback, and recommendations. This way we can ensure that the data we are sending to the API endpoints is in the correct format and type, and also we can ensure that the data we are receiving from the API endpoints is in the correct format and type. This will help us to avoid any errors or issues related to data validation and parsing in our application.
# here we are importing the necessary libraries and modules for our Pydantic models. We will use the BaseModel class from Pydantic to define our data models, and we will also import the necessary types like Any, Dict, List, Optional from the typing module to define the types of our data fields in the models. This way we can ensure that our data models are well-defined and we can easily validate and parse the data using these models in our API endpoints.
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
# pydantic is a data validation and settings management library for Python. It uses Python type annotations to validate and parse data. It is used in FastAPI to define the structure of the request and response data.
# pydantic is a python module which is used to validate the requests.
# Like here we want the input text which is coming from the user to be in a specific format, so we will use pydantic to define that format and validate the input data.


class ComponentScores(BaseModel):
    formatting: float
    keywords: float
    content: float
    skill_validation: float
    ats_compatibility: float

# BaseModel: Comes from Pydantic. It’s used to define data models with type validation.
# Class ComponentScores: Represents a structured object that holds different scoring components.
# Attributes:
# formatting: float → score for resume formatting
# keywords: float → score for keyword usage/matching
# content: float → score for overall content quality
# skill_validation: float → score for skills matching/validation
# ats_compatibility: float → score for ATS (Applicant Tracking System) compatibility
# Each field is typed as float, meaning Pydantic will enforce that values must be numbers (e.g., 0.0–1.0 or 0–100 depending on your scoring system).

# Why use this :-
# Validation: If you pass invalid data (like a string instead of a float), FastAPI will automatically reject it with a clear error.
# Serialization: It can easily convert to JSON for API responses:
# {
#   "formatting": 0.85,
#   "keywords": 0.92,
#   "content": 0.78,
#   "skill_validation": 0.80,
#   "ats_compatibility": 0.90
# }


# This class is another Pydantic model that defines the structure of data returned when comparing a resume against a job description (JD)
class JDComparison(BaseModel):
    match_percentage: float
    semantic_similarity: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    skills_gap: List[str]


# This class is another Pydantic model that structures how your API represents the results of skill validation in a resume analysis
class SkillValidationDetails(BaseModel):
    validated: List[Dict[str, Any]] = []      # [{'skill': str, 'projects': [str]}]
    unvalidated: List[str] = []             # ['Flask', 'A/B Testing', ...]
    total: int = 0
    validated_count: int = 0
    validated_pct: float = 0.0

# Here this validated: List[Dict[str, Any]] :-
# A list of dictionaries, each representing a skill that was successfully validated.
# Example entry: {"skill": "Python", "projects": ["ResumeIQ", "AttendifyX"]}
# This shows not only the skill but also the projects where it was demonstrated.


# This class defines a Pydantic model that structures how your system represents issues found in a resume analysis, especially with respect to ATS (Applicant Tracking System) compatibility
class IssueDetail(BaseModel):
    issue_title: str
    severity_level: str     # like "critical", "high", "medium", "low". SO based on that we can decide priority of fixing that issue. Like critical issues should be fixed first, then high, then medium, and then low.
    ats_impact: str
    explanation: str
    where_it_appears: str
    how_to_fix: str
    action_items: List[str] = []     # here currently we are taking this as empty list, but when we will implement the logic for this, then we will populate this list with the actual action items for each issue.
    example_improvement: str

# Here action_items: List[str] = [] :-
# A list of concrete steps the user can take.
# Example: ["Remove table formatting", "Use consistent bullet points"]

# # example_improvement: str :-  
# Shows a sample corrected version for clarity.
# Example: "Bachelor of Technology, Computer Science (2019–2023)"


# This class defines the main response schema for your resume analysis API. It’s a Pydantic model that aggregates all the different components we’ve been building (ComponentScores, IssueDetail, JDComparison, SkillValidationDetails) into one unified structure
class AnalysisResponse(BaseModel):
    ATS_score: float      # Overall score for the resume’s ATS compatibility
    component_scores: ComponentScores    # Breakdown of scores (formatting, keywords, content, etc.).
    issues_summary: List[str]         # A high-level summary of the main issues found in the resume.
    detailed_feedback: List[IssueDetail]      # A list of detailed feedback items, each describing a specific issue with the resume and how to fix it.
    jd_match_analysis: Optional[JDComparison] = None
    # Here Optional means that this field may or may not be present in the response. When it is present, it will contain a JDComparison object with details about how well the resume matches the job description. If it is not present, it means that the JD comparison was not performed or there was an issue with it, and the API will simply omit this field from the response. And we are currently setting it to None by default, which means that if we don't provide any value for this field, it will be None. This way we can handle cases where the JD comparison is not applicable or not performed without causing errors in our API response.
    skill_validation_details: Optional[SkillValidationDetails] = None
    # here This is also optional because we may not always perform skill validation in every analysis, or there may be cases where skill validation is not applicable. By making it optional, we can ensure that our API response remains flexible and can accommodate different scenarios without breaking the structure of the response. If skill validation is performed, this field will contain a SkillValidationDetails object with the results; if not, it will simply be omitted from the response.
    

    ats_score: float
    keyword_match: float = 0.0
    missing_keywords: List[str] = []
    matched_keywords: List[str] = []
    suggestions: List[str] = []
    strengths: List[str] = []
    critical_issues: List[str] = []       # High‑priority problems.
    skills: List[str] = []
    jd_comparison: Optional[JDComparison] = None
    warnings: List[str] = []
    interpretation: str = ""     # Narrative explanation of the analysis.


# SO Pydantic actually performs 3 things i.e firstly validate input type & then convert it into JSON serializable format & then also provide documentation for the API endpoints using the defined models. So by defining these Pydantic models, we can ensure that our API endpoints are well-structured, validated, and documented, which will help us to build a robust and user-friendly API for our resume analysis application.
