from pathlib import Path
import duckdb
import requests
import pandas as pd

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

import pickle

from preprocess import preprocess

DATA_DIR = Path("data")
CATEGORY = "Books"
BASE_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw"
REVIEWS_URL = f"{BASE_URL}/review_categories/{CATEGORY}.jsonl.gz"
META_URL    = f"{BASE_URL}/meta_categories/meta_{CATEGORY}.jsonl.gz"
REVIEWS_FILE = DATA_DIR / f"{CATEGORY}.jsonl.gz"
META_FILE    = DATA_DIR / f"meta_{CATEGORY}.jsonl.gz"
OUTPUT_FILE  = DATA_DIR / f"{CATEGORY}_merged.parquet"

c2 = duckdb.connect()

c2.execute(f"""
      COPY (SELECT * FROM read_json_auto('{REVIEWS_URL}')  LIMIT 20000)
      TO 'data/raw/reviews_raw.parquet'
      (FORMAT PARQUET, COMPRESSION ZSTD)
  """)

c2.execute(f"""
      COPY (SELECT * FROM read_json_auto('{META_URL}') LIMIT 20000)
      TO 'data/raw/meta_raw.parquet'
      (FORMAT PARQUET, COMPRESSION ZSTD)
  """)

c2.execute("""
    COPY (
        SELECT
           b.title,
           b.author.name AS author,
           b.average_rating,
           b.rating_number,
           b.features AS book_details,
           b.price,
           b.categories,

           r.text AS individual_review,
           r.rating AS individual_rating,

           b.parent_asin AS book_asin,
           r.asin AS rating_asin
        FROM read_parquet('data/raw/meta_raw.parquet') b
        LEFT JOIN read_parquet('data/raw/reviews_raw.parquet') r USING (parent_asin)
    )
    TO 'data/processed/merged.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
""")

df = c2.execute(f"SELECT * FROM read_parquet('data/processed/merged.parquet')").df()
df = df.fillna("")

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
                "price": row["price"]
            }
        )
    )

retriever = BM25Retriever.from_documents(
    documents,
    k=5,
    preprocess_func=preprocess
)

with open('data/processed/retriever.pkl', 'wb') as file:
    pickle.dump(retriever, file)

# print("Made it here")
# print(Path.cwd())
