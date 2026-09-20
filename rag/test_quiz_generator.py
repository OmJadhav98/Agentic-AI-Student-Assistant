from quiz_generator import generate_mcqs


study_text = """
A data structure is a specialized format for organizing and storing data.
An array stores elements in contiguous memory locations.
A linked list consists of nodes where each node contains data and a reference.
A stack follows the Last In First Out principle.
A queue follows the First In First Out principle.
A binary tree is a tree data structure where each node has at most two children.
"""


mcqs = generate_mcqs(study_text, 5)

print("Generated MCQs:", len(mcqs))

for mcq in mcqs:
    print("\nQuestion", mcq["question_number"])
    print(mcq["question"])

    for i, option in enumerate(mcq["options"], start=1):
        print(f"{i}. {option}")

    print("Correct Answer:", mcq["correct_answer"])