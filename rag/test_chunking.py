from chunking import chunk_text


sample_text = """
Machine Learning is a branch of Artificial Intelligence.
It allows computers to learn patterns from data.
Supervised learning uses labelled data for training.
Unsupervised learning works with unlabelled data.
Deep Learning uses neural networks with multiple layers.
"""


chunks = chunk_text(sample_text, chunk_size=100, overlap=20)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)