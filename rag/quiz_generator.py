import re
import random


def extract_sentences(text):
    """Extract useful sentences from study material."""

    sentences = re.split(r'(?<=[.!?])\s+', text)

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 30
    ]


def generate_mcqs(text, number_of_questions=5):
    """
    Generate basic MCQs from study material.
    """

    sentences = extract_sentences(text)

    if len(sentences) < number_of_questions:
        number_of_questions = len(sentences)

    selected_sentences = random.sample(sentences, number_of_questions)

    questions = []

    for index, sentence in enumerate(selected_sentences, start=1):

        words = re.findall(r'\b[A-Za-z]{4,}\b', sentence)

        if not words:
            continue

        correct_answer = random.choice(words)

        options = [correct_answer]

        other_words = [
            word for word in words
            if word.lower() != correct_answer.lower()
        ]

        random.shuffle(other_words)

        for word in other_words:
            if word not in options:
                options.append(word)

            if len(options) == 4:
                break

        while len(options) < 4:
            options.append("None of these")

        random.shuffle(options)

        questions.append({
            "question_number": index,
            "question": f"Which term appears in this statement?\n{sentence}",
            "options": options,
            "correct_answer": correct_answer
        })

    return questions