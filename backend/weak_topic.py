# -----------------------------
# Detect Weak Topics
# -----------------------------

def detect_weak_topics(
    topic_performance,
    threshold=60
):
    """
    Identify topics where the student's
    score is below the given threshold.

    Default threshold: 60%
    """

    weak_topics = []

    for topic, data in topic_performance.items():

        score = data["score_percentage"]

        if score < threshold:

            weak_topics.append({
                "topic": topic,
                "score_percentage": score,
                "attempted": data["attempted"],
                "correct": data["correct"],
                "status": "Weak"
            })

    # Lowest-scoring topics first
    weak_topics.sort(
        key=lambda item: item["score_percentage"]
    )

    return weak_topics