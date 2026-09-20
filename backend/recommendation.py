# -----------------------------
# Generate Study Recommendations
# -----------------------------

def generate_recommendations(weak_topics):
    """
    Generate personalized study recommendations
    based on the student's weak topics.
    """

    recommendations = []

    for topic in weak_topics:

        subject = topic["topic"]
        score = topic["score_percentage"]

        # -----------------------------
        # High Priority
        # -----------------------------

        if score < 40:

            priority = "High"

            message = (
                f"Focus strongly on {subject}. "
                f"Revise the study material and "
                f"practice more questions."
            )

        # -----------------------------
        # Medium Priority
        # -----------------------------

        elif score < 60:

            priority = "Medium"

            message = (
                f"Revise {subject} and "
                f"practice additional questions."
            )

        # -----------------------------
        # Low Priority
        # -----------------------------

        else:

            priority = "Low"

            message = (
                f"Do a quick revision of {subject}."
            )

        recommendations.append({
            "topic": subject,
            "score_percentage": score,
            "priority": priority,
            "recommendation": message
        })

    return recommendations