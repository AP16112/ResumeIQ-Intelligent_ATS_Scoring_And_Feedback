# Here in this folder, we will create different files which will contain the core logic or business logicof our project. 
# Like here we have created this 'ats_scorer.py' file to write the logic of our ATS Scoring system. This file will contain the code to calculate the ATS score for a given resume and job description. This way we can keep our code organized and modular. We can also create other files for different functionalities like feedback_engine, pdf_export, resume_analyzer, etc. This way we can keep our code clean and maintainable.
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.

# SO in this file, we will write the logic of ATS Score engine actually


# It is Python’s built‑in regular expressions module. Allows you to search, match, and manipulate text patterns.
# e.g text = "Hello, world!" then, words = re.split(r'\W+', text). print(words)  # ['Hello', 'world', '']
import re  

# Imports the spaCy library, a powerful NLP (Natural Language Processing) toolkit. Helps with tasks like tokenization, part‑of‑speech tagging, named entity recognition (NER), and dependency parsing.
import spacy
import numpy as np

# SentenceTransformer (from sentence-transformers) :- A class that loads pre‑trained transformer models (like BERT variants) specialized for generating sentence embeddings.
# Embeddings = numerical vector representations of text that capture semantic meaning.
# model = SentenceTransformer('all-MiniLM-L6-v2')    # it will load this BERT model
# embedding = model.encode("I love playing cricket")
from sentence_transformers import SentenceTransformer

# here we are importing this Dict, List, Optional, Tuple  from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import Dict, List, Optional, Tuple


from backend.utils.file_utils import log_warning

# Now if we want to use the fine tune BERT model here, we can simply do that also by simply changing the value of this SENTENCE_TRANSFORMER_MODEL inside config file by the fine tune BERT model 
from backend.core.config import SENTENCE_TRANSFORMER_MODEL       
# SO here we will use our own fine tune BERT model actually here

from backend.utils.matching import fuzzy_match_keywords


# This line defines a regular expression pattern for matching U.S. ZIP codes:
# r'...' → Raw string literal in Python. It tells Python not to treat backslashes as escape characters, so \b means "word boundary" instead of \\b.
# \b → Word boundary. Ensures the ZIP code is matched as a standalone unit, not inside a longer string.
# \d{5} → Exactly five digits (the standard 5‑digit ZIP code).
# (?:-\d{4})? → A non‑capturing group:
# - → A literal hyphen.
# \d{4} → Exactly four digits (the ZIP+4 extension).
# ? → Makes the whole group optional (so both 5‑digit and 9‑digit ZIP codes are valid).
# \b → Another word boundary at the end.
# What it matches: ✅ 12345 (basic ZIP code), ✅ 12345-6789 (ZIP+4 format), ❌ 123456 (too many digits), ❌ 1234 (too few digits)
ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'


# That regex pattern is designed to match street addresses in a fairly standard U.S. format:
# \b → Word boundary, ensures the match starts at a clean boundary.
# \d+ → One or more digits (the street number, e.g. 123). \s+ → One or more spaces.
# [A-Z][a-z]+ → A capitalized word (e.g. Main, Elm).
# (?:\s+[A-Z][a-z]+)* → Zero or more additional capitalized words (e.g. New York → New + York).
# \s+ → Space before the street type.
# (?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl) → Matches common street suffixes.
# \b → Word boundary at the end.
# Examples it matches:✅ 123 Main Street, ✅ 456 Elm Rd, ✅ 789 New York Avenue, ✅ 42 Sunset Blvd
STREET_ADDRESS_PATTERN = (
    r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+'
    r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
)

# Here we have define these regex patterns at the front only & not in functions because they regex patters needs compilations.
# And if we add them in functions, & 100 users are using our app in 1 hour, then they gets compiled 100 times, which increases load on our server
# So that's why we are defining them at the front only outside the functions so they gets compiled once when app started & then later we will directly used these compiled regex expressions directly inside functions.




# n: float → The input value you want to evaluate (like a score or metric).
# tiers: list → A list of tuples i.e (threshold, points) pairs. Each pair defines:
# threshold: the minimum value required.
# pts: the score/points awarded if n meets that threshold.
def _tier_score(n: float, tiers: list)-> float:
    for threshold, pts in tiers:
        if n >= threshold:
            return pts
    #This means the function gives the points for the first threshold that n meets or exceeds. If no thresholds are met, return 0.0.
    
    return 0.0




# Location/privacy detection :-
# THis fn will be used to find location-related information (like cities, countries, addresses) inside a given text.
# nlp: spacy.Language → A spaCy language model object (e.g., en_core_web_sm) used to process the text.
def detect_location_info(text: str, nlp: spacy.Language) -> Dict:
    locations = []

    # method 1: spacy NER
    # Passes the input string text into the spaCy NLP pipeline (nlp). This produces a Doc object containing tokens, part‑of‑speech tags, and named entities.
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            # ent.start_char (character index where it begins).
            locations.append({'text': ent.text, 'type': ent.label_.lower(), 'start': ent.start_char})
            # 'start': ent.start_char → The character position in the original text where the location starts.

    # method 2: street address regx
    # re.finditer(...) :- Searches through the string text for all matches of the regex pattern STREET_ADDRESS_PATTERN. Unlike findall, finditer returns an iterator of match objects, which contain detailed info about each match (like position, groups, etc.).
    # re.IGNORECASE makes the search case‑insensitive (so it matches Main Street or main street).
    # for match in re.finditer(...) :- Loops through each match object found in the text.
    # match.group() :- Returns the actual substring that matched the regex (e.g., "123 Main Street").
    # match.start() :- Returns the starting character index of the match in the original text. Useful for locating where the address appears.
    for match in re.finditer(STREET_ADDRESS_PATTERN, text, re.IGNORECASE):
        locations.append({'text': match.group(), 'type': 'address', 'start': match.start()})


    # method 3: ZIP/PIN CODE REGEX PATTERN
    # It is using a regex pattern to detect ZIP codes (or PIN codes, if adapted for India) in text.
    # re.finditer(ZIP_CODE_PATTERN, text) :- Scans the string text for all matches of the regex ZIP_CODE_PATTERN. finditer returns an iterator of match objects, each containing details about the match (like the matched text and its position).
    # Example pattern: ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'. This matches U.S. ZIP codes in 5‑digit or ZIP+4 format.
    # match.group() :- Returns the actual substring that matched the regex (e.g., "90210" or "12345-6789").
    for match in re.finditer(ZIP_CODE_PATTERN, text):
        locations.append({'text': match.group(), 'type': 'zip', 'start': match.start()})

    # Here we are using these 3 methods & all 3 are actually needed because each method catches something which other methods misses.

    # THis line is a boolean check to see if any of the extracted locations are of type "address"
    # any(...) :- Returns True if at least one of the items in the generator expression is True. Returns False if none of them match.
    has_address = any(loc['type'] == 'address' for loc in locations)
    has_zip  = any(loc['type'] == 'zip' for loc in locations)


    # Now if address and zip code also present other then location in resume, then we will apply penalty & raise privacy risk
    if has_address and has_zip:    # If both a street address and a ZIP/PIN code are present → this is considered the highest privacy risk.
        privacy_risk, penalty = 'high', 5.0
    elif has_address or has_zip:    # If either an address or a ZIP/PIN code is present (but not both) → still high risk, but slightly lower.
        privacy_risk, penalty = 'high', 4.0
    elif len(locations) > 3:   # If more than 3 location entities (cities, countries, landmarks, etc.) are detected → considered medium risk.
        privacy_risk, penalty = 'medium', 3.0
    elif locations:     # If at least one location entity exists (but not enough to trigger higher rules) → considered low risk.
        privacy_risk, penalty = 'low', 2.0
    else:
        privacy_risk, penalty = 'none', 0.0

    
    recommendations = []

    if not locations:
        recommendations.append(" No privacy concerns detected.")
    if has_address:
        recommendations.append(" Remove full street addresses — ATS systems don't need this and it's a privacy risk.")
    if has_zip:
        recommendations.append(" Remove zip codes — this level of location detail is unnecessary.")
    if privacy_risk in ('low', 'medium') and not has_address and not has_zip:
        recommendations.append(" Consider reducing location mentions. 'City, State' in the contact header is sufficient.")

    return {
        'location_found':     len(locations) > 0,
        'detected_locations': locations,
        'privacy_risk':       privacy_risk,
        'recommendations':    recommendations,
        'penalty_applied':    penalty,
    }




# It is a utility function to measure how semantically similar skill is to a text using embeddings.
# embedder: SentenceTransformer → a pre‑trained or fine‑tuned SentenceTransformer model that can convert text into embeddings.
# So here type of this embedder is SentenceTransformer model actually. so in this embedder, we will store our fine tune model.
# This function is computing the semantic similarity between a skill (like "Python") and a text (like a resume or job description) using embeddings from a SentenceTransformer model
def _calculate_semantic_similarity(skill: str, text: str, embedder: SentenceTransformer) -> float:
    # similarity = (A · B) / (|A| × |B|)
    if not skill or not text:
        return 0.0
    

    try:
        skill_vec  = embedder.encode(skill, convert_to_tensor=False)
        text_vec   = embedder.encode(text,  convert_to_tensor=False)

        # Computes cosine similarity
        similarity = np.dot(skill_vec, text_vec) / (
            np.linalg.norm(skill_vec) * np.linalg.norm(text_vec)
        )

        # Ensures the similarity score is between 0.0 and 1.0.
        # 0.0 → no similarity, 1.0 → perfect match.
        return float(max(0.0, min(1.0, similarity)))
    
    except Exception as e:
        log_warning(f"Similarity error for '{skill}': {e}", context='ats_scorer')
        
        return 0.0

# e.g score = _calculate_semantic_similarity("Python", "Experienced in Python and Java development", embedder), # print(score)  # e.g., 0.87



# This function is designed to check whether a given skill appears in a text (like a resume or job description) either by direct substring match or by semantic similarity using embeddings
def _skill_matches(skill: str, text: str, embedder: SentenceTransformer, threshold: float) -> Tuple[bool, float]:
    # fast, o(n) directly check if skill is a substring of the text (case-insensitive)
    if skill.lower() in text.lower():
        return True, 1.0
    
    # slow, semantic similarity check using sentence embeddings
    sim = _calculate_semantic_similarity(skill, text, embedder)

    return sim >= threshold, sim




# Skill validation :-
# It’s a resume skill validation fn that checks whether claimed skills are actually supported by projects or experience entries.
def validate_skills_with_projects(skills: List[str], projects: List[Dict], experience_entries: List[Dict], embedder: SentenceTransformer, threshold: float = 0.6) -> Dict:
    if not skills:
        return {
            'validated_skills':  [],
            'unvalidated_skills':  [],
            'validation_percentage': 0.0,
            'skill_project_mapping': {},
            'validation_score':  0.0,
        }
    
    # Here we are creating this single string that concatenates all the text from the user’s experience entries
    # Ensures e is a dictionary (if isinstance(e, dict)).
    experience_text = ' '.join( f"{e.get('job_title', '')} {e.get('company', '')} {e.get('description', '')}"  for e in experience_entries  if isinstance(e, dict) ).strip()

    validated_skills      = []
    unvalidated_skills    = []
    skill_project_mapping = {}

    for skill in skills:
        matching_projects = []
        max_similarity    = 0.0

        for project in projects:
            project_text = f"{project.get('title', '')} {project.get('description', '')}"
            matched, sim = _skill_matches(skill, project_text, embedder, threshold)
            max_similarity = max(max_similarity, sim)

            if matched:
                matching_projects.append(project.get('title', 'Untitled Project'))

        if experience_text:
            matched, sim = _skill_matches(skill, experience_text, embedder, threshold)
            
            max_similarity = max(max_similarity, sim)
            
            if matched and 'Experience Section' not in matching_projects:
                matching_projects.append('Experience Section')

        if matching_projects:
            validated_skills.append({'skill': skill, 'projects': matching_projects, 'similarity': max_similarity})
            skill_project_mapping[skill] = matching_projects
        else:
            unvalidated_skills.append(skill)
            skill_project_mapping[skill] = []

    validation_percentage = len(validated_skills) / len(skills)
    validation_score = validation_percentage * 15.0      # since we define the weightage of skill validations to be 15 

    return {
        'validated_skills':      validated_skills,
        'unvalidated_skills':    unvalidated_skills,
        'validation_percentage': validation_percentage,
        'skill_project_mapping': skill_project_mapping,
        'validation_score':      validation_score,
    }




# 1. formatting score :-
# This function is calculating a formatting score for a resume based on how well‑structured and complete it looks.
# This function _calc_formatting_score is designed to evaluate how well a resume is formatted and return a numeric score (between 0 and 20)
# parsed_resume: a dictionary containing structured resume data (experience, education, skills, summary, projects).
# text: the raw resume text (used to check bullet points).
def _calc_formatting_score(parsed_resume: Dict, text: str) -> float:
    score = 0.0    # at first, we are assuming it to be 0

    # parsed_resume.get('experience', []) :- Looks inside the parsed_resume dictionary for the key "experience". If "experience" doesn’t exist, it defaults to an empty list [].
    exp_entries  = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    edu_entries  = [e for e in parsed_resume.get('education', [])  if isinstance(e, dict)]
    skills  = parsed_resume.get('skills', [])
    summary = parsed_resume.get('professional_summary', '')
    
    proj_entries = [p for p in parsed_resume.get('projects', [])   if isinstance(p, dict)]


    # Ensures there are valid experience entries (exp_entries not empty). At least one entry must have either a job title or description. If true → add 3.0 points.
    if exp_entries and any(e.get('job_title') or e.get('description') for e in exp_entries):
        score += 3.0
    if edu_entries:
        score += 2.0
    if len(skills) >= 3:    # If the resume lists at least 3 skills → add 2.0 points. This rewards resumes that show a broader skill set.
        score += 2.0
    if len(summary) > 30:
        score += 1.5
    if proj_entries:
        score += 1.5

    # This line is counting how many bullet points or numbered list items appear in the resume text
    # text.split('\n') :- Splits the resume text into individual lines based on newline characters.
    # 1 for line in text.split('\n') if ... :- Iterates through each line. For every line that matches the condition, yields 1.
    # re.match(r'^\s*[•\-\*\◦]', line) :- Matches lines that start with optional whitespace followed by a bullet symbol (•, -, *, ◦).
    # Example: " - Developed APIs" → match.
    # re.match(r'^\s*\d+\.', line) :- Matches lines that start with optional whitespace followed by a number and a dot (like 1. or 23.).
    # Example: "2. Built dashboards" → match.
    # sum(...) :- Adds up all the 1s produced by the generator. Result = total number of bullet/numbered lines in the resume.
    bullet_count = sum(
        1 for line in text.split('\n')  if re.match(r'^\s*[•\-\*\◦]', line) or re.match(r'^\s*\d+\.', line)
    )

    # This helper function maps a numeric input into a tiered score.
    # It takes two arguments:
    # bullet_count: the number of bullets found.
    # A list of (threshold, points) pairs:
    # Meaning: ≥15 bullets → 5.0 points and so on..
    score += _tier_score(bullet_count, [(15,5.0),(10,4.0),(5,3.0),(3,2.0),(1,1.0)])

    filled = sum(1 for has_it in [bool(exp_entries), bool(edu_entries), bool(skills), bool(summary.strip()), bool(proj_entries) ] if has_it)

    score += _tier_score(filled, [(4,5.0),(3,4.0),(2,3.0),(1,2.0)])

    return min(20.0, max(0.0, score))




# 2. keyword score :-
# This function _calc_keywords_score is meant to calculate a score based on how well the resume’s keywords align with skills and (optionally) job description keywords
def _calc_keywords_score(resume_keywords: List[str], skills: List[str], jd_keywords: Optional[List[str]] = None ) -> float:
    score = 0.0

    # Counts how many keywords were extracted from the resume. And then based on that, assign the score
    score += _tier_score(len(resume_keywords), [(20,10.0),(15,8.0),(10,6.0),(5,4.0),(3,2.0)])
    score += _tier_score(len(skills), [(15,10.0),(10,8.0),(7,6.0),(5,4.0),(3,2.0)])

    if jd_keywords:
        all_resume_terms = list(set(resume_keywords + skills))

        fuzzy_result = fuzzy_match_keywords(all_resume_terms, jd_keywords, threshold=80)

        match_pct = len(fuzzy_result['matched']) / len(jd_keywords) if jd_keywords else 0
        
        score += _tier_score(match_pct, [(0.7,5.0),(0.5,4.0),(0.3,3.0),(0.2,2.0),(0.1,1.0)])
    # But if JD is not provided by user, then we do this:- 
    # if JD is not provided by user but resume has at least 10 keywords → add +3.0.
    elif len(resume_keywords) >= 10:
        # This +3.0 is a fallback bonus when no job description (JD) keywords are provided
        score += 3.0
        # If jd_keywords is provided, the score reflects how well the resume aligns with the job description.
        # But if no JD keywords are given, the function still needs a way to reward resumes that are keyword‑rich.

    return min(25.0, max(0.0, score))    # Ensures score stays between 0 and 25 because we define the weightage of keywords to be 25




# 3. CONTENT QUALITY SCORE :-
# This function _calc_content_score is designed to measure the quality of resume content based on action verbs and grammar correctness:
def _calc_content_score(text: str, action_verbs: List[str], grammar_results: Dict ) -> float:
    score = 0.0

    #  Encourages resumes that use powerful verbs like developed, led, implemented
    score += _tier_score(len(action_verbs), [(15,10.0),(10,8.0),(7,6.0),(5,4.0),(3,2.0)])

    number_patterns = [
        r'\d+%',         # percentages (e.g., "20% increase")
        r'\$\d+',       # dollar amounts (e.g., "$5000 saved")
        r'\d+[kKmMbB]',  # large numbers (e.g., "10k users")
        r'\d+\s*(?:users|customers|clients|projects|hours|days|months|years)', # quantified metrics  (e.g., “200 users”, “12 projects”)
        r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+', # achievements with numbers (e.g., “improved by 30”, “saved 100”).
    ]

    # Scans the resume text for quantified achievements (numbers, percentages, metrics). Counts how many matches are found.
    # re.findall(p, text, re.IGNORECASE) :- For each regex pattern p, it searches the resume text (text) for all matches. Returns a list of all matches found.
    achievement_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in number_patterns)
    # text = "Increased revenue by 20% and saved $5000. Managed 10k users."
    # Matches: \d+% → "20%" → 1 match & \$\d+ → "$5000" → 1 match  & \d+[kKmMbB] → "10k" → 1 match
    # Total = 3

    score += _tier_score(achievement_count, [(10,5.0),(7,4.0),(5,3.0),(3,2.0),(1,1.0)])

    grammar_penalty = grammar_results.get('penalty_applied', 0.0)

    # grammar_penalty comes from the grammar checker results (e.g., number of errors or severity score).
    # The formula starts with a base of 10 points for grammar. It subtracts half of the penalty value (grammar_penalty / 2.0).
    score += max(0.0, 10.0 - grammar_penalty / 2.0)

    return min(25.0, max(0.0, score))




# 4. SKILL VALIDATION SCORE :-
def _calc_skill_validation_score(validation_results: Dict) -> float:
    return min(15.0, max(0.0, validation_results.get('validation_score', 0.0)))




# 5. ATS COMPATIBILITY SCORE :-
# This function _calc_ats_compatibility_score is designed to measure how ATS‑friendly (Applicant Tracking System compatible) a resume is.
# ATS systems parse resumes automatically, so the score reflects how easily the resume can be read and processed by such software.
# text: str → The raw resume text. Used to check formatting, symbols, and parsing issues.
# location_results: Dict → Results from location extraction (e.g., whether the resume correctly parsed a location or contact info).
# parsed_resume: Dict → The structured resume data (experience, education, skills, projects, etc.) after parsing.
def _calc_ats_compatibility_score(text: str, location_results: Dict, parsed_resume: Dict ) -> float:
    score = 15.0       # Start with a base score of 15.0. This is the maximum possible ATS compatibility score before deductions/adjustments.

    # deduction 1
    # Deducts points based on location parsing issues. location_results is a dictionary from earlier location analysis. If it contains "penalty_applied", subtract that value.
    # Example: if penalty = 2.0, score becomes 13.0.
    score -= location_results.get('penalty_applied', 0.0)

    # deduction 2
    # Counts how many special box‑drawing characters (like │, ═, ╬) appear in the resume text.
    # These symbols often come from tables or decorative formatting, which ATS systems struggle to parse.
    # re.findall(...) :- This uses Python’s regular expression (regex) library (re) to search through the resume text.
    # findall returns a list of all matches of the given pattern in the string text
    special_chars = len(re.findall(r'[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]', text))
    # The square brackets [...] define a character class — meaning “match any one of these characters.”
    # Inside are box‑drawing characters (Unicode symbols often used in tables or decorative borders):
    # Vertical bars: │
    # Corners: ╔, ╗, ╚, ╝
    # Crossings: ┼, ╬
    # Horizontal lines: ═
    # Junctions: ┤, ├, ┴, ┬, ╠, ╣, ╦, ╩
    # These symbols are common in resumes formatted with tables or ASCII art.

    if special_chars > 20:    score -= 2.0
    elif special_chars > 10:  score -= 1.0

    exp_entries  = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    edu_entries  = [e for e in parsed_resume.get('education', [])  if isinstance(e, dict)]
    
    skills_count = len(parsed_resume.get('skills', []))

    # Loops through each experience entry. Gets the "description" field (or empty string if missing). Measures its length (number of characters). Adds them all up.
    exp_desc_len = sum(len(e.get('description', '')) for e in exp_entries)
    edu_desc_len = sum(len((e.get('degree') or '') + (e.get('institution') or '')) for e in edu_entries)  # Handle None to prevent string concatenation errors


    # deduction 3
    # Each condition evaluates to either True (which counts as 1) or False (which counts as 0). The sum adds them up.
    # Result = number of sections that are too short.
    short_sections = sum([
        bool(exp_entries) and exp_desc_len < 20,
        bool(edu_entries) and edu_desc_len < 20,
        bool(parsed_resume.get('skills')) and skills_count < 2,
    ])

    if short_sections >= 2:    score -= 2.0    # If 2 or more sections are short → subtract 2 points.
    elif short_sections >= 1:  score -= 1.0

    # If the resume has valid experience entries AND more than 5 skills listed, add +1 point.
    # This rewards resumes that balance work history with a solid skill set.
    # Encourages resumes that show both practical experience and breadth of skills.
    if exp_entries and skills_count > 5:
        score += 1.0

    return min(15.0, max(0.0, score))




# Score aggregation and final interpretation :-
# So, this is the orchestrator function that pulls together all the individual scoring components (formatting, keywords, content, ATS compatibility, etc.) into one unified result.
# It calls all the smaller scoring functions (_calc_formatting_score, _calc_keywords_score, _calc_content_score, _calc_ats_compatibility_score, etc.) and combines their outputs.
# Returns a dictionary with the final scores and interpretation.
def calculate_overall_score(
    text: str,
    parsed_resume: Dict,
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None,
    experience_months: int = 0,
) -> Dict:

    formatting_score  = _calc_formatting_score(parsed_resume, text)
    keywords_score = _calc_keywords_score(keywords, skills, jd_keywords)
    content_score  = _calc_content_score(text, action_verbs, grammar_results)
    skill_validation_score  = _calc_skill_validation_score(skill_validation_results)
    ats_compatibility_score = _calc_ats_compatibility_score(text, location_results, parsed_resume)

    # This dictionary defines the maximum possible score for each resume evaluation component in your ATS scoring system
    COMPONENT_MAX = {
        'formatting': 20.0, 'keywords': 25.0, 'content': 25.0,
        'skill_validation': 15.0, 'ats_compatibility': 15.0,
    }


    formatting_pct = (formatting_score / COMPONENT_MAX['formatting']) * 100.0
    keywords_pct = (keywords_score / COMPONENT_MAX['keywords']) * 100.0
    content_pct = (content_score / COMPONENT_MAX['content']) * 100.0
    skill_validation_pct  = (skill_validation_score / COMPONENT_MAX['skill_validation']) * 100.0
    ats_compatibility_pct = (ats_compatibility_score / COMPONENT_MAX['ats_compatibility']) * 100.0

    # COmbined percentage of skills + keywords
    skills_keywords_pct = (keywords_pct * 0.6) + (skill_validation_pct * 0.4)

    # This line is calculating the weighted overall score by combining the percentages from different resume evaluation components
    # The weightage in this formula is chosen to reflect the relative importance of different resume components when evaluated by ATS systems and recruiters
    base_score = (
        skills_keywords_pct * 0.40 +
        content_pct * 0.30 +
        formatting_pct * 0.15 +
        ats_compatibility_pct * 0.15
    )
    # Weighting factors :-
    # 0.40 → Skills/keywords contribute 40% of the overall score.
    # 0.30 → Content contributes 30%.
    # 0.15 → Formatting contributes 15%.
    # 0.15 → ATS compatibility contributes 15%.


    penalties = {}
    bonuses = {}
    score = base_score

    if grammar_results.get('penalty_applied', 0.0) > 0:
        penalties['grammar'] = grammar_results['penalty_applied']

    if location_results.get('penalty_applied', 0.0) > 0:
        penalties['location_privacy'] = location_results['penalty_applied']


    validation_pct = skill_validation_results.get('validation_percentage', 0.0)
    
    if validation_pct >= 0.9:
        bonuses['excellent_skill_validation'] = 2.0
        score += 2.0
    elif validation_pct >= 0.8:
        bonuses['good_skill_validation'] = 1.0
        score += 1.0


    if grammar_results.get('total_errors', 0) == 0:
        bonuses['perfect_grammar'] = 1.0
        score += 1.0

    if jd_keywords and len(jd_keywords) > 0:
        all_resume_terms = list(set((keywords or []) + (skills or [])))
        fuzzy_result = fuzzy_match_keywords(all_resume_terms, jd_keywords, threshold=80)
        
        missing_pct = len(fuzzy_result['missing']) / len(jd_keywords)

        if missing_pct > 0.7:
            penalties['missing_jd_keywords'] = 15.0
            score -= 15.0
        elif missing_pct > 0.5:
            penalties['missing_jd_keywords'] = 10.0
            score -= 10.0
        elif missing_pct > 0.3:
            penalties['missing_jd_keywords'] = 5.0
            score -= 5.0


    overall_score = min(100.0, max(0.0, score))

    interpretation = _generate_score_interpretation(overall_score)

    return {
        'overall_score': round(overall_score, 1),
        'formatting_score': round(formatting_score, 1),
        'keywords_score': round(keywords_score, 1),
        'content_score': round(content_score, 1),
        'skill_validation_score':  round(skill_validation_score, 1),
        'ats_compatibility_score': round(ats_compatibility_score, 1),
        'overall_interpretation':  interpretation,
        'penalties': penalties,
        'bonuses': bonuses
    }




# Generating the user strength based on the overall score :-
def generate_strengths(score_results: Dict, skill_validation_results: Dict, grammar_results: Dict ) -> List[str]:
    strengths = []

    if score_results['formatting_score'] >= 16:
        strengths.append(' Well-structured with clear sections and bullet points')
    
    if score_results['keywords_score'] >= 20:
        strengths.append(' Strong keyword optimization and skills presence')
    
    if score_results['content_score']  >= 20:
        strengths.append(' Excellent use of action verbs and quantifiable achievements')
    
    if score_results['skill_validation_score']  >= 12:
        pct = skill_validation_results.get('validation_percentage', 0) * 100
        strengths.append(f' {pct:.0f}% of skills are validated by projects')
    
    if score_results['ats_compatibility_score'] >= 13:
        strengths.append(' Excellent ATS compatibility with clean formatting')
    
    if grammar_results.get('total_errors', 0) == 0:
        strengths.append(' Error-free grammar and spelling')

    # If no strengths were identified (all scores too low), adds a motivational fallback message. 
    # Ensures the function always returns at least one strength.
    if not strengths:
        strengths.append('Your resume has potential - focus on the recommendations below')
    
    return strengths




# Critical issues that could cause ATS rejection :-
# This function identifies critical resume issues that could cause an ATS (Applicant Tracking System) to reject or downgrade the resume. 
def generate_critical_issues(score_results: Dict, grammar_results: Dict, location_results: Dict ) -> List[str]:
    issues = []

    critical_errors = len(grammar_results.get('critical_errors', []))
    
    if critical_errors > 0:
        issues.append(f' {critical_errors} critical grammar/spelling error(s) detected')
    
    if location_results.get('privacy_risk') == 'high':
        issues.append('High privacy risk: Remove detailed location information')
    
    if score_results['formatting_score']  < 10:
        issues.append(' Poor formatting: Add clear sections and bullet points')
    
    if score_results['keywords_score'] < 12:
        issues.append(' Insufficient keywords and skills')
    
    if score_results['skill_validation_score'] < 7:
        issues.append(' Most skills lack supporting evidence in projects')

    return issues




# Actionable improvements to enhance ATS performance :-
def generate_improvements(score_results: Dict, skill_validation_results: Dict) -> List[str]:
    improvements = []

    if 12 <= score_results['formatting_score'] < 16:
        improvements.append('Add more bullet points and improve section organization')
    
    if 14 <= score_results['keywords_score'] < 20:
        improvements.append('Include more relevant keywords and technical skills')
    
    if 14 <= score_results['content_score'] < 20:
        improvements.append('Add more quantifiable achievements and action verbs')
    
    if 7  <= score_results['skill_validation_score'] < 12:
        unvalidated_count = len(skill_validation_results.get('unvalidated_skills', []))
        improvements.append(f'Validate {unvalidated_count} skill(s) by adding relevant project details')
    
    if 9  <= score_results['ats_compatibility_score'] < 13:
        improvements.append('Simplify formatting for better ATS compatibility')

    return improvements



# Interpretation of overall score :-
def _generate_score_interpretation(overall_score: float) -> str:
    if overall_score >= 90:   
        return 'Excellent! Your resume is highly optimized for ATS systems.'
    elif overall_score >= 80:  
        return 'Great! Your resume should perform well with most ATS systems.'
    elif overall_score >= 70:  
        return 'Good! Your resume is ATS-friendly with room for minor improvements.'
    elif overall_score >= 60:  
        return 'Fair. Your resume needs some improvements to be fully ATS-compatible.'
    elif overall_score >= 50:  
        return 'Below Average. Significant improvements needed for ATS compatibility.'
    else: 
        return 'Poor. Your resume requires major revisions to pass ATS screening.'





#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Here we have given this kind of weightage :-
# "formatting": 20, "keywords": 25, "content": 25, "skill_validation": 15, "ats_compatibility": 15
# ats_compatibility means that whether our system can parse the resume or not as per ATS
# ats_compatibility refers to how well the resume aligns with the way Applicant Tracking Systems (ATS) parse and interpret documents.

# SO keywords + skills have 40% weightage actually here becuase ATS system mostly relies on keywords & skills words matching, that's why 40% weightage is given to them



