import os

from google import genai


# -----------------------------
# Detect Subject from Study Material
# -----------------------------

def detect_subject(text):
    """
    Detect the main academic subject
    from uploaded study material.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Unknown Subject"

    try:

        client = genai.Client(
            api_key=api_key
        )

        prompt = f"""
You are an academic subject classifier.

Read the following study material and identify
the main academic subject.

Return ONLY the subject name.
Do not give explanations.
Do not include punctuation.

Examples:
Database Management System
Data Structures
Machine Learning
Deep Learning
Computer Vision
Big Data
Data Analytics

Study Material:
{text[:12000]}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        subject = response.text.strip()

        if not subject:
            return "Unknown Subject"

        return subject

    except Exception:
        return "Unknown Subject"