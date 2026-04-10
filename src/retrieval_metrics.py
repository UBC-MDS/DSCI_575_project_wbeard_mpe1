from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

import pickle

from preprocess import preprocess

with open('data/processed/retriever.pkl', 'rb') as file:
    retriever = pickle.load(file)

query = "rinella nature justin smith"

# Retrieve relevant documents
results = retriever.invoke(query)
# Display the results
print("Top Retrieved Documents:\n")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}\n")
