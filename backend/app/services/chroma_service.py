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
    top_k: int = 3
):

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

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