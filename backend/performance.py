# -----------------------------
# Calculate Quiz Performance
# -----------------------------

def calculate_performance(results):
    """
    Calculate a student's quiz performance.

    Each result should contain:

    {
        "topic": "...",
        "correct": True/False
    }
    """

    # No quiz results
    if not results:
        return {
            "total_questions": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "score_percentage": 0,
            "topic_performance": {}
        }

    # -----------------------------
    # Overall Performance
    # -----------------------------

    total_questions = len(results)

    correct_answers = sum(
        1
        for result in results
        if result["correct"]
    )

    incorrect_answers = (
        total_questions - correct_answers
    )

    score_percentage = round(
        (correct_answers / total_questions) * 100,
        2
    )

    # -----------------------------
    # Topic-wise Performance
    # -----------------------------

    topic_scores = {}

    for result in results:

        topic = result["topic"]

        if topic not in topic_scores:
            topic_scores[topic] = []

        topic_scores[topic].append(
            1 if result["correct"] else 0
        )

    topic_performance = {}

    for topic, scores in topic_scores.items():

        attempted = len(scores)
        correct = sum(scores)

        percentage = round(
            (correct / attempted) * 100,
            2
        )

        topic_performance[topic] = {
            "attempted": attempted,
            "correct": correct,
            "score_percentage": percentage
        }

    # -----------------------------
    # Final Result
    # -----------------------------

    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "score_percentage": score_percentage,
        "topic_performance": topic_performance
    }