import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Union

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def generate_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()

def calculate_similarity(text_or_vector_a: Union[str, list], text_or_vector_b: Union[str, list]) -> float:
    """
    Computes the cosine similarity score between two representations.
    Accepts either raw text strings or pre-computed vector lists.
    Returns a float value between -1.0 and 1.0.
    """
    # 1. If inputs are strings, convert them to vectors on the fly using your encoder
    if isinstance(text_or_vector_a, str):
        vector_a = generate_embedding(text_or_vector_a)
    else:
        vector_a = text_or_vector_a

    if isinstance(text_or_vector_b, str):
        vector_b = generate_embedding(text_or_vector_b)
    else:
        vector_b = text_or_vector_b

    # 2. Safely perform the numpy matrix math
    a = np.array(vector_a)
    b = np.array(vector_b)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # Safety check to avoid division by zero if an embedding is empty
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return float(dot_product / (norm_a * norm_b))