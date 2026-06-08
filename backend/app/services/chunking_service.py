# def chunk_text(
#     text: str,
#     chunk_size: int = 500
# ):

#     chunks = []

#     for i in range(0, len(text), chunk_size):

#         chunk = text[i:i + chunk_size]

#         chunks.append(chunk)

#     return chunks



from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def chunk_text(
    text: str,
    chunk_size: int = 256
):
    # Convert text to tokens
    tokens = tokenizer.encode(
        text,
        add_special_tokens=False
    )

    chunks = []

    for i in range(0, len(tokens), chunk_size):

        chunk_tokens = tokens[i:i + chunk_size]

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True
        )

        chunks.append(chunk_text)

    return chunks