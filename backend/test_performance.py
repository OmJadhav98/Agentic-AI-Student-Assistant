from performance import calculate_performance


results = [
    {"topic": "CNN", "correct": True},
    {"topic": "CNN", "correct": True},
    {"topic": "CNN", "correct": False},
    {"topic": "Data Structures", "correct": True},
    {"topic": "Data Structures", "correct": False},
]


performance = calculate_performance(results)


print("Overall Performance")
print("-------------------")
print("Total Questions:", performance["total_questions"])
print("Correct Answers:", performance["correct_answers"])
print("Incorrect Answers:", performance["incorrect_answers"])
print("Score:", performance["score_percentage"], "%")


print("\nTopic-wise Performance")
print("----------------------")

for topic, data in performance["topic_performance"].items():
    print(
        topic,
        "->",
        data["score_percentage"],
        "%",
        "| Attempted:",
        data["attempted"],
        "| Correct:",
        data["correct"]
    )