import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def generate_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()

# 🔥 ADD THIS FUNCTION TO FIX THE IMPORT ERROR
def calculate_similarity(vector_a: list, vector_b: list) -> float:
    """
    Computes the cosine similarity score between two vector embeddings.
    Returns a float value between -1.0 and 1.0.
    """
    a = np.array(vector_a)
    b = np.array(vector_b)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # Safety check to avoid division by zero if an embedding is empty
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return float(dot_product / (norm_a * norm_b))