# from rank_bm25 import BM25Okapi

# from app.services.chroma_service import (
#     collection,
#     search_documents
# )

# def keyword_search(
#     query: str,
#     top_k: int = 3
# ):

#     all_documents = collection.get()

#     documents = all_documents["documents"]

#     if not documents:
#         return []

#     tokenized_docs = [
#         doc.lower().split()
#         for doc in documents
#     ]

#     bm25 = BM25Okapi(
#         tokenized_docs
#     )

#     tokenized_query = query.lower().split()

#     scores = bm25.get_scores(
#         tokenized_query
#     )

#     ranked_results = sorted(
#         zip(documents, scores),
#         key=lambda x: x[1],
#         reverse=True
#     )

#     formatted_results = []

#     for doc, score in ranked_results[:top_k]:

#         formatted_results.append({
#             "text": doc,
#             "keyword_score": float(score)
#         })

#     return formatted_results


# def hybrid_search(
#     query: str,
#     top_k: int = 3,
#     filters: dict = None
# ):

#     semantic_results = search_documents(
#         query=query,
#         top_k=top_k,
#         filters=filters
#     )

#     keyword_results = keyword_search(
#         query=query,
#         top_k=top_k
#     )

#     combined_results = {
#         item["text"]: item
#         for item in semantic_results
#     }

#     for item in keyword_results:

#         if item["text"] not in combined_results:

#             combined_results[item["text"]] = item

#     return list(
#         combined_results.values()
#     )

from rank_bm25 import BM25Okapi
from app.services.chroma_service import (
    get_tenant_collection,  # 🔥 Use this to isolate keyword search too
    search_documents
)

def keyword_search(
    tenant_id: str,         # 🔥 Enforced tenant context boundary
    query: str,
    top_k: int = 3
):
    """
    Performs BM25 keyword search explicitly restricted to a single 
    tenant's isolated document database space.
    """
    # Grab the specific workspace collection
    collection = get_tenant_collection(tenant_id)
    all_documents = collection.get()

    documents = all_documents["documents"]
    metadatas = all_documents["metadatas"] if "metadatas" in all_documents else None

    if not documents:
        return []

    tokenized_docs = [
        doc.lower().split()
        for doc in documents
    ]

    bm25 = BM25Okapi(tokenized_docs)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    # Track metadatas along with docs to preserve environment/service attributes for merging
    doc_meta_score = zip(documents, metadatas or [{}] * len(documents), scores)
    ranked_results = sorted(
        doc_meta_score,
        key=lambda x: x[2],
        reverse=True
    )

    formatted_results = []
    for doc, meta, score in ranked_results[:top_k]:
        formatted_results.append({
            "text": doc,
            "keyword_score": float(score),
            "metadata": meta
        })

    return formatted_results


def hybrid_search(
    tenant_id: str,         # 🔥 Enforced tenant context boundary
    query: str,
    top_k: int = 3,
    filters: dict = None
):
    """
    Blends tenant-isolated semantic vector results and tenant-isolated 
    BM25 keyword search results into a unified collection context list.
    """
    # 1. Fetch strictly bounded vector semantic search results
    semantic_results = search_documents(
        tenant_id=tenant_id,
        query=query,
        top_k=top_k,
        filters=filters
    )

    # 2. Fetch strictly bounded BM25 keyword search results
    keyword_results = keyword_search(
        tenant_id=tenant_id,
        query=query,
        top_k=top_k
    )

    # 3. Merge results gracefully by text lookup key
    combined_results = {
        item["text"]: item
        for item in semantic_results
    }

    for item in keyword_results:
        if item["text"] not in combined_results:
            combined_results[item["text"]] = {
                "text": item["text"],
                "distance": 1.0,  # Fallback vector placeholder metric distance
                "metadata": item.get("metadata", {})
            }

    return list(combined_results.values())