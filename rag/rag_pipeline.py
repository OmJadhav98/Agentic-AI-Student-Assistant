import os
import fitz

from rag.embeddings import create_embeddings
from rag.faiss_store import FAISSStore
from rag.llm import generate_answer


# ============================================================
# Knowledge Base Cache
# ============================================================

knowledge_base_cache = {}


# ============================================================
# Build Knowledge Base
# ============================================================

def build_knowledge_base(material):
    """
    Build a FAISS knowledge base from the selected PDF.

    If the PDF has already been processed, the cached
    FAISS store is returned instead of processing it again.
    """

    # Return cached knowledge base if available
    if material in knowledge_base_cache:
        return knowledge_base_cache[material]

    pdf_folder = "uploads"

    # Build path to selected PDF
    pdf_file = os.path.join(
        pdf_folder,
        material
    )

    # Check whether PDF exists
    if not os.path.exists(pdf_file):
        raise ValueError(
            f"Selected study material not found: {material}"
        )

    # ========================================================
    # Extract Text
    # ========================================================

    document = fitz.open(pdf_file)

    try:

        all_text = ""

        for page in document:
            all_text += page.get_text() + "\n"

    finally:

        document.close()

    if not all_text.strip():
        raise ValueError(
            "Selected PDF contains no readable text."
        )

    # ========================================================
    # Create Text Chunks
    # ========================================================

    chunks = []

    chunk_size = 500
    overlap = 50

    start = 0

    while start < len(all_text):

        end = start + chunk_size

        chunk = all_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move forward while maintaining overlap
        start = end - overlap

    if not chunks:
        raise ValueError(
            "No usable text chunks were created from the PDF."
        )

    # ========================================================
    # Create Embeddings
    # ========================================================

    embeddings = create_embeddings(chunks)

    # ========================================================
    # Create FAISS Store
    # ========================================================

    store = FAISSStore(
        embeddings.shape[1]
    )

    store.add_embeddings(
        embeddings,
        chunks
    )

    # ========================================================
    # Save in Cache
    # ========================================================

    knowledge_base_cache[material] = store

    return store


# ============================================================
# Ask Question
# ============================================================

def ask_question(store, question):
    """
    Search the FAISS knowledge base for relevant content
    and generate an answer using the LLM.
    """

    # ========================================================
    # Create Question Embedding
    # ========================================================

    query_embedding = create_embeddings(
        [question]
    )

    # ========================================================
    # Search Relevant Chunks
    # ========================================================

    results = store.search(
        query_embedding,
        top_k=3
    )

    # ========================================================
    # Build Context
    # ========================================================

    context = "\n\n".join(
        result["text"]
        for result in results
    )

    # ========================================================
    # Generate AI Answer
    # ========================================================

    answer = generate_answer(
        question,
        context
    )

    return {
        "question": question,
        "answer": answer,
        "sources": results
    }