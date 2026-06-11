# So this file will only be used when user will upload both resume & JD for matching
# Here inside this file, we will perform the resume skills matching with JD skills matching & return how many skills matched & how many not.


# here we are importing this Dict, List from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import Dict, List

# Here we are importing the fuzz module from the RapidFuzz library
# RapidFuzz is a fast string matching and fuzzy search library for Python. Similar to fuzzywuzzy, but optimized for speed and lower memory usage. Useful when comparing text for similarity — e.g., matching resume skills against job description keywords.
from rapidfuzz import fuzz
# The fuzz module provides functions to calculate similarity scores between strings. Some common ones:
# fuzz.ratio(str1, str2) :-  Compares two strings and returns a similarity score (0–100).
# fuzz.partial_ratio(str1, str2) :- Compares substrings — useful if one string is contained within another.
# fuzz.token_sort_ratio(str1, str2)  :- Ignores word order by sorting tokens before comparison.
# fuzz.token_set_ratio(str1, str2) :- Ignores duplicate words and compares sets of tokens.



# Here it is a Python dictionary called SKILL_ALIASES.
# Keys = alternate spellings, abbreviations, or shorthand for skills.
# Values = canonical/normalized names you want to use consistently.
# The type hint Dict[str, str] means: keys and values are both strings.
SKILL_ALIASES: Dict[str, str] = {
    'reactjs':       'react',
    'react.js':      'react',
    'angularjs':     'angular',
    'vuejs':         'vue',
    'vue.js':        'vue',
    'nextjs':        'next.js',
    'nodejs':        'node.js',
    'node':          'node.js',
    'expressjs':     'express',
    'express.js':    'express',
    'springboot':    'spring boot',
    'golang':        'go',
    'ml':            'machine learning',
    'ai':            'artificial intelligence',
    'nlp':           'natural language processing',
    'cv':            'computer vision',
    'k8s':           'kubernetes',
    'sklearn':       'scikit-learn',
    'postgres':      'postgresql',
    'dotnet':        '.net',
    'tailwindcss':   'tailwind',
    'amazon web services': 'aws',
    'google cloud':  'gcp',
    'pyspark':       'spark',
    'huggingface':   'hugging face',
}



def normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()

    # .get(key, default) → tries to find cleaned in the dictionary: If found → returns the canonical name. Example: "reactjs" → "react".
    # If not found → returns the original cleaned string. Example: "tensorflow" → "tensorflow" (unchanged, since not in aliases).
    return SKILL_ALIASES.get(cleaned, cleaned)




# threshold: minimum similarity score (default = 80) for considering two keywords a match.
# Output: a dictionary mapping resume keywords to lists of JD keywords they match.
def fuzzy_match_keywords(resume_keywords: List[str], jd_keywords: List[str], threshold: int = 80) -> Dict[str, List[str]]:
    # Loops through each keyword in resume_keywords. Passes it through normalize_skill (which lowercases and maps aliases like "reactjs" → "react").
    # Builds a dictionary:
    # Key = normalized skill (canonical form).
    # Value = original skill string from the resume.
    # e.g resume_keywords = ["ReactJS", "ML"] then, resume_normalized = {"react": "ReactJS", "machine learning": "ML"}
    resume_normalized = {normalize_skill(kw): kw for kw in resume_keywords}
    jd_normalized = {normalize_skill(kw): kw for kw in jd_keywords}

    matched_jd_originals = []
    missing_jd_originals = []

    # This loop checks each JD skill against resume skills. If there’s an exact normalized match, it’s marked as matched. Otherwise, it uses fuzzy string similarity (fuzz.token_sort_ratio) to see if the JD skill is close enough to a resume skill. If the similarity score passes the threshold, it’s matched; otherwise, it’s marked missing.
    for jd_canon, jd_original in jd_normalized.items():
        # 1. Exact canonical match
        if jd_canon in resume_normalized:
            # If the canonical JD skill is exactly present in the resume’s normalized skills, it’s a direct match.
            matched_jd_originals.append(jd_original)
            continue

        # 2. Fuzzy match against all resume canonical names
        best_score = 0

        for resume_canon in resume_normalized:
            score = fuzz.token_sort_ratio(jd_canon, resume_canon)
            best_score = max(best_score, score)

        if best_score >= threshold:
            matched_jd_originals.append(jd_original)
        else:
            missing_jd_originals.append(jd_original)


    return {
        'matched': sorted(matched_jd_originals),
        'missing': missing_jd_originals,
    }