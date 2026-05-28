import chromadb
from chromadb.config import Settings

from app.services.embedding_service import (
    generate_embedding
)

client = chromadb.PersistentClient(
    path="/app/chroma_storage"
)

collection = client.get_or_create_collection(
    name="enterprise_knowledge_base"
)

def add_document(
    document_id: str,
    text: str,
    metadata: dict = None
):

    embedding = generate_embedding(text)

    collection.add(
        ids=[document_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )

def search_documents(
    query: str,
    top_k: int = 3,
    filters: dict = None
):

    query_embedding = generate_embedding(query)

    # Filter preparation
    where_clause = None
    
    if filters:
        # Strip out any keys that have None values
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        
        if len(clean_filters) > 1:
            # 🔥 FIX 2: Explicitly format multiple keys with ChromaDB's logical '$and' operator
            where_clause = {
                "$and": [
                    {key: value} 
                    for key, value in clean_filters.items()
                ]
            }
        elif len(clean_filters) == 1:
            where_clause = clean_filters

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause  # Pass our safe where clause structure
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