"""Create key-word and semantic search systems"""

import duckdb
import pandas as pd

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from preprocess import preprocess
from dotenv import load_dotenv
import os
import pickle


c2 = duckdb.connect()

df = c2.execute("SELECT * FROM read_parquet('data/processed/merged.parquet') WHERE rating_order = 1").df()
df = df.fillna("")

# create documents

documents = []

for _, row in df.iterrows():
    content = f"""Title: {row['title']}
    Author: {row['author']}
    Details: {row['book_details']}
    Categories: {row['categories']}
    """

    documents.append(
        Document(
            page_content=content,
            metadata={
                "title": row["title"],
                "author": row["author"],
                "categories": row["categories"],
                "average_rating": row["average_rating"],
                "total_ratings": row["rating_number"],
                "individual_review": row["individual_review"],
                "individual_rating": row["individual_rating"],
                "price": row["price"],
                "book_details": row["book_details"]
            }
        )
    )

# keyword search system

retriever = BM25Retriever.from_documents(
    documents,
    k=5,
    preprocess_func=preprocess
)

# semantic search system

load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_store = FAISS.from_documents(documents, embeddings)

# save search systems

with open('data/processed/retriever.pkl', 'wb') as file:
    pickle.dump(retriever, file)

vector_store.save_local("data/processed/faiss_index")