import os
import fitz

from ai_quiz_generator import generate_ai_mcqs


pdf_folder = "../uploads"

all_text = ""

for filename in os.listdir(pdf_folder):

    if filename.lower().endswith(".pdf"):

        file_path = os.path.join(
            pdf_folder,
            filename
        )

        document = fitz.open(file_path)

        for page in document:
            all_text += page.get_text() + "\n"

        document.close()


questions = generate_ai_mcqs(
    all_text,
    number_of_questions=5
)

print("\nAI GENERATED QUIZ")
print("-----------------")

for question in questions:
    print(f"\n{question['question_number']}. {question['question']}")

    for option in question["options"]:
        print(f"   - {option}")

    print(f"Correct Answer: {question['correct_answer']}")