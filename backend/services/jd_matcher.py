# Here in this folder, we will create different files which will contain the core logic or business logic of our project. 
# Like here we have created this 'jd_matcher.py' file to write the logic for matching the resume with the given JD.
# Like how our text gets extracted from the resume, what feedback & recommendations this project will give to user, etc, all that logic will be written here in this services folder.

# So inside this services folder, we will write the business logic for all the layers & for that we will create separate files for each layer like ats_scorer.py for ATS scoring logic, feedback_engine.py for feedback & recommendation logic, pdf_export.py for PDF export logic, resume_analyzer.py for resume analysis logic, etc. This way we can keep our code organized and modular. We can also easily test each layer separately by writing unit tests for each file. This way we can ensure that our code is working correctly and we can easily maintain it in the future.
# SO It will also help to maintain that each of these layers are independent of each other, so if we want to change the logic of one layer, it will not affect the other layers. This way we can easily update our code in the future without worrying about breaking other parts of the code. 
# So in this way, each layers will not know anything about the other layers actually.


# SO this file will only be used when user uploaded both resume & JD, & then this file is used to match the resume with JD using the Fine Tune BERT model which we created in the '3_BERT_FINE_TUNE_model' jupyter notebook & stored that model in this 'ml bert model' folder


# here we are importing this Dict, List from the typing module to use them in our code for type hinting. This way we can easily identify the types of the variables and also we can easily debug our application by looking at the type hints in our code. This way we can keep our code organized and modular by using type hints in our code. We will write all the logging related code in this file only, so that we can keep our code organized and modular.
from typing import List, Dict
import numpy as np

# here we are importing spacy also
import spacy

# SentenceTransformer (from sentence-transformers) :- A class that loads pre‑trained transformer models (like BERT variants) specialized for generating sentence embeddings.
# Embeddings = numerical vector representations of text that capture semantic meaning.
# model = SentenceTransformer('all-MiniLM-L6-v2')    # it will load this BERT model
# embedding = model.encode("I love playing cricket")
from sentence_transformers import SentenceTransformer

# Here we are importing these functions from utils folder actually
from backend.utils.matching import fuzzy_match_keywords, normalize_skill

# Here we are importing the fuzz module from the RapidFuzz library
# RapidFuzz is a fast string matching and fuzzy search library for Python. Similar to fuzzywuzzy, but optimized for speed and lower memory usage. Useful when comparing text for similarity — e.g., matching resume skills against job description keywords.
from rapidfuzz import fuzz
# The fuzz module provides functions to calculate similarity scores between strings. Some common ones:
# fuzz.ratio(str1, str2) :-  Compares two strings and returns a similarity score (0–100).
# fuzz.partial_ratio(str1, str2) :- Compares substrings — useful if one string is contained within another.
# fuzz.token_sort_ratio(str1, str2)  :- Ignores word order by sorting tokens before comparison.
# fuzz.token_set_ratio(str1, str2) :- Ignores duplicate words and compares sets of tokens.



# It is a utility function to measure how semantically similar a resume is to a job description using embeddings.
# embedder: SentenceTransformer → a pre‑trained or fine‑tuned SentenceTransformer model that can convert text into embeddings.
# So here type of this embedder is SentenceTransformer model actually. so in this embedder, we will store our fine tune model.
def calculate_semantic_similarity(resume_text: str, jd_text: str, embedder: SentenceTransformer) -> float:
    # Here when we call this fn, we will pass our fine tune model as this embedder actually.
    # converts text into a numerical vector (embedding) that captures semantic meaning.
    # convert_to_tensor=False → returns a NumPy array instead of a PyTorch tensor (so you can use NumPy operations directly).
    resume_emb = embedder.encode(resume_text[:5000], convert_to_tensor=False)
    jd_emb  = embedder.encode(jd_text[:5000], convert_to_tensor=False)


    # Dot product: np.dot(resume_emb, jd_emb) → measures how aligned the two vectors are.
    # Norms: np.linalg.norm(...) → computes the magnitude (length) of each vector.
    # Formula: cosine similarity(𝐴 , 𝐵) = (𝐴 ⋅ 𝐵) / (∥𝐴∥⋅ ∥𝐵∥)
    similarity = np.dot(resume_emb, jd_emb) / ( np.linalg.norm(resume_emb) * np.linalg.norm(jd_emb) )   # Cosine similarity calculation
    
    # np.clip(similarity, 0.0, 1.0) → restricts the similarity score to the range [0, 1]. Ensures you don’t get negative values (which aren’t meaningful in this context). Converts the result to a plain Python float for easier handling
    return float(np.clip(similarity, 0.0, 1.0))




def identify_matched_keywords(resume_keywords: List[str], jd_keywords: List[str]) -> List[str]:
    result = fuzzy_match_keywords(resume_keywords, jd_keywords, threshold=80)
    
    return result['matched']



def identify_missing_keywords(resume_keywords: List[str], jd_keywords: List[str], top_n: int = 15) -> List[str]:
    result = fuzzy_match_keywords(resume_keywords, jd_keywords, threshold=80)
    
    return result['missing'][:top_n]   # here we are only returning top_n amount of missing keywords if mising keywords are larger then top_n




# spaCy is a leading open‑source Python library for advanced Natural Language Processing (NLP), designed for production use. It provides fast, accurate tools for text processing, including tokenization, part‑of‑speech tagging, dependency parsing, and named entity recognition.
# resume_skills: a list of skills extracted from the candidate’s resume. jd_text: the raw job description text.
# nlp: a spaCy language model (e.g., en_core_web_sm, en_core_web_md) used for NLP processing.
# Output: a list of strings (skills that are missing in the resume compared to the JD).
def analyze_skills_gap(resume_skills: List[str], jd_text: str, nlp: spacy.Language) -> List[str]:
    # Passes the first 5000 characters of the job description into the spaCy pipeline.
    # doc is a spaCy Doc object containing tokens, entities, and linguistic annotations. Truncation ([:5000]) prevents memory overload if the JD is very long.
    doc = nlp(jd_text[:5000])
    jd_skills = set()     # Creates an empty set to store unique skills extracted from the JD.


    # doc.ents → spaCy’s list of named entities detected in the job description text.
    # Each ent has:
    # ent.text → the actual text span (e.g., "Python", "AWS", "Docker").
    # ent.label_ → the entity type (e.g., ORG for organizations, PRODUCT for products, LANGUAGE for programming languages).
    # If the entity type is one of PRODUCT, ORG, or LANGUAGE, it’s likely a skill/technology.
    # Adds the lowercase version of the entity text to jd_skills.
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
            jd_skills.add(ent.text.lower())


    # doc.noun_chunks → spaCy’s noun phrase extractor (groups of words functioning as nouns).
    # Example noun chunks: "machine learning", "data analysis", "cloud computing".
    # Converts each chunk to lowercase and strips whitespace.
    # Filters: only keep chunks with 1–4 words (to avoid very long phrases that aren’t skills).
    # Adds them to jd_skills.
    for chunk in doc.noun_chunks:
        ct = chunk.text.lower().strip()
        if 1 <= len(ct.split()) <= 4:
            jd_skills.add(ct)
    # JD text: "Strong background in machine learning and data analysis."  
    # Noun chunks: "background", "machine learning", "data analysis"  → "machine learning" and "data analysis" added to jd_skills.


    # Normalize resume skills for comparison
    resume_normalized = {normalize_skill(s) for s in resume_skills}

    gap = []

    for jd_skill in jd_skills:
        jd_norm = normalize_skill(jd_skill)

        # Check canonical match first
        if jd_norm in resume_normalized:
            continue

        # Then try fuzzy match against all resume skills
        # (fuzz.token_sort_ratio(jd_norm, rs) for rs in resume_normalized) :- Loops through every rs (resume skill, normalized) in resume_normalized. For each one, computes a similarity score with the job description skill jd_norm using:
        # fuzz.token_sort_ratio → compares two strings by sorting their tokens before measuring similarity. Example: "machine learning" vs "learning machine" → 100 (perfect match). Produces a stream of similarity scores (e.g., [92, 85, 100, 67]).
        # Takes the highest similarity score from the generator. default=0 ensures that if resume_normalized is empty, best_score will safely be 0 instead of causing an error.
        best_score = max((fuzz.token_sort_ratio(jd_norm, rs) for rs in resume_normalized), default = 0)
        
        if best_score < 75:
            gap.append(jd_skill)

    return sorted(gap)[:20]





# This function is designed to compute an overall match percentage between a resume and a job description by combining keyword overlap and semantic similarity.
def calculate_match_percentage(resume_keywords: List[str], jd_keywords: List[str], semantic_similarity: float) -> float:
    if not jd_keywords:   # If the JD has no keywords, the function returns 0.0 immediately (no basis for comparison).
        return 0.0
    
    matched = identify_matched_keywords(resume_keywords, jd_keywords)

    keyword_overlap = len(matched) / len(jd_keywords)

    # Keyword overlap (60%) → direct skill matching. Semantic similarity (40%) → overall textual similarity.
    match_pct = (keyword_overlap * 0.6 + semantic_similarity * 0.4) * 100

    return float(np.clip(match_pct, 0.0, 100.0))




# embedder: a SentenceTransformer model for semantic similarity.
# nlp: a spaCy language model for skill extraction.
def compare_resume_with_jd(resume_text: str, resume_keywords: List[str], resume_skills: List[str], jd_text: str, jd_keywords: List[str], embedder: SentenceTransformer, nlp: spacy.Language) -> Dict:
    semantic_similarity = calculate_semantic_similarity(resume_text, jd_text, embedder)

    matched_keywords    = identify_matched_keywords(resume_keywords, jd_keywords)
    missing_keywords    = identify_missing_keywords(resume_keywords, jd_keywords)
    skills_gap          = analyze_skills_gap(resume_skills, jd_text, nlp)
    
    match_percentage    = calculate_match_percentage(
        resume_keywords, jd_keywords, semantic_similarity
    )

    return {
        'match_percentage':    match_percentage,
        'semantic_similarity': semantic_similarity,
        'matched_keywords':    matched_keywords,
        'missing_keywords':    missing_keywords,
        'skills_gap':          skills_gap,
    }





#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Text Embeddings And cosine similarity :- 
# An embedding is a numerical vector representation of text (word, sentence, or document).
# Captures semantic meaning so that similar texts have similar vectors.
# So we will use Transformer models (BERT, SentenceTransformers) to create them.

# Cosine Similarity is a metric to measure how similar two vectors are, based on the angle between them.
# 1 → vectors point in the same direction (high similarity).
# 0 → vectors are orthogonal (no similarity).
# -1 → vectors point in opposite directions (rare in embeddings).
# cosine similarity(𝐴,𝐵) = (𝐴 ⋅ 𝐵) / ∥ 𝐴 ∥ ⋅ ∥ 𝐵 ∥



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# BERT :-
# BERT (Bidirectional Encoder Representations from Transformers) is a landmark NLP model introduced by Google in 2018 that reads text bidirectionally, enabling deep contextual understanding and achieving state‑of‑the‑art results across many language tasks. 
# It revolutionized how machines process language by pre‑training on massive text corpora and then fine‑tuning for specific tasks like question answering, sentiment analysis, and named entity recognition.

# What BERT Is :-
# Full Form: Bidirectional Encoder Representations from Transformers.
# Type: Transformer‑based language representation model.
# Introduced by: Google AI Language team (Jacob Devlin et al., 2018).
# Core Idea: Unlike older models that read text left‑to‑right or right‑to‑left, BERT reads both directions simultaneously, capturing richer context.

# How BERT Works :-
# Pre‑training on large datasets (Wikipedia + BookCorpus).
# Masked Language Model (MLM): Random words are masked, and BERT predicts them using surrounding context.
# Next Sentence Prediction (NSP): Learns whether one sentence logically follows another.
# Fine‑tuning: Once pre‑trained, BERT can be adapted to specific tasks with minimal changes.
# Example: Add a classification layer for sentiment analysis.
# Example: Add a span prediction layer for question answering.

# Why BERT Matters :-
# Contextual power: Understands meaning based on surrounding words.
# Generalizability: One pre‑trained model can be fine‑tuned for many tasks.
# Foundation model: Inspired modern LLMs like GPT, T5, and beyond.

# SO if we have two words like AI & ML, then for python both are different & have different meaning but we know in terms of resume both are same only
# So we make use of BERT to detech that these are similar kind of words & then we increase their match score