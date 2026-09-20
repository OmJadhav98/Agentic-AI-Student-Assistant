from chunking import chunk_text
from embeddings import create_embeddings
from faiss_store import FAISSStore


sample_text = """
Machine Learning is a branch of Artificial Intelligence.
It allows computers to learn patterns from data.
Supervised learning uses labelled data for training.
Unsupervised learning works with unlabelled data.
Deep Learning uses neural networks with multiple layers.
"""


# 1. Split text
chunks = chunk_text(
    sample_text,
    chunk_size=100,
    overlap=20
)

print("Number of chunks:", len(chunks))


# 2. Create embeddings
embeddings = create_embeddings(chunks)

print("Embedding shape:", embeddings.shape)


# 3. Create FAISS store
dimension = embeddings.shape[1]

store = FAISSStore(dimension)


# 4. Add embeddings
store.add_embeddings(
    embeddings,
    chunks
)

print("FAISS vectors:", store.index.ntotal)


# 5. Create query
query = "What is supervised learning?"


# 6. Convert query to embedding
query_embedding = create_embeddings([query])


# 7. Search
results = store.search(
    query_embedding,
    top_k=2
)


# 8. Display results
print("\nQuery:")
print(query)

print("\nRelevant chunks:")

for i, result in enumerate(results, start=1):

    print(f"\n--- Result {i} ---")
    print("Similarity:", result["score"])
    print("Text:", result["text"])