import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash"

PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "education": {"type": "string"},
        "location": {"type": "string"},
        "skills": {"type": "array", "items": {"type": "string"}},
        "interests": {"type": "array", "items": {"type": "string"}},
        "experience": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "education", "location", "skills", "interests", "experience"]
}


def normalize(value: str) -> str:
    value = value.lower().strip()
    aliases = {
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "postgres": "postgresql",
        "reactjs": "react",
        "nodejs": "node.js",
        "node": "node.js",
    }
    value = aliases.get(value, value)
    return re.sub(r"[^a-z0-9+#.\-]", "", value)


def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def extract_text_from_pdf(uploaded_file) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
    except Exception as e:
        raise RuntimeError(
            "Could not read this PDF. Make sure pypdf is installed."
        ) from e


def extract_profile(text: str) -> dict[str, Any]:
    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to .env locally "
            "or Streamlit Secrets when deployed."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are the Profile Intelligence Agent inside C4,
a career skill-gap-to-job matching platform.

Extract structured candidate information from the profile below.

Rules:
- Use ONLY information actually present.
- Never invent skills, education, experience, location, or projects.
- Normalize obvious variations such as ReactJS -> React.
- Keep skills short and useful for job matching.
- If information is missing, use an empty string or empty array.
- Return only the requested JSON.

PROFILE:
{text}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=PROFILE_SCHEMA,
                max_output_tokens=900,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return json.loads(response.text)

    except Exception as e:
        error_text = str(e)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise RuntimeError(
                "Gemini quota is currently exhausted. "
                "Use Demo Mode for the hackathon demo or wait for the quota to reset."
            ) from e

        raise RuntimeError(
            f"Gemini request failed: {error_text}"
        ) from e


def calculate_match(candidate_skills, required_skills):
    candidate = {normalize(x) for x in candidate_skills if x}
    required = {normalize(x) for x in required_skills if x}

    matched = candidate & required
    missing = required - candidate

    score = round((len(matched) / len(required)) * 100) if required else 0

    return score, sorted(matched), sorted(missing)


def match_jobs(profile, jobs):
    results = []
    candidate_skills = profile.get("skills", [])

    for job in jobs:
        score, matched, missing = calculate_match(
            candidate_skills,
            job.get("required_skills", [])
        )

        results.append({
            **job,
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
        })

    return sorted(
        results,
        key=lambda item: item["match_score"],
        reverse=True
    )


def recommend_courses(skill_gaps, courses):
    missing = {normalize(skill) for skill in skill_gaps}
    recommendations = []

    for course in courses:
        course_skills = course.get("skills", [])
        overlap = missing & {
            normalize(skill) for skill in course_skills
        }

        if overlap:
            recommendations.append({
                **course,
                "skills": sorted(overlap),
                "_score": len(overlap),
            })

    recommendations.sort(
        key=lambda item: item["_score"],
        reverse=True
    )

    for item in recommendations:
        item.pop("_score", None)

    return recommendations


def analyze_candidate(candidate_text, jobs, courses):
    profile = extract_profile(candidate_text)
    matched_jobs = match_jobs(profile, jobs)

    skill_gaps = []
    seen = set()

    for job in matched_jobs[:5]:
        for skill in job["missing_skills"]:
            if skill not in seen:
                seen.add(skill)
                skill_gaps.append(skill)

    return {
        "profile": profile,
        "matched_jobs": matched_jobs[:6],
        "skill_gaps": skill_gaps,
        "recommended_courses": recommend_courses(
            skill_gaps, courses
        )[:8],
    }


def demo_result(jobs, courses):
    profile = {
        "name": "Roshan",
        "education": "B.Tech Computer Engineering",
        "location": "Ahmedabad",
        "skills": ["C", "Python", "SQL", "Streamlit", "Git"],
        "interests": [
            "Artificial Intelligence",
            "Backend Development",
            "Software Development"
        ],
        "experience": ["Academic projects", "Hackathon project"],
    }

    matched_jobs = match_jobs(profile, jobs)

    skill_gaps = []
    seen = set()

    for job in matched_jobs[:5]:
        for skill in job["missing_skills"]:
            if skill not in seen:
                seen.add(skill)
                skill_gaps.append(skill)

    return {
        "profile": profile,
        "matched_jobs": matched_jobs[:6],
        "skill_gaps": skill_gaps,
        "recommended_courses": recommend_courses(
            skill_gaps, courses
        )[:8],
    }
