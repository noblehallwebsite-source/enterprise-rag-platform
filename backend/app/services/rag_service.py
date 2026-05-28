# from app.services.chroma_service import (
#     search_documents
# )

from app.services.hybrid_search_service import (
    hybrid_search
)

from app.services.ai_service import (
    generate_ai_response
)

from app.services.rerank_service import (
    rerank_documents
)

def run_rag_pipeline(query: str, filters: dict = None):

#     retrieved_docs = search_documents(
#         query=query,
#         top_k=3,
#         filters=filters
#     )

    retrieved_docs = hybrid_search(
        query=query,
        top_k=10,
        filters=filters
    )

    reranked_docs = rerank_documents(
        query=query,
        documents=retrieved_docs,
        top_k=3
    )

    context = "\n".join([
        item["text"]
        for item in reranked_docs
    ])

    augmented_prompt = f"""
Use the provided enterprise context
to answer the user's question.

Context:
{context}

Question:
{query}
"""

    ai_answer = generate_ai_response(
        augmented_prompt
    )

    return {
        "query": query,
        "retrieved_context": reranked_docs,
        "ai_answer": ai_answer
    }