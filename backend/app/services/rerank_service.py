from sklearn.metrics.pairwise import cosine_similarity

from app.services.embedding_service import (
    generate_embedding
)

def rerank_documents(
    query: str,
    documents: list,
    top_k: int = 3
):

    query_embedding = generate_embedding(
        query
    )

    reranked_results = []

    for document in documents:

        document_embedding = generate_embedding(
            document["text"]
        )

        similarity_score = cosine_similarity(
            [query_embedding],
            [document_embedding]
        )[0][0]

        document["rerank_score"] = float(
            similarity_score
        )

        reranked_results.append(
            document
        )

    reranked_results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked_results[:top_k]