import re
from collections import Counter


def extract_questions(text):
    """
    Extract questions from PYQ text.
    Looks for numbered questions such as:
    1. ...
    2. ...
    Q1. ...
    """

    pattern = r"(?:^|\n)\s*(?:Q(?:uestion)?\s*)?(\d+)[.)]\s*(.+?)(?=\n\s*(?:Q(?:uestion)?\s*)?\d+[.)]|\Z)"

    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    questions = []

    for number, question in matches:
        question = " ".join(question.split())

        if len(question) > 10:
            questions.append({
                "question_number": int(number),
                "question": question
            })

    return questions


def extract_keywords(question):
    """
    Extract simple keywords from a question.
    """

    stop_words = {
        "what", "is", "are", "the", "of", "in", "a", "an",
        "and", "or", "to", "for", "on", "with", "explain",
        "define", "describe", "discuss", "how", "why",
        "which", "write", "about"
    }

    words = re.findall(r"[A-Za-z]+", question.lower())

    keywords = [
        word for word in words
        if len(word) > 3 and word not in stop_words
    ]

    return keywords


def analyze_pyq(text):
    """
    Analyze PYQ text and identify frequently occurring keywords.
    """

    questions = extract_questions(text)

    all_keywords = []

    for item in questions:
        keywords = extract_keywords(item["question"])
        all_keywords.extend(keywords)

    keyword_frequency = Counter(all_keywords)

    return {
        "total_questions": len(questions),
        "questions": questions,
        "important_keywords": keyword_frequency.most_common(10)
    }