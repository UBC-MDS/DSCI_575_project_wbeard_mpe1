# Standard imports
from pathlib import Path
import sys
import os
import pickle

# from preprocess import preprocess_without_using_stopwords
from rag_pipeline import get_rag_response

from dotenv import load_dotenv

# Third-party imports
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Some setup
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv(Path(__file__).parent.parent / ".env")

# load searches
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = FAISS.load_local(
    "data/processed/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

semantic_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

with open('data/processed/retriever.pkl', 'rb') as file:
    bm25_retriever = pickle.load(file)

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, semantic_retriever],
    weights=[0.2, 0.8],
)

rag_queries = [
    "backpacking across europe",
    "books for kids learning geology",
    "knitting crochet guide",
    "best way to start a business",
    "how to get out of debt"
]

"""Get top results for RAG semantic and ensemble search"""

for query in rag_queries:

    semantic_results = semantic_retriever.invoke(query)
    ensemble_results = ensemble_retriever.invoke(query)
    ensemble_results = ensemble_results[:min(5, len(ensemble_results))]

    semantic_rag = get_rag_response(query, semantic_retriever)
    ensemble_rag = get_rag_response(query, ensemble_retriever)

    print("=" * 80)
    print(f"## QUERY: {query}\n")

    # rag semantic search
    print("### RAG Semantic:\n")
    print(f"**RAG Response:** {semantic_rag}\n")
    print("#### Top Results")
    for i, doc in enumerate(semantic_results, 1):
        print(f"""{i}. Title: {doc.metadata.get("title")}
""")

    # semantic search
    print("### RAG Ensemble:\n")
    print(f"**RAG Response:** {ensemble_rag}\n")
    print("#### Top Results")
    for i, doc in enumerate(ensemble_results, 1):
        print(f"""{i}. Title: {doc.metadata.get("title")}
""")
