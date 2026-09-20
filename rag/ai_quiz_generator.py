import os
import json

from dotenv import load_dotenv
from google import genai


# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )

client = genai.Client(
    api_key=api_key
)


# -----------------------------
# Generate AI Quiz
# -----------------------------

def generate_ai_mcqs(
    text,
    number_of_questions=5
):
    """
    Generate meaningful MCQs from the
    provided study material using Gemini.
    """

    # Limit context size
    text = text[:30000]

    prompt = f"""
You are an educational quiz generator.

Generate exactly {number_of_questions}
multiple-choice questions ONLY from the
study material provided below.

Rules:
1. Questions must test understanding
   of the study material.
2. Each question must have exactly 4 options.
3. Only one option must be correct.
4. Do not use information outside
   the provided material.
5. Keep questions clear and suitable
   for a college student.
6. Return ONLY valid JSON.
7. Do not include markdown or ```json.

Return this exact structure:

[
  {{
    "question_number": 1,
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_answer": "Option A"
  }}
]

STUDY MATERIAL:
{text}
"""

    try:

        # Ask Gemini to generate questions
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        response_text = response.text.strip()

        if not response_text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        # -----------------------------
        # Remove Markdown Code Blocks
        # -----------------------------

        if response_text.startswith("```"):

            response_text = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # -----------------------------
        # Parse JSON
        # -----------------------------

        questions = json.loads(
            response_text
        )

        # -----------------------------
        # Validate Response
        # -----------------------------

        if not isinstance(questions, list):
            raise ValueError(
                "AI response is not a list of questions."
            )

        for question in questions:

            required_fields = [
                "question_number",
                "question",
                "options",
                "correct_answer"
            ]

            for field in required_fields:

                if field not in question:
                    raise ValueError(
                        f"Missing field: {field}"
                    )

            if len(question["options"]) != 4:
                raise ValueError(
                    "Each question must have exactly 4 options."
                )

        return questions

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        )

    except Exception as e:

        raise ValueError(
            f"Quiz generation failed: {e}"
        )