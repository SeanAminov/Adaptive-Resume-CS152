# Pulls skills out of resume/job-description text.
# Matches text against the alias dictionary and returns the canonical
# (normalized) skill names.

import re

from skills_data import SKILL_ALIASES


def extract_skills(text):
    """
    Find every skill we recognize in the text.
    Returns a sorted list of canonical skill names (no duplicates).
    """
    if not text:
        return []

    # Work in lowercase so matching is case-insensitive.
    # We'll also blank out skills as we find them so that shorter
    # aliases (like "c") don't accidentally match inside a longer
    # skill we've already counted (like "c++").
    working_text = text.lower()
    found = set()

    # Match longer aliases first. If we look for "machine learning"
    # before "ml", we avoid double-counting.
    aliases_sorted = sorted(SKILL_ALIASES.keys(), key=len, reverse=True)

    for alias in aliases_sorted:
        # Custom boundaries using lookaround so things like "C++" and
        # "C#" still match (regular \b doesn't treat + or # as word
        # characters, which breaks those).
        pattern = r'(?<!\w)' + re.escape(alias) + r'(?!\w)'
        if re.search(pattern, working_text):
            found.add(SKILL_ALIASES[alias])
            # Wipe out the match so it can't be re-matched by a shorter alias.
            working_text = re.sub(pattern, ' ', working_text)

    return sorted(found)


def compare_skills(resume_skills, job_skills):
    """
    Given two skill lists, return (matched, missing) where matched is
    the skills both sides have and missing is what the job wants but
    the resume doesn't have.
    """
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)
    return matched, missing
