# import chromadb
# from chromadb.config import Settings

# from app.services.embedding_service import (
#     generate_embedding
# )

# client = chromadb.PersistentClient(
#     path="/app/chroma_storage"
# )

# collection = client.get_or_create_collection(
#     name="enterprise_knowledge_base"
# )

# def add_document(
#     document_id: str,
#     text: str,
#     metadata: dict = None
# ):

#     embedding = generate_embedding(text)

#     collection.add(
#         ids=[document_id],
#         documents=[text],
#         embeddings=[embedding],
#         metadatas=[metadata or {}]
#     )

# def search_documents(
#     query: str,
#     top_k: int = 3,
#     filters: dict = None
# ):

#     query_embedding = generate_embedding(query)

#     # Filter preparation
#     where_clause = None
    
#     if filters:
#         # Strip out any keys that have None values
#         clean_filters = {k: v for k, v in filters.items() if v is not None}
        
#         if len(clean_filters) > 1:
#             # 🔥 FIX 2: Explicitly format multiple keys with ChromaDB's logical '$and' operator
#             where_clause = {
#                 "$and": [
#                     {key: value} 
#                     for key, value in clean_filters.items()
#                 ]
#             }
#         elif len(clean_filters) == 1:
#             where_clause = clean_filters

#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k,
#         where=where_clause  # Pass our safe where clause structure
#     )

#     # Defensive Guard: If Chroma DB returns completely empty results
#     if not results or not results["documents"] or not results["documents"][0]:
#         return []

#     formatted_results = []

#     documents = results["documents"][0]
#     distances = results["distances"][0]
#     metadatas = results["metadatas"][0]

#     for doc, distance, metadata in zip(
#         documents,
#         distances,
#         metadatas
#     ):
#         formatted_results.append({
#             "text": doc,
#             "distance": distance,
#             "metadata": metadata
#         })

#     return formatted_results

import chromadb
from chromadb.config import Settings

from app.services.embedding_service import (
    generate_embedding
)

# Persistent Client remains global across the application instance
client = chromadb.PersistentClient(
    path="/app/chroma_storage"
)

# =====================================================================
# STEP 2 & 3: REMOVED GLOBAL COLLECTION & ADDED TENANT HELPER
# =====================================================================
def get_tenant_collection(tenant_id: str):
    """
    Dynamically fetches or creates a dedicated, structurally isolated 
    ChromaDB collection for a specific enterprise tenant.
    """
    # Defensive cleanup to ensure names match ChromaDB formatting regulations (alphanumeric, underscores, hyphens)
    safe_tenant_id = str(tenant_id).strip().lower().replace("-", "_")
    collection_name = f"tenant_{safe_tenant_id}_docs"
    
    return client.get_or_create_collection(
        name=collection_name
    )


# =====================================================================
# STEP 4 & 5: TENANT-AWARE DOCUMENT INGESTION
# =====================================================================
def add_document(
    tenant_id: str,        # 🔥 Required parameter for tenant scope boundary
    document_id: str,
    text: str,
    metadata: dict = None
):
    """
    Generates text embeddings and routes the data payload exclusively to the 
    isolated vector workspace belonging to the specified tenant.
    """
    embedding = generate_embedding(text)

    # Resolve the isolated database layer boundary
    collection = get_tenant_collection(tenant_id)

    collection.add(
        ids=[document_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )


# =====================================================================
# STEP 6: TENANT-ISOLATED RETRIEVAL
# =====================================================================
def search_documents(
    tenant_id: str,        # 🔥 Enforced required boundary parameter
    query: str,
    top_k: int = 3,
    filters: dict = None
):
    """
    Queries exclusively within the specified tenant's collection space. 
    It is mathematically impossible to pull records from another client organization.
    """
    query_embedding = generate_embedding(query)

    # Resolve the correct collection target
    collection = get_tenant_collection(tenant_id)

    # Filter preparation
    where_clause = None
    
    if filters:
        # Strip out any keys that have None values
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        
        if len(clean_filters) > 1:
            # Explicitly format multiple keys with ChromaDB's logical '$and' operator
            where_clause = {
                "$and": [
                    {key: value} 
                    for key, value in clean_filters.items()
                ]
            }
        elif len(clean_filters) == 1:
            where_clause = clean_filters

    # Execute search completely restricted to this specific workspace container
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause
    )

    # Defensive Guard: If Chroma DB returns completely empty results
    if not results or not results["documents"] or not results["documents"][0]:
        return []

    formatted_results = []

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for doc, distance, metadata in zip(
        documents,
        distances,
        metadatas
    ):
        formatted_results.append({
            "text": doc,
            "distance": distance,
            "metadata": metadata
        })

    return formatted_results