# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'recommendation_engine.py' file to provide the user with the recommendations to improve the resume
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.

# So this file will tell us, what issues we have to work on first i.e what issues we have prioritize & how we can solve them.

# The dataclasses module was introduced in Python 3.7.
# A dataclass is a decorator (@dataclass) that automatically generates special methods for classes, such as:
# __init__ → constructor
# __repr__ → string representation
# __eq__ → equality comparison
# This saves you from writing boilerplate code.
# Example:
# @dataclass
# class IssueDetail:
#     issue_title: str
#     severity_level: str
#     ats_impact: str
# Instantiating:
# issue = IssueDetail("Missing Projects Section", "High", "High")
# You don’t need to manually define __init__.
from dataclasses import dataclass

# The enum module provides the Enum base class for defining enumerations.
# An enumeration is a set of symbolic names (members) bound to unique constant values.
# Useful for fields that should only take a limited set of values (e.g., severity levels).
# Example:
# class SeverityLevel(Enum):
#     LOW = "Low"
#     MODERATE = "Moderate"
#     HIGH = "High"
# Usage:
# level = SeverityLevel.HIGH
# print(level.value)  # "High"
from enum import Enum

# here we are importing this Dict, List, Optional, Tuple  from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import Dict, List, Optional



# Here we are  defining an enumeration (Enum) called Priority in Python, which is used to represent fixed priority levels:
class Priority(Enum):
    CRITICAL='critical'
    HIGH='high'
    MEDIUM='medium'
    LOW='low'
# Each member has:
# A name (e.g., CRITICAL)
# A value (e.g., 'critical')

# Priority.CRITICAL :- Refers to the enum member CRITICAL.
# You can access:
# Priority.CRITICAL.name → "CRITICAL"
# Priority.CRITICAL.value → "critical"

# Here we are using enum because if we do this directly, then even if we do spelling mistake, our code will work & it will show incorrect spelling in UI, but with enum, if we spelling mistake, then it will show error at that point only & not show incorrect spelling in UI & we can change that easily at that time.


# This defines a dataclass called Recommendation, which is a structured way to represent a piece of advice or guidance in your resume analysis system.
@dataclass
class Recommendation:
    title: str
    description: str
    priority: Priority    # Uses the Priority enum you defined earlier (CRITICAL, HIGH, MEDIUM, LOW). Ensures recommendations are ranked by importance. Example: Priority.HIGH.
    impact_score: float
    category: str
    action_items: List[str]




# Generator 1 :-
# This function generates structured recommendations based on skill validation results
# Here Output : Returns a list of Recommendation objects (the dataclass you defined earlier).
# Each Recommendation will provide actionable advice for improving the resume’s skills section.
def generate_skill_recommendations(skill_validation_results: Dict) -> List[Recommendation]:
    recommendations  = []

    unvalidated  = skill_validation_results.get('unvalidated_skills', [])
    validation_pct = skill_validation_results.get('validation_percentage', 0.0)

    # If there are no unvalidated skills (meaning every skill listed is backed by evidence), then there’s nothing to recommend.
    if not unvalidated:
        return recommendations    # empty list

    if validation_pct < 0.4:
        priority, impact = Priority.CRITICAL, 8.0
        # Now this priority.value actually gives 'critical'  
    elif validation_pct < 0.6:
        priority, impact = Priority.HIGH, 6.0
    elif validation_pct < 0.8:
        priority, impact = Priority.MEDIUM, 4.0
    else:
        priority, impact = Priority.LOW, 2.0


    action_items = [ f"Add a project or experience demonstrating '{skill}', or remove it from skills" for skill in unvalidated[:5] ]
    
    # If more then 5 skills are unvalidated, then for remaining skills these above 5 skills, we will do this
    if len(unvalidated) > 5:
        action_items.append(f'... and {len(unvalidated) - 5} more unvalidated skill(s)')

    recommendations.append(
        Recommendation(
            title = 'Validate Your Listed Skills',
            description  = (
                f'{len(unvalidated)} skill(s) are not demonstrated in your projects or experience. '
                'ATS systems and recruiters look for evidence that you\'ve actually used the skills you claim.'
            ),
            priority = priority,
            impact_score = impact,
            category = 'skill_validation',
            action_items = action_items,
        )
    )

    return recommendations




# Generator 2: grammatical suggestions :-
# This function is designed to generate recommendations related to grammar quality in a resume. 
# Input: grammar_results: Dict → a dictionary containing the results of grammar analysis (e.g., total errors, critical errors, moderate errors, minor errors).
def generate_grammar_recommendations(grammar_results: Dict) -> List[Recommendation]:
    recommendations = []

    critical_errors = grammar_results.get('critical_errors', [])
    moderate_errors = grammar_results.get('moderate_errors', [])
    minor_errors = grammar_results.get('minor_errors', [])

    total = len(critical_errors) + len(moderate_errors) + len(minor_errors)

    if total == 0:
        return recommendations
    

    if critical_errors:    # if critical grammatical errors exists
        items = []

        for error in critical_errors[:5]:
            # Gets the text that was flagged as incorrect. If missing, defaults to "unknown". Example: "recieve".
            word = error.get('error_text', 'unknown')
            suggest = error.get('suggestions', [])   # Retrieves a list of suggested corrections. Example: ["receive"].
            suffix = f" → '{suggest[0]}'" if suggest else ''

            items.append(f"Fix '{word}'{suffix}: {error.get('message', '')}")
            # e.g "Fix 'recieve' → 'receive': Spelling mistake"


        # If more then 5 critical_errors are found, then for remaining critical_errors other then these above 5 critical_errors, we will do this  
        if len(critical_errors) > 5:
            items.append(f'... and {len(critical_errors) - 5} more critical error(s)')

        recommendations.append(
            Recommendation(
                title  = 'Fix Critical Spelling/Grammar Errors',
                description  = (
                    f'{len(critical_errors)} critical error(s) found. These spelling mistakes or '
                    'major grammar issues will make your resume look unprofessional.'
                ),
                priority  = Priority.CRITICAL,
                impact_score = min(10.0, len(critical_errors) * 2.0),
                category = 'grammar',
                action_items = items,
            )
        )


    if moderate_errors:
        items = []

        for error in moderate_errors[:3]:
            word = error.get('error_text', 'unknown')
            suggest = error.get('suggestions', [])
            suffix  = f" → '{suggest[0]}'" if suggest else ''

            items.append(f"Fix '{word}'{suffix}: {error.get('message', '')}")


        if len(moderate_errors) > 3:
            items.append(f'... and {len(moderate_errors) - 3} more moderate error(s)')


        recommendations.append(
            Recommendation(
                title = 'Address Punctuation and Capitalization Issues',
                description  = (
                    f'{len(moderate_errors)} moderate error(s) found. '
                    'These punctuation or capitalization issues should be corrected.'
                ),
                priority = Priority.HIGH,
                impact_score = min(6.0, len(moderate_errors) * 1.0),
                category = 'grammar',
                action_items = items,
            )
        )


    if minor_errors and len(minor_errors) >= 3:
        recommendations.append(
            Recommendation(
                title = 'Consider Style Improvements',
                description  = (
                    f'{len(minor_errors)} minor style suggestion(s) found. '
                    'These are optional improvements for better readability.'
                ),
                priority  = Priority.LOW,
                impact_score = 1.0,
                category = 'grammar',
                action_items = [
                    f'Review {len(minor_errors)} style suggestion(s) for improved readability',
                    'Use consistent formatting throughout',
                ],
            )
        )


    return recommendations




# Generator 3: location recommendations :-
# This function is used for generating recommendations about location information in a resume. 
def generate_location_recommendations(location_results: Dict) -> List[Recommendation]:
    recommendations = []
    
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk = location_results.get('privacy_risk', 'none')

    if privacy_risk == 'none' or not detected_locations:
        return recommendations

    addresses = [loc for loc in detected_locations if loc.get('type') == 'address']
    zip_codes = [loc for loc in detected_locations if loc.get('type') == 'zip']

    action_items = []

    for addr in addresses[:2]:
        action_items.append(f"Remove full address: '{addr.get('text', '')}'")

    for z in zip_codes[:2]:
        action_items.append(f"Remove zip code: '{z.get('text', '')}'")

    action_items.append("Keep only 'City, State' in your contact header")


    if privacy_risk == 'high':
        priority = Priority.CRITICAL
        impact = 5.0
        description = (
            'Your resume contains detailed location information that poses a privacy risk. '
            'Full addresses and zip codes are unnecessary and can be used to identify your location.'
        )
    elif privacy_risk == 'medium':
        priority = Priority.HIGH
        impact = 3.0
        description = (
            "Your resume contains multiple location mentions. Consider simplifying to just "
            "'City, State' in your contact header."
        )
    else:
        priority = Priority.MEDIUM
        impact = 2.0
        description = (
            'Minor location information detected. Consider reviewing for unnecessary location details.'
        )


    recommendations.append(
        Recommendation(
            title = 'Protect Your Location Privacy',
            description = description,
            priority = priority,
            impact_score = impact,
            category = 'location',
            action_items = action_items,
        )
    )


    return recommendations




# Generator 4: keyword recommendations :-
# This function is used for generating keyword‑related recommendations in a resume analysis system
# keyword_analysis: Optional[Dict] → a dictionary containing results of keyword analysis (e.g., matched vs. missing job description keywords, keyword frequency, semantic similarity).
# resume_keywords: Optional[List[str]] → a list of keywords extracted directly from the resume.
def generate_keyword_recommendations( keyword_analysis: Optional[Dict] = None, resume_keywords: Optional[List[str]] = None ) -> List[Recommendation]:
    recommendations = []

    if keyword_analysis:   # it means that JD is provided
        missing  = keyword_analysis.get('missing_keywords', [])
        gap  = keyword_analysis.get('skills_gap', [])
        match_pct = keyword_analysis.get('match_percentage', 0.0)

        if missing:
            if match_pct < 40:
                priority, impact = Priority.CRITICAL, 8.0
            elif match_pct < 60:
                priority, impact = Priority.HIGH, 6.0
            else:
                priority, impact = Priority.MEDIUM, 4.0

            items = [f"Add '{kw}' to your resume in a relevant section" for kw in missing[:7]]

            if len(missing) > 7:
                items.append(f'... and {len(missing) - 7} more missing keyword(s)')


            recommendations.append(
                Recommendation(
                    title = 'Add Missing Job Description Keywords',
                    description  = (
                        f'{len(missing)} keyword(s) from the job description are missing from '
                        f'your resume. Your current match is {match_pct:.0f}%.'
                    ),
                    priority = priority,
                    impact_score = impact,
                    category = 'keywords',
                    action_items = items,
                )
            )


        if gap:
            items = [f"Consider adding '{skill}' if you have this skill" for skill in gap[:5]]
            
            if len(gap) > 5:
                items.append(f'... and {len(gap) - 5} more skill(s) mentioned in the job')

            recommendations.append(
                Recommendation(
                    title = 'Address Skills Gap',
                    description  = (
                        f'The job description mentions {len(gap)} skill(s) not found in your resume. '
                        'Add these skills if you have them, or consider gaining them.'
                    ),
                    priority = Priority.HIGH,
                    impact_score = 5.0,
                    category = 'keywords',
                    action_items = items,
                )
            )

    elif resume_keywords is not None:    # when JD is not provided
        if len(resume_keywords) < 10:
            recommendations.append(
                Recommendation(
                    title = 'Increase Keyword Density',
                    description  = (
                        f'Your resume contains only {len(resume_keywords)} keywords. '
                        'Adding more relevant keywords will improve ATS matching.'
                    ),
                    priority = Priority.MEDIUM,
                    impact_score = 4.0,
                    category = 'keywords',
                    action_items = [
                        "Add more technical skills and tools you've used",
                        'Include industry-specific terminology',
                        'Mention relevant certifications and methodologies',
                    ],
                )
            )


    return recommendations




# Generator 5: formatting and structure recommendations :-
# This function is used for generating formatting‑related recommendations in a resume analysis system.
# Inputs:
# score_results: Dict → contains numeric scores for different resume components (e.g., formatting score, keyword score, ATS compatibility).
# sections: Dict[str, str] → dictionary of resume sections (e.g., "experience": "...text...", "education": "...text...").
def generate_formatting_recommendations( score_results: Dict, sections: Dict[str, str] ) -> List[Recommendation]:
    recommendations  = []

    formatting_score = score_results.get('formatting_score', 0.0)

    section_recommendations = {
        'experience': "Add a clear 'Experience' or 'Work History' section",
        'education':  "Add an 'Education' section with your qualifications",
        'skills':  "Add a 'Skills' section listing your technical and soft skills",
        'summary': "Consider adding a 'Summary' or 'Objective' section at the top",
        'projects': "Consider adding a 'Projects' section to showcase your work",
    }

    missing_sections = []

    for section_name, suggestion in section_recommendations.items():
        content = sections.get(section_name, '')

        if not content or len(content) < 20:
            # Adds a tuple (section_name, suggestion) to the missing_sections list.
            # e.g ("Projects", "Add at least 2–3 significant projects with details").
            missing_sections.append((section_name, suggestion))


    core_missing = [(n, s) for n, s in missing_sections if n in ['experience', 'education', 'skills']]
    optional_missing = [(n, s) for n, s in missing_sections if n in ['summary', 'projects']]


    if core_missing:
        recommendations.append(
            Recommendation(
                title = 'Add Missing Core Sections',
                description  = (
                    f'Your resume is missing {len(core_missing)} essential section(s). '
                    'ATS systems expect standard resume sections.'
                ),
                priority = Priority.CRITICAL,
                impact_score = 7.0,
                category = 'formatting',
                action_items = [suggestion for _, suggestion in core_missing],
            )
        )


    if optional_missing and formatting_score < 15:
        recommendations.append(
            Recommendation(
                title = 'Consider Adding Optional Sections',
                description  = 'Adding a summary and projects section can strengthen your resume.',
                priority = Priority.LOW,
                impact_score = 2.0,
                category = 'formatting',
                action_items = [suggestion for _, suggestion in optional_missing],
            )
        )


    if formatting_score < 12:   # Below 60% of 20 pts
        recommendations.append(
            Recommendation(
                title = 'Improve Resume Structure',
                description  = (
                    f'Your formatting score is {formatting_score:.1f}/20. '
                    'Better structure will improve ATS parsing and readability.'
                ),
                priority = Priority.HIGH,
                impact_score = 5.0,
                category = 'formatting',
                action_items = [
                    'Use bullet points to list achievements and responsibilities',
                    'Add clear section headers (Experience, Education, Skills)',
                    'Ensure consistent formatting throughout',
                    'Use a clean, single-column layout',
                ],
            )
        )


    return recommendations




# This function is designed to sort recommendations by importance so the most urgent ones appear first.
# Now using this fn, we will assign priority to these recommentations, so that we can decide which recommendations we need to give firstly.
def _prioritize_recommendations(recommendations: List[Recommendation]) -> List[Recommendation]:
    # Creates a dictionary mapping each Priority enum to a numeric rank.
    # Lower numbers = higher importance.
    # CRITICAL → 0 (highest priority)
    # HIGH → 1
    # MEDIUM → 2
    # LOW → 3 (lowest priority)
    priority_order = {
        Priority.CRITICAL: 0,
        Priority.HIGH:     1,
        Priority.MEDIUM:   2,
        Priority.LOW:      3,
    }

    # Uses Python’s sorted() to order the list. 
    # The key function (which is a lambda fn) returns a tuple for each recommendation:
    # priority_order[r.priority] → ensures CRITICAL comes before HIGH, etc.
    # -r.impact_score → sorts by descending impact score within the same priority level (higher impact first).
    # Example:
    # Two HIGH priority recommendations: one with impact 8.0, one with impact 6.0.
    # Both have the same priority rank (1), so sorting falls back to -impact_score.   
    # The one with 8.0 impact comes first.
    return sorted(
        recommendations, 
        key = lambda r: (priority_order[r.priority], -r.impact_score) 
    )
    # Python sorts tuples element by element:
    # First by priority rank (CRITICAL = 0, HIGH = 1, MEDIUM = 2, LOW = 3).
    # If two recommendations have the same priority, it sorts by the second element (impact score descending, because of the minus sign).
    
    # lambda r: Creates an anonymous function (a function without a name).
    # It takes one argument r, which represents a single Recommendation object.

    # recommendations :- A list of Recommendation objects (each has priority, impact_score, etc.).
    # key=lambda r: (...) :- Defines how each recommendation should be ranked for sorting. r is a single Recommendation object.
    # The lambda returns a tuple with two values:
    # priority_order[r.priority] → numeric rank of the priority.
    # -r.impact_score → negative impact score (so higher scores come first).




# Orchestrator of this file :-
# This function is the orchestrator — it pulls together all the specialized recommendation generators (skills, grammar, location, formatting, keywords) into one unified pipeline.
def generate_all_recommendations(
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    score_results: Dict,
    sections: Dict[str, str],
    keyword_analysis: Optional[Dict] = None,
    resume_keywords: Optional[List[str]] = None,
) -> Dict:

    all_recs = []

    # Collect from all five domain generators
    # Here we are using extend :- Because it Adds multiple elements from another iterable (like a list, tuple, or set) to the end of the list.
    # Behavior: It iterates through the argument and adds each element individually.
    # arr = [1, 2, 3] & arr.extend([4, 5]) , so print(arr)   # [1, 2, 3, 4, 5]
    # arr = [1, 2, 3] & arr.append([4, 5]) , so print(arr)   # [1, 2, 3, [4, 5]]
    all_recs.extend(generate_skill_recommendations(skill_validation_results))
    all_recs.extend(generate_grammar_recommendations(grammar_results))
    all_recs.extend(generate_location_recommendations(location_results))
    all_recs.extend(generate_keyword_recommendations(keyword_analysis, resume_keywords))
    all_recs.extend(generate_formatting_recommendations(score_results, sections))


    # Sort: critical first, highest impact within each tier
    prioritized = _prioritize_recommendations(all_recs)

    # Group by priority level for convenient access
    critical = [r for r in prioritized if r.priority == Priority.CRITICAL]
    high = [r for r in prioritized if r.priority == Priority.HIGH]
    medium = [r for r in prioritized if r.priority == Priority.MEDIUM]
    low = [r for r in prioritized if r.priority == Priority.LOW]

    # Estimate improvement potential (sum of impact scores, capped at 30)
    # This line is calculating an overall improvement estimate based on the impact scores of prioritized recommendations, but with a cap.
    estimated_improvement = min(30.0, sum(r.impact_score for r in prioritized))
    # sum(r.impact_score for r in prioritized) :- Loops through all recommendations in the list prioritized. Extracts each recommendation’s impact_score. Adds them up to get the total potential improvement if all recommendations were applied. Example: If impact scores are [8.0, 6.0, 4.0], the sum = 18.0.

    # So it means that we are saying even after recommendations, max-to-max our ATS score can improve by 30 points only.
    # because we do not want to claim that recommendations can imporve score by 50 points or 60 points as which is very odd

    return {
        'all_recommendations': prioritized,
        'critical_recommendations': critical,
        'high_recommendations': high,
        'medium_recommendations': medium,
        'low_recommendations': low,
        'total_count':  len(prioritized),
        'estimated_improvement': estimated_improvement,
    }




# This function is meant to convert recommendation objects into a clean, API‑friendly format (plain dictionaries).
def format_recommendations_for_api(recommendations_result: Dict) -> List[Dict]:
    priority_icons = {
        Priority.CRITICAL: '🔴',
        Priority.HIGH:     '🟠',
        Priority.MEDIUM:   '🟡',
        Priority.LOW:      '🟢',
    }

    priority_labels = {
        Priority.CRITICAL: 'Critical',
        Priority.HIGH:     'High Priority',
        Priority.MEDIUM:   'Medium Priority',
        Priority.LOW:      'Low Priority',
    }

    return [
        {
            'title':          rec.title,
            'description':    rec.description,
            'priority_icon':  priority_icons[rec.priority],
            'priority_label': priority_labels[rec.priority],
            'priority_value': rec.priority.value,
            'impact_score':   rec.impact_score,
            'category':       rec.category,
            'action_items':   rec.action_items,
        }

        for rec in recommendations_result.get('all_recommendations', [])
    ]




# This function is designed to produce a textual summary of all recommendations — essentially a human‑readable overview. 
def get_recommendation_summary(recommendations_result: Dict) -> str:
    total = recommendations_result.get('total_count', 0)
    critical = len(recommendations_result.get('critical_recommendations', []))
    high = len(recommendations_result.get('high_recommendations', []))
    improvement = recommendations_result.get('estimated_improvement', 0.0)

    if total == 0:
        return 'Excellent! No major recommendations. Your resume is well-optimized.'


    if critical > 0:
        return (
            f'Found {total} recommendation(s) including {critical} critical issue(s). '
            f'Addressing these could improve your score by up to {improvement:.0f} points.'
        )
    elif high > 0:
        return (
            f'Found {total} recommendation(s) including {high} high-priority item(s). '
            f'Addressing these could improve your score by up to {improvement:.0f} points.'
        )
    else:
        return (
            f'Found {total} recommendation(s) for improvement. '
            f'Addressing these could improve your score by up to {improvement:.0f} points.'
        )
    



