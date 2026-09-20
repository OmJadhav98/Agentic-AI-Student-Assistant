# -----------------------------
# Text Chunking
# -----------------------------

def chunk_text(
    text,
    chunk_size=500,
    overlap=50
):
    """
    Split text into overlapping chunks.

    chunk_size:
        Maximum approximate number of characters
        in each chunk.

    overlap:
        Number of characters shared between
        consecutive chunks.
    """

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks