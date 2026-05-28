from rank_bm25 import BM25Okapi

from app.services.chroma_service import (
    collection,
    search_documents
)

def keyword_search(
    query: str,
    top_k: int = 3
):

    all_documents = collection.get()

    documents = all_documents["documents"]

    if not documents:
        return []

    tokenized_docs = [
        doc.lower().split()
        for doc in documents
    ]

    bm25 = BM25Okapi(
        tokenized_docs
    )

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked_results = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    formatted_results = []

    for doc, score in ranked_results[:top_k]:

        formatted_results.append({
            "text": doc,
            "keyword_score": float(score)
        })

    return formatted_results


def hybrid_search(
    query: str,
    top_k: int = 3,
    filters: dict = None
):

    semantic_results = search_documents(
        query=query,
        top_k=top_k,
        filters=filters
    )

    keyword_results = keyword_search(
        query=query,
        top_k=top_k
    )

    combined_results = {
        item["text"]: item
        for item in semantic_results
    }

    for item in keyword_results:

        if item["text"] not in combined_results:

            combined_results[item["text"]] = item

    return list(
        combined_results.values()
    )