import os

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


# -----------------------------
# Gemini Client
# -----------------------------

client = genai.Client(
    api_key=api_key
)


# -----------------------------
# Generate AI Answer
# -----------------------------

def generate_answer(question, context):
    """
    Generate an answer using the retrieved
    study material from the RAG pipeline.
    """

    prompt = f"""
You are a helpful academic assistant.

Answer the student's question using the
study material provided below.

Study Material:
{context}

Student Question:
{question}

Instructions:
- Answer clearly and simply.
- Use only the provided study material when possible.
- If the answer is not available in the study material,
  say that the information is not available in the
  provided material.
- Do not invent facts.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        return response.text.strip()

    except Exception as e:

        raise RuntimeError(
            f"AI answer generation failed: {e}"
        )