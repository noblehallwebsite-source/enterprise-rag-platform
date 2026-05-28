from app.services.embedding_service import (
    calculate_similarity
)

def evaluate_grounding(
    answer: str,
    retrieved_documents: list
):

    if not retrieved_documents:

        return {
            "grounding_score": 0.0,
            "grounded": False
        }

    similarities = []

    for document in retrieved_documents:

        score = calculate_similarity(
            answer,
            document["text"]
        )

        similarities.append(score)

    max_similarity = max(similarities)

    return {
        "grounding_score": float(
            max_similarity
        ),
        "grounded": max_similarity > 0.5
    }