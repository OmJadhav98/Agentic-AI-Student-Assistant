from pyq_analysis import analyze_pyq


sample_pyq = """
1. Explain convolutional neural networks.
2. Explain the working of convolution in CNN.
3. What is pooling in CNN?
4. Explain CNN architecture.
5. What are the applications of convolutional neural networks?
6. Explain the difference between supervised learning and unsupervised learning.
"""


result = analyze_pyq(sample_pyq)

print("Total Questions:", result["total_questions"])

print("\nQuestions:")
for item in result["questions"]:
    print(item)

print("\nImportant Keywords:")
for keyword, count in result["important_keywords"]:
    print(keyword, "->", count)