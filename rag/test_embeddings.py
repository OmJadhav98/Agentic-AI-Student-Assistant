from chunking import chunk_text
from embeddings import create_embeddings


sample_text = """
Machine Learning is a branch of Artificial Intelligence.
It allows computers to learn patterns from data.
Supervised learning uses labelled data for training.
Unsupervised learning works with unlabelled data.
Deep Learning uses neural networks with multiple layers.
"""


# Split text into chunks
chunks = chunk_text(
    sample_text,
    chunk_size=100,
    overlap=20
)

# Create embeddings
embeddings = create_embeddings(chunks)


print("Number of chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)

print("\nFirst chunk:")
print(chunks[0])

print("\nFirst embedding:")
print(embeddings[0])