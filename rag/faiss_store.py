import faiss
import numpy as np


# -----------------------------
# FAISS Vector Store
# -----------------------------

class FAISSStore:

    def __init__(self, dimension):
        """
        Create a FAISS vector store.

        Inner Product is used with normalized vectors,
        which gives cosine similarity.
        """

        self.dimension = dimension

        # FAISS index for cosine similarity
        self.index = faiss.IndexFlatIP(
            dimension
        )

        # Store original text chunks
        self.chunks = []


    # -----------------------------
    # Add Embeddings
    # -----------------------------

    def add_embeddings(
        self,
        embeddings,
        text_chunks
    ):
        """
        Add embedding vectors and their
        corresponding text chunks.
        """

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        if embeddings.size == 0:
            return

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(
            embeddings
        )

        # Add vectors to FAISS
        self.index.add(
            embeddings
        )

        # Store corresponding text
        self.chunks.extend(
            text_chunks
        )


    # -----------------------------
    # Search
    # -----------------------------

    def search(
        self,
        query_embedding,
        top_k=3
    ):
        """
        Search for the most relevant
        text chunks.
        """

        if self.index.ntotal == 0:
            return []

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        ).reshape(1, -1)

        # Normalize query vector
        faiss.normalize_L2(
            query_embedding
        )

        # Don't request more results
        # than available vectors
        top_k = min(
            top_k,
            self.index.ntotal
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index != -1:

                results.append({
                    "score": float(score),
                    "text": self.chunks[index]
                })

        return results