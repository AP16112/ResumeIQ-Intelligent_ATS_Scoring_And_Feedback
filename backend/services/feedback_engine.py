# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'feedback_engine.py' file to provide the user with the feedback related to resume
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.

# So this file will tell : what is specifically wrong in my resume?

# It is Python’s built‑in regular expressions module. Allows you to search, match, and manipulate text patterns.
# e.g text = "Hello, world!" then, words = re.split(r'\W+', text). print(words)  # ['Hello', 'world', '']
import re  

# here we are importing this Dict, List, Optional, Tuple  from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import List, Dict, Any, Optional

from backend.models.schemas import IssueDetail


# THis is the main function that inspects the resume for problems.
# Returns a list of IssueDetail objects (structured issue reports with title, severity, ATS impact, suggested fixes, etc.).
def analyze_issues(
    resume_text: str,    # The raw text of the resume. Used for regex checks, grammar analysis, keyword detection, etc.
    parsed_resume: Dict,         
    skills: List[str], 
    projects: List[Dict], 
    action_verbs: List[str], 
    skill_validation: Dict, 
    scores: Dict,     # Contains numeric scores for different components (formatting, keywords, content, ATS compatibility, skill validation).
    contact_info: Optional[Dict] = None   # Contact details parsed from the resume (email, phone, location). Optional because not all resumes include it.
) -> List[IssueDetail]:
    
    # Initializes an empty list called detected. This will eventually hold IssueDetail objects (structured reports of problems found in the resume).
    # The type hint List[IssueDetail] makes it clear that each element will be an IssueDetail.
    detected: List[IssueDetail] = []


    # Unpack frequently-used structured fields once at the top
    # instead of repeatedly calling parsed_resume.get(...) later, we extract the key sections once here for convenience and readability.
    exp_entries  = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    edu_entries  = [e for e in parsed_resume.get('education',  []) if isinstance(e, dict)]
    proj_entries = [p for p in parsed_resume.get('projects',   []) if isinstance(p, dict)]
    summary  = (parsed_resume.get('professional_summary') or '').strip()  # Handle None to prevent string concatenation errors

    # Build a combined experience text for regex-based checks that still need text
    # some checks (like regex for action verbs or quantified achievements) require raw text, not structured data.
    experience_text = '\n'.join(e.get('description', '') for e in exp_entries).strip()
    # Loops through each experience entry in exp_entries. Extracts the "description" field (or '' if missing). Joins them together with newline characters (\n). Strips whitespace at the ends.


    # 1. missing project section :-
    resume_lower = resume_text.lower()

    # Loops through each keyword in the list. Checks if that keyword is present in resume_lower. any(...) returns True if at least one keyword is found, otherwise False.
    has_projects_signal = any(kw in resume_lower for kw in [
        'project', 'github.com', 'deployed', 'built a', 'developed a',
        'created a', 'implemented a', 'live demo', 'tech stack',
    ])


    # This line checks three signals to decide if the resume lacks project evidence:
    # not proj_entries → No structured "projects" section in the parsed resume.
    # len(projects) == 0 → The projects list passed into the function is empty.
    # not has_projects_signal → No textual hints of projects in the raw resume text (like “project,” “github.com,” “deployed,” etc.).
    # Only if all three are missing does it conclude the resume has no project evidence.
    if not proj_entries and len(projects) == 0 and not has_projects_signal:
        detected.append(IssueDetail(
            issue_title="Missing Projects Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "Your resume does not have a dedicated Projects section. "
                "ATS systems and recruiters look for concrete projects to validate "
                "that your listed skills have been applied in practice."
            ),

            where_it_appears="Resume structure — no 'Projects' header was detected",

            how_to_fix=(
                "Add a 'Projects' section with 2–3 significant projects. "
                "For each project, include the title, technologies used, "
                "what you built, and a measurable outcome."
            ),

            action_items=[
                "Add a 'PROJECTS' section heading after your Experience section",
                "Include 2–3 projects (personal, academic, or open-source)",
                "For each project: write the title, tech stack used, what you built, and a measurable result",
                "Example: 'E-Commerce Platform — React, Node.js, MongoDB. Handled 500+ transactions/month'",
                "Link to GitHub or a live demo if available (e.g., github.com/yourname/project)",
            ],

            example_improvement=(
                "Add:\n"
                "PROJECTS\n"
                "• E-Commerce Platform — Built a full-stack shopping site using "
                "React, Node.js, and MongoDB. Implemented payment processing with "
                "Stripe, handling 500+ transactions/month.\n"
                "• ML Sentiment Analyzer — Trained a BERT model on 10K reviews "
                "achieving 92% accuracy. Deployed as a REST API with FastAPI."
            ),
        ))


    # 2. missing experience section :-
    has_experience_signal = any(kw in resume_lower for kw in [
        'intern', 'internship', 'employed', 'worked at', 'working at',
        'company', 'organization', 'job', 'role', 'position', 'designation',
        'manager', 'engineer', 'developer', 'analyst', 'consultant',
    ])


    if not exp_entries and not has_experience_signal:
        detected.append(IssueDetail(
            issue_title="Missing Work Experience Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "No work experience section was detected. Even for freshers, "
                "internships, freelance work, or volunteer experience help "
                "demonstrate professional capability."
            ),
            where_it_appears="Resume structure — no 'Experience' or 'Work History' header found",
            how_to_fix=(
                "Add an 'Experience' section. If you lack formal employment, "
                "include internships, freelance projects, open-source contributions, "
                "or relevant volunteer work."
            ),
            action_items=[
                "Add an 'EXPERIENCE' or 'INTERNSHIPS' section to your resume",
                "List each role with: Job Title — Company Name (Month Year – Month Year)",
                "Add 2–4 bullet points per role describing what you did and its impact",
                "If no formal job: include internships, freelance work, open-source, or college clubs",
                "Start every bullet with a past-tense action verb (Developed, Built, Led, etc.)",
            ],
            example_improvement=(
                "Add:\n"
                "EXPERIENCE\n"
                "Software Engineering Intern — XYZ Corp (Jun 2025 – Aug 2025)\n"
                "• Developed REST APIs with FastAPI serving 10K requests/day\n"
                "• Reduced page load time by 40% through caching optimization"
            ),
        ))



    # 3. Missing Education Section :-
    has_education_signal = any(kw in resume_lower for kw in [
        'b.tech', 'btech', 'b.e.', 'b.sc', 'bsc', 'm.tech', 'mtech', 'm.sc',
        'bachelor', 'master', 'phd', 'university', 'college',
        'institute of technology', 'cgpa', 'gpa', 'graduated', 'diploma',
        'class of', '20', 'batch of',
    ])


    if not edu_entries and not has_education_signal:
        detected.append(IssueDetail(
            issue_title="Missing Education Section",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "No education section was found. Most ATS systems expect an "
                "Education section with at least your degree and institution."
            ),
            where_it_appears="Resume structure — no 'Education' header detected",
            
            how_to_fix=(
                "Add an 'Education' section listing your degree, university, "
                "graduation year, and optionally your GPA or relevant coursework."
            ),
            action_items=[
                "Add an 'EDUCATION' section (usually at the bottom for experienced candidates, top for freshers)",
                "Include: Degree name — Institution name (Start Year – End Year)",
                "Add your CGPA or percentage if it is 7.0+ or 70%+",
                "Optionally list 3–5 relevant courses (e.g., Data Structures, DBMS, ML)",
            ],
            example_improvement=(
                "Add:\n"
                "EDUCATION\n"
                "B.Tech in Computer Science — Manipal Institute of Technology, Bengaluru (2023–2027)\n"
                "CGPA: 9.5 | Relevant Coursework: Data Structures, ML, DBMS"
            ),
        ))



    # 4. Missing Skills Section :- 
    if not parsed_resume.get('skills') and len(skills) < 3:  # only flag if extraction also found very few skills
        detected.append(IssueDetail(
            issue_title="Missing or Weak Skills Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Only {len(skills)} skill(s) were detected. ATS systems "
                "rely heavily on keyword matching from a dedicated Skills section. "
                "Without clear skills listed, your resume may fail automated filters."
            ),
            where_it_appears="Skills section — either missing or contains very few items",
            
            how_to_fix=(
                "Add a clear 'Skills' section organized by category. "
                "Include programming languages, frameworks, tools, and soft skills "
                "that match your target role."
            ),
            action_items=[
                "Add a 'TECHNICAL SKILLS' or 'SKILLS' section",
                "Organize by category: Languages, Frameworks, Tools, Databases, Cloud",
                "List at least 10–15 skills relevant to your target role",
                "Use the exact names that appear in job descriptions (e.g., 'React.js' not just 'React')",
                "Include tools you use daily: Git, VS Code, Postman, Docker, etc.",
            ],
            example_improvement=(
                "Add:\n"
                "TECHNICAL SKILLS\n"
                "Languages: Python, JavaScript, TypeScript, SQL\n"
                "Frameworks: React, FastAPI, Django, Express.js\n"
                "Tools: Docker, Git, AWS, PostgreSQL, MongoDB"
            ),
        ))



    # 5. Skills Lack Supporting Evidence :-
    unvalidated = skill_validation.get('unvalidated_skills', [])
    validated   = skill_validation.get('validated_skills', [])

    total_skills = len(unvalidated) + len(validated)

    if total_skills > 0 and len(unvalidated) > len(validated):
        # Takes the first 8 unvalidated skills (to avoid an overly long list).
        # Joins them into a comma‑separated string.
        unsupported_list = ', '.join(unvalidated[:8])
        
        pct_unsupported = round((len(unvalidated) / total_skills) * 100)

        action_items_skills = [ f"Mention '{skill}' in a project or experience bullet point" for skill in unvalidated[:5] ]
        action_items_skills.append("Remove skills you cannot demonstrate with any project or experience")
        
        # As we already added the actions needed to be done for the 5 unvalidated skills, so if more then 5 unvlaided skills, then for them, we will do this.
        if len(unvalidated) > 5:
            action_items_skills.append(f"({len(unvalidated) - 5} more unvalidated skills — review each one)")
        

        detected.append(IssueDetail(
            issue_title="Most Skills Lack Supporting Evidence",
            severity_level="Moderate",
            ats_impact="High",
            explanation=(
                f"{pct_unsupported}% of your listed skills ({len(unvalidated)} out of "
                f"{total_skills}) are not backed by any mention in your projects or "
                "experience sections. Recruiters and ATS systems cross-reference "
                "skills against actual work to verify credibility."
            ),
            where_it_appears=f"These skills have no supporting context: {unsupported_list}",
            
            how_to_fix=(
                "For each skill in your Skills section, ensure it appears at least "
                "once in a project description or experience bullet point. "
                "Describe how and where you used that technology."
            ),
            action_items=action_items_skills,
            
            example_improvement=(
                f"Your skill '{unvalidated[0]}' has no supporting evidence.\n\n"
                f"Fix: Add to a project or experience bullet:\n"
                f"'Built a data pipeline using {unvalidated[0]} that processed "
                "10K records daily, reducing manual effort by 60%.'"
            ),
        ))



    # 6. Weak Action Verbs :-

    # Outer loop: iterate over experience entries
    # exp_entries is a list of dictionaries, each representing one job/experience entry.
    # Inner loop: split description into lines
    # For each experience entry, get the "description" field. If "description" is missing, default to ''.
    # Split the description into separate lines using newline (\n).
    # e.g "Developed APIs\nLed a team" → ["Developed APIs", "Led a team"].
    description_lines = [ line.strip() for exp in exp_entries for line in exp.get('description', '').split('\n') if line.strip() ]
    # if line.strip() :- Keeps only non‑empty lines. Prevents blank lines from being added to the list. Example: " " → discarded.


    if len(description_lines) > 3 and len(action_verbs) < 3:
        detected.append(IssueDetail(
            issue_title="Bullet Points Lack Strong Action Verbs",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                f"Your experience section has {len(description_lines)} bullet points but "
                f"only {len(action_verbs)} start with strong action verbs. "
                "ATS systems and recruiters favor bullets that begin with verbs like "
                "'Developed', 'Implemented', 'Designed', 'Optimized'."
            ),
            where_it_appears="Experience section — bullet point openings",
            how_to_fix=(
                "Start every bullet point with a past-tense action verb. "
                "Avoid starting with 'Responsible for', 'Worked on', or 'Helped with'. "
                "Use verbs like: Developed, Built, Designed, Implemented, Led, Automated, Optimized."
            ),
            action_items=[
                "Rewrite every bullet that starts with 'Responsible for', 'Helped', 'Worked on', or 'Assisted'",
                "Use: Developed, Built, Designed, Implemented, Led, Automated, Optimized, Deployed, Reduced, Increased",
                "Make verbs past-tense for previous roles, present-tense for current role",
                f"Review all {len(description_lines)} bullet points — at least {len(description_lines)} should start with action verbs",
                "Avoid weak openers like 'Was responsible for...' or 'Involved in...'",
            ],
            example_improvement=(
                "Before:\n"
                "• Responsible for building the backend\n"
                "• Worked on the payment feature\n\n"
                "After:\n"
                "• Developed a REST API with FastAPI handling 5K daily requests\n"
                "• Implemented Stripe payment integration reducing checkout time by 30%"
            ),
        ))



    # 7. No Quantifiable Achievements :-
    # Here, this will check whether the resume’s experience section contains measurable, quantifiable achievements (numbers, percentages, dollar amounts).
    number_pattern = r'\d+[%+]?|\$\d+'
    # Defines a regex pattern (number_pattern) to detect numbers in the text.
    # \d+ → matches one or more digits.
    # [%+]? → optionally matches a % or + sign after the number (e.g., 20%, +15).
    # |\$\d+ → OR matches a dollar sign followed by digits (e.g., $5000).
    # Together, this pattern detects metrics like percentages, improvements, or monetary values.


    # re.findall(number_pattern, experience_text) → searches the resume’s experience text for all matches of the pattern. If matches are found, it returns a list of them.
    # bool(...) → converts that list into True if non‑empty, False if empty.
    # if experience_text else False → ensures that if there’s no experience text at all, has_metrics is set to False.
    # So has_metrics is True if the resume experience contains numbers/metrics, otherwise False.
    has_metrics = bool(re.findall(number_pattern, experience_text)) if experience_text else False


    if experience_text and not has_metrics:
        detected.append(IssueDetail(
            issue_title="No Quantifiable Achievements Found",
            severity_level="Moderate",
            ats_impact="Medium",
            explanation=(
                "Your experience section does not contain any measurable outcomes "
                "(numbers, percentages, or dollar amounts). Quantified achievements "
                "make your impact concrete and are strongly preferred by recruiters."
            ),
            where_it_appears="Experience section — bullet point content",
            how_to_fix=(
                "Add numbers to at least 50% of your bullet points. "
                "Include metrics like: users served, response time improved, "
                "revenue generated, lines of code, team size, etc."
            ),
            action_items=[
                "Go through each bullet point and ask: 'How much?', 'How many?', 'By what %?'",
                "Add metrics: users served, requests/day, % improvement, team size, time saved",
                "Examples: '500+ daily users', 'reduced load time by 40%', 'handled 10K API calls/day'",
                "If exact numbers aren't known, use reasonable estimates (e.g., '~200 users')",
                "Aim for numbers in at least 50% of your experience bullets",
            ],
            example_improvement=(
                "Before:\n"
                "• Improved application performance\n"
                "• Managed a team of developers\n\n"
                "After:\n"
                "• Improved API response time by 45% through Redis caching\n"
                "• Led a team of 5 developers delivering 3 features per sprint"
            ),
        ))



    # 8. Missing Contact Information :- 

    if contact_info:
        missing_contacts = []

        # Looks for the "email" key in contact_info.
        # If it’s missing or empty, adds "email" to the missing_contacts list.
        if not contact_info.get('email'):
            missing_contacts.append('email')
        if not contact_info.get('phone'):
            missing_contacts.append('phone number')
        if not contact_info.get('linkedin'):
            missing_contacts.append('LinkedIn URL')

        if len(missing_contacts) >= 2:
            contact_action_items = [f"Add your {item} to the header section" for item in missing_contacts]
            
            contact_action_items += [
                "Format the contact line as: email | phone | linkedin | github",
                "Make sure your LinkedIn URL is a custom short URL (linkedin.com/in/yourname)",
                "Add a GitHub link if you have public projects (github.com/yourname)",
            ]

            detected.append(IssueDetail(
                issue_title="Incomplete Contact Information",
                severity_level="High",
                ats_impact="High",
                explanation=(
                    f"Your resume is missing: {', '.join(missing_contacts)}. "
                    "Recruiters need reliable ways to reach you. Missing contact "
                    "details can cause your application to be skipped entirely."
                ),
                where_it_appears="Header / Contact section at the top of the resume",
                how_to_fix=(
                    "Add your full name, email, phone number, LinkedIn profile, "
                    "and optionally a GitHub or portfolio link at the top of your resume."
                ),
                action_items=contact_action_items,
                example_improvement=(
                    "Add at top:\n"
                    "John Doe\n"
                    "john.doe@email.com | +91-9876543210\n"
                    "linkedin.com/in/johndoe | github.com/johndoe"
                ),
            ))



    # 9. Low Formatting Score :-

    formatting_score = scores.get('formatting_score', 20)

    if formatting_score < 10:
        detected.append(IssueDetail(
            issue_title="Poor Resume Formatting",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Your formatting score is {formatting_score}/20, which indicates "
                "problems like missing section headers, inconsistent structure, "
                "or non-standard layout that ATS parsers struggle with."
            ),
            where_it_appears="Overall document structure and formatting",
            how_to_fix=(
                "Use a clean, single-column layout with standard section headers "
                "(Experience, Education, Skills, Projects). Use consistent bullet "
                "points, standard fonts, and avoid tables, columns, or graphics."
            ),
            action_items=[
                "Switch to a single-column layout (avoid two-column templates for ATS)",
                "Use standard section headers: EXPERIENCE, EDUCATION, SKILLS, PROJECTS",
                "Use bullet points (•) consistently — don't mix with dashes or asterisks",
                "Remove all tables, text boxes, headers/footers, and images — ATS cannot parse them",
                "Use a standard font (Calibri, Arial, Times New Roman) at 10–12pt",
                "Order sections: Contact → Summary → Experience → Projects → Education → Skills",
            ],
            example_improvement=(
                "Use this structure:\n"
                "NAME & CONTACT\n"
                "SUMMARY (2-3 lines)\n"
                "EXPERIENCE (reverse chronological)\n"
                "PROJECTS (2-3 key projects)\n"
                "EDUCATION\n"
                "SKILLS (categorized)"
            ),
        ))



    # 10. Missing Summary/Objective :-

    if not summary:
        detected.append(IssueDetail(
            issue_title="Missing Professional Summary",
            severity_level="Low",
            ats_impact="Low",
            explanation=(
                "Your resume does not include a Professional Summary or Objective "
                "section at the top. While not required, a 2-3 line summary helps "
                "recruiters quickly understand your profile and target role."
            ),
            where_it_appears="Top of resume — below contact info",
            how_to_fix=(
                "Add a 2-3 sentence summary highlighting your experience level, "
                "key skills, and career focus. Tailor it to the job you're applying for."
            ),
            action_items=[
                "Add a 'PROFESSIONAL SUMMARY' or 'OBJECTIVE' section at the top of your resume",
                "Write 2–3 sentences: who you are, your key skills, and what role you seek",
                "Mention your years of experience or education level upfront",
                "Tailor this section for each job application — reference the specific role",
                "Keep it under 60 words — recruiters spend only 6 seconds on first scan",
            ],
            example_improvement=(
                "Add:\n"
                "PROFESSIONAL SUMMARY\n"
                "Full-stack developer with 2+ years of experience building scalable "
                "web applications using React, Node.js, and AWS. Passionate about "
                "clean architecture and performance optimization."
            ),
        ))

    return detected




# This utility fn creates a summary list of issue titles from detailed issue objects
# Here detected_issues is a list of IssueDetail objects.
def generate_issues_summary(detected_issues: List[IssueDetail]) -> List[str]:
    """Extract issue titles to formulate the issues_summary list."""
    return [issue.issue_title for issue in detected_issues]



