# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'resume_analyzer.py' file which will acts as the orchestrator file for all these files of this services folder for the complete analysis of resume with feedback & recommendations
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.



import logging
import spacy

from sentence_transformers import SentenceTransformer

from typing import Dict, List, Optional

from backend.models.schemas import IssueDetail

from backend.services.groq_parser import parse_resume, parse_job_description
from backend.services.jd_matcher import compare_resume_with_jd
from backend.services.feedback_engine import analyze_issues, generate_issues_summary
from backend.services.ats_scorer import calculate_overall_score, validate_skills_with_projects

logger = logging.getLogger('ats_resume_scorer')



# The function is designed to perform a complete analysis of a resume.
# Likely coordinates multiple sub‑functions (parsing, keyword matching, skill gap analysis, similarity scoring).
# resume_text: str :- The raw text extracted from the resume file (PDF/DOCX already parsed). Input for NLP and embedding models.
# nlp: spacy.Language :- A spaCy language model instance (e.g., en_core_web_sm). Used for tokenization, named entity recognition, and skill extraction.
def analyze_full_resume(resume_text: str, nlp: spacy.Language, embedder: SentenceTransformer, job_description: Optional[str] = None ) -> Dict:
    import logging
    logger = logging.getLogger('ats_resume_scorer')

    logger.info(
        'Starting full resume analysis pipeline: resume_text_length=%d job_description_present=%s',
        len(resume_text or ''),
        bool(job_description and job_description.strip())
    )

    parsed_resume = parse_resume(resume_text)

    # logger.info(...) :- Sends an informational log message (not an error, just a status update). Useful for developers/admins to see what the system extracted.
    # !r inside the f-string :- !r means “use the repr() representation” of the value.
    # Ensures the string is logged with quotes and escape sequences visible.
    # Example: Without !r: Groq parsed summary: Experienced Python developer
    # With !r: Groq parsed summary: 'Experienced Python developer'
    logger.info(f"Groq parsed summary: {parsed_resume.get('professional_summary', '')[:100]!r}")
    logger.info(f"Groq parsed skills count: {len(parsed_resume.get('skills', []))}")
    logger.info(f"Groq parsed experience count: {len(parsed_resume.get('experience', []))}")

    skills  = parsed_resume.get('skills', [])
    projects = parsed_resume.get('projects', [])
    keywords = parsed_resume.get('keywords', [])
    action_verbs = parsed_resume.get('action_verbs', [])

    logger.info('Parsed resume extracted %d skills, %d projects, %d keywords, %d action_verbs',
                len(skills), len(projects), len(keywords), len(action_verbs))

    # sum(...) :- Adds up all the values produced by the generator. Produces the total months of experience.
    # e.g if user have two experience entries, 6 & 3 months, then sum = 3 + 6 = 9 months in total
    experience_months = sum( int(e.get('duration_months', 0)) for e in parsed_resume.get('experience', []) if isinstance(e, dict) )

    contact_info = {
        'email': parsed_resume.get('email'),
        'phone': parsed_resume.get('phone'),
        'linkedin': parsed_resume.get('linkedin'),
        'github': parsed_resume.get('github'),
        'portfolio': None,
    }

    skill_validation = validate_skills_with_projects(
        skills=skills,
        projects=projects,
        experience_entries=parsed_resume.get('experience', []),
        embedder=embedder,
    )
    logger.info('Skill validation produced %d validated skills and %d unvalidated skills',
                len(skill_validation.get('validated_skills', [])),
                len(skill_validation.get('unvalidated_skills', [])))

    jd_comparison_result = None
    jd_keywords = None

    if job_description and job_description.strip():
        logger.info('Starting job description comparison. JD length=%d', len(job_description.strip()))
        parsed_jd = parse_job_description(job_description.strip())

        logger.info(
            'Parsed JD keywords counts: required=%d preferred=%d keywords=%d',
            len(parsed_jd.get('required_skills', [])),
            len(parsed_jd.get('preferred_skills', [])),
            len(parsed_jd.get('keywords', [])),
        )

        # ["Python", "FastAPI"] + ["Docker", "Kubernetes"] + ["AWS"] → ["Python", "FastAPI", "Docker", "Kubernetes", "AWS"]
        jd_keywords = list(set(
            parsed_jd.get('keywords', []) +
            parsed_jd.get('required_skills', []) +
            parsed_jd.get('preferred_skills', [])
        ))

        jd_comparison_result = compare_resume_with_jd(
            resume_text = resume_text,
            resume_keywords = keywords,
            resume_skills = skills,
            jd_text = job_description.strip(),
            jd_keywords = jd_keywords,
            embedder = embedder,
            nlp = nlp,
        )
        logger.info('JD comparison finished: matched=%d missing=%d skills_gap=%d',
                    len(jd_comparison_result.get('matched_keywords', [])),
                    len(jd_comparison_result.get('missing_keywords', [])),
                    len(jd_comparison_result.get('skills_gap', [])))

    from backend.utils.file_utils import (
        get_default_grammar_results, get_default_location_results,
    )

    grammar_results  = get_default_grammar_results()
    location_results = get_default_location_results()

    scores = calculate_overall_score(
        text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        keywords=keywords,
        action_verbs=action_verbs,
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        jd_keywords=jd_keywords,
        experience_months=experience_months,
    )

    detailed_feedback = analyze_issues(
        resume_text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        projects=projects,
        action_verbs=action_verbs,
        skill_validation=skill_validation,
        scores=scores,
        contact_info=contact_info,
    )
    logger.info('Generated %d detailed feedback items', len(detailed_feedback))

    issues_summary = generate_issues_summary(detailed_feedback)
    logger.info('Generated issues summary with %d entries', len(issues_summary))

    validated_raw = skill_validation.get('validated_skills', [])
    unvalidated_raw = skill_validation.get('unvalidated_skills', [])
    total_skills = len(validated_raw) + len(unvalidated_raw)
    val_pct  = round((len(validated_raw) / total_skills * 100) if total_skills > 0 else 0, 1)


    skill_validation_details = {
        "validated": [
            {
                "skill":    item['skill'],
                "projects": item.get('projects', []),
            }
            for item in validated_raw
        ],

        "unvalidated": unvalidated_raw,
        "total": total_skills,
        "validated_count": len(validated_raw),
        "validation_pct": val_pct,
    }

    logger.info(
        'Completed analysis scoring: overall_score=%s formatting=%s keywords=%s content=%s skill_validation=%s ats_compatibility=%s',
        scores['overall_score'],
        scores['formatting_score'],
        scores['keywords_score'],
        scores['content_score'],
        scores['skill_validation_score'],
        scores['ats_compatibility_score'],
    )

    result = {
        "ATS_score":  scores['overall_score'],
        "ats_score": scores['overall_score'],
        "component_scores": {
            "formatting": scores['formatting_score'],
            "keywords": scores['keywords_score'],
            "content": scores['content_score'],
            "skill_validation": scores['skill_validation_score'],
            "ats_compatibility": scores['ats_compatibility_score'],
        },
        "issues_summary": issues_summary,
        "detailed_feedback": detailed_feedback,
        "jd_match_analysis": jd_comparison_result,
        "jd_comparison": jd_comparison_result,
        "skills": skills,
        "matched_keywords":  (
            jd_comparison_result['matched_keywords'] if jd_comparison_result else list(keywords[:20])
        ),
        "missing_keywords":  (
            jd_comparison_result['missing_keywords'] if jd_comparison_result else []
        ),
        "strengths": _generate_strengths(parsed_resume, skills, projects, action_verbs, skill_validation, scores),
        "interpretation": scores.get('overall_interpretation', ''),
        "skill_validation_details": skill_validation_details,
        "experience_months": experience_months,
    }





# This is defining a helper function that generates a list of strengths from a resume analysis
def _generate_strengths(
    parsed_resume: Dict, skills: List, projects: List,
    action_verbs: List, skill_validation: Dict, scores: Dict,
) -> List[str]:
    
    """Generate a list of things the resume does well, based on actual structured data."""
    
    strengths = []

    if parsed_resume.get('experience'):
        strengths.append("Has a dedicated Experience section")

    if parsed_resume.get('projects') or len(projects) > 0:
        strengths.append("Includes a Projects section showcasing applied skills")
    
    if parsed_resume.get('education'):
        strengths.append("Education section is present")
    
    if parsed_resume.get('skills'):
        strengths.append("Clear Skills section with listed technologies")
    
    if parsed_resume.get('professional_summary', '').strip():
        strengths.append("Professional Summary provides a quick overview")

    if len(skills) >= 8:
        strengths.append(f"Strong skill set — {len(skills)} skills detected")
    
    if len(action_verbs) >= 5:
        strengths.append(f"Uses {len(action_verbs)} strong action verbs in bullet points")

    
    validated = skill_validation.get('validated_skills', [])
    
    if len(validated) >= 3:
        strengths.append(f"{len(validated)} skills are backed by project/experience evidence")

    if scores.get('formatting_score', 0) >= 16:
        strengths.append("Well-formatted and ATS-friendly structure")
    
    if scores.get('content_score', 0) >= 20:
        strengths.append("Content quality is high with measurable achievements")

    logger.info('Generated strengths list with %d entries', len(strengths))

    return strengths