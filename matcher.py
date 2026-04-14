# Compares a resume against a job description.
# Two signals: TF-IDF cosine similarity on the raw text, and
# how many of the job's listed skills appear on the resume.
# Combined into one overall compatibility score.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import compare_skills, extract_skills


# Weights for combining the two scores.
# Skill overlap matters more to us than general text similarity,
# so skill_score gets weighted higher. We might tune this later
# once the feedback-learning feature is in.
SKILL_WEIGHT = 0.7
TEXT_WEIGHT = 0.3


def compute_text_similarity(resume_text, job_text):
    """
    TF-IDF + cosine similarity between the two documents.
    Returns a float between 0 and 1.
    """
    if not resume_text or not job_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf = vectorizer.fit_transform([resume_text, job_text])
    except ValueError:
        # Can happen if both docs are empty after stop words are removed.
        return 0.0

    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return float(sim)


def compute_skill_score(resume_skills, job_skills):
    """
    Fraction of the job's skills that the resume covers.
    Returns 0 if the job lists no recognized skills.
    """
    if not job_skills:
        return 0.0
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    return len(resume_set & job_set) / len(job_set)


def match_resume_to_job(resume_text, job_text):
    """
    Runs the full comparison and returns everything the UI needs.
    """
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    matched, missing = compare_skills(resume_skills, job_skills)

    text_sim = compute_text_similarity(resume_text, job_text)
    skill_score = compute_skill_score(resume_skills, job_skills)
    overall = (SKILL_WEIGHT * skill_score) + (TEXT_WEIGHT * text_sim)

    return {
        'resume_skills': resume_skills,
        'job_skills': job_skills,
        'matched_skills': matched,
        'missing_skills': missing,
        'text_similarity': text_sim,
        'skill_score': skill_score,
        'overall_score': overall,
    }
