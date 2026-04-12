from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

#from preprocess import preprocess

# Standard imports
from pathlib import Path
import sys
import os
import pickle

# Third-party imports
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Some setup
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv(Path(__file__).parent.parent / ".env")


with open('data/processed/retriever.pkl', 'rb') as file:
    retriever = pickle.load(file)

# load semantic search index
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_store = FAISS.load_local(
    "data/processed/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

queries_easy = [
    "children's books about rocks",
    "knitting crochet guide",
    "start business",
    "personal finance debt free",
]

queries_medium = [
    "books for kids learning geology",
    "easy guide to using wool",
    "running a store successfully",
    "how to get out of debt",
]

queries_complex = [
    "how to teach grade 1 earth science",
    "what are the various patterns for knitting",
    "how to beat your competitors",
    "resources for getting your money in order",
]

"""Get top results for BM25 and semantic search"""

for query in queries_complex:
    results = retriever.invoke(query)
    print("=" * 80)
    print(f"QUERY: {query}\n")

    # keyword search
    print("BM25 Top Results:\n")
    for i, doc in enumerate(results, 1):
        print(f"""{i}. Title: {doc.metadata.get("title")}
Author: {doc.metadata.get("author")}
Details: {doc.metadata.get("book_details")[:100]}
""")

    # semantic search
    results_s = vector_store.similarity_search(query, k=5)
    print("Semantic Top Results:\n")
    for i, doc in enumerate(results_s, 1):
        print(f"""{i}. Title: {doc.metadata.get("title")}
Author: {doc.metadata.get("author")}
Details: {doc.metadata.get("book_details")[:100]}
""")
