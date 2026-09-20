from weak_topic import detect_weak_topics


topic_performance = {
    "CNN": {
        "attempted": 3,
        "correct": 2,
        "score_percentage": 66.67
    },
    "Data Structures": {
        "attempted": 2,
        "correct": 1,
        "score_percentage": 50.0
    }
}


weak_topics = detect_weak_topics(topic_performance)


print("Weak Topics")
print("-----------")

if weak_topics:
    for topic in weak_topics:
        print(
            topic["topic"],
            "->",
            topic["score_percentage"],
            "%",
            "| Status:",
            topic["status"]
        )
else:
    print("No weak topics found.")