from sentence_transformers import SentenceTransformer


# -----------------------------
# Embedding Model
# -----------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# Create Embeddings
# -----------------------------

def create_embeddings(text_chunks):
    """
    Convert text chunks into numerical
    embedding vectors.
    """

    if not text_chunks:
        return []

    embeddings = model.encode(
        text_chunks,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embeddings