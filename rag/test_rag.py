import os
import fitz

from embeddings import create_embeddings
from faiss_store import FAISSStore
from llm import generate_answer


# PDF folder
pdf_folder = "../uploads"

# Find all PDF files
pdf_files = [
    os.path.join(pdf_folder, file)
    for file in os.listdir(pdf_folder)
    if file.lower().endswith(".pdf")
]

if not pdf_files:
    raise ValueError("No PDF files found in uploads folder.")


# Extract text from all PDFs
all_text = ""

for pdf_file in pdf_files:
    print(f"\nReading: {os.path.basename(pdf_file)}")

    document = fitz.open(pdf_file)

    for page in document:
        all_text += page.get_text() + "\n"

    document.close()


print("\nTotal extracted characters:", len(all_text))


# Split text into chunks
chunks = []

chunk_size = 500
overlap = 50

start = 0

while start < len(all_text):
    end = start + chunk_size
    chunk = all_text[start:end].strip()

    if chunk:
        chunks.append(chunk)

    start = end - overlap


print("Number of chunks:", len(chunks))


# Create embeddings
print("\nCreating embeddings...")

embeddings = create_embeddings(chunks)

print("Embedding shape:", embeddings.shape)


# Create FAISS vector store
store = FAISSStore(embeddings.shape[1])

store.add_embeddings(
    embeddings,
    chunks
)

print("FAISS knowledge base created.")


# Ask a question
question = input("\nAsk a question about the PDFs: ")


# Create query embedding
query_embedding = create_embeddings([question])


# Search relevant chunks
results = store.search(
    query_embedding,
    top_k=3
)


# Combine retrieved information
context = "\n\n".join(
    result["text"]
    for result in results
)


print("\nRetrieved information:")
print("----------------------")
print(context)


# Generate answer using Gemini
print("\nGenerating AI answer...")

answer = generate_answer(
    question,
    context
)


print("\nAI Answer:")
print("----------")
print(answer)