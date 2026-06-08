# def chunk_text(
#     text: str,
#     chunk_size: int = 500
# ):

#     chunks = []

#     for i in range(0, len(text), chunk_size):

#         chunk = text[i:i + chunk_size]

#         chunks.append(chunk)

#     return chunks



# Token chunking
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

tokenizer = embedding_model.tokenizer


def chunk_text(
    text: str,
    chunk_size: int = 256,
    overlap: int = 50
):
    tokens = tokenizer.encode(
        text,
        add_special_tokens=False
    )

    chunks = []

    step = chunk_size - overlap

    for i in range(
        0,
        len(tokens),
        step
    ):
        chunk_tokens = tokens[
            i:i + chunk_size
        ]

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True
        )

        chunks.append(chunk_text)

    return chunks



# sentence chunking
# def chunk_text(
#     text: str,
#     chunk_size: int = 2,
#     overlap: int = 1
# ):

#     # Split into sentences
#     sentences = text.split(".")

#     # Remove empty entries
#     sentences = [
#         s.strip()
#         for s in sentences
#         if s.strip()
#     ]

#     chunks = []

#     step = chunk_size - overlap

#     for i in range(
#         0,
#         len(sentences),
#         step
#     ):

#         chunk_sentences = sentences[
#             i:i + chunk_size
#         ]

#         chunk = ". ".join(
#             chunk_sentences
#         )

#         if chunk:
#             chunks.append(chunk)

#     return chunks