# -----------------------------
# Analyze Weak Concepts
# -----------------------------

def detect_weak_concepts(results):
    """
    Identify questions that the student
    answered incorrectly.
    """

    weak_concepts = []

    for result in results:

        if not result["correct"]:

            weak_concepts.append({
                "question": result.get("question"),
                "status": "Needs Revision"
            })

    return weak_concepts