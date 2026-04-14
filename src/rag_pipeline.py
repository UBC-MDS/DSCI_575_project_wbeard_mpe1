
import os

import pickle

from dotenv import load_dotenv

# from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

llm_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",  # Keep this as text-generation for the base
    max_new_tokens=100,
    # provider="auto" #"novita"
)

llm = ChatHuggingFace(llm=llm_endpoint)

#print(llm.invoke("Michael is "))

# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# vector_store = FAISS.load_local(
#     "data/processed/faiss_index",
#     embeddings,
#     allow_dangerous_deserialization=True
# )

# semantic_retriever = vector_store.as_retriever(
#     search_type="similarity",
#     search_kwargs={"k": 5}
# )

# # load keyword search retriever
# with open('data/processed/retriever.pkl', 'rb') as file:
#     bm25_retriever = pickle.load(file)

# ensemble_retriever = EnsembleRetriever(
#     retrievers=[bm25_retriever, semantic_retriever],
#     weights=[0.2, 0.8]  # Example: asigning 40% importance to BM25, 60% to Semantic Search
# )

def build_context(docs):
    """Prompt-ready context block"""

    return "\n\n".join(
        f"Title: {doc.metadata.get('title')}\n"
        f"Author: {doc.metadata.get('author', '')}\n"
        f"Categories: {doc.metadata.get('categories')}\n"
        f"Book details: {doc.metadata.get('book_details')}\n"
        f"Review: {doc.metadata.get('individual_review')[:200]}\n"
        for doc in docs
    )


SYSTEM_PROMPT = """
    You are a helpful Amazon shopping assistant.
    You have access to a sample of books listed on Amazon.
    Answer the question using only the following context:
    Always provide the title and author, when available.
    Do not include results that do not have both title and author.
    If there isn't helpful information in the context, just say that
    there are no relevant books available in the books sample."""


def build_prompt(query, context):
    return f"""{SYSTEM_PROMPT}

context:
{context}

question:
{query}

Answer based on the Amazon datasets: """

# one function, two parameters: query


def get_rag_response(question, retriever_type):

    rag_chain = (
        {
            "context": (retriever_type | RunnableLambda(build_context)),
            "query": RunnablePassthrough()
        }
        | RunnableLambda(lambda x: build_prompt(x["query"], x["context"]))
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(question)

#     print(answer)

#     print("=" * 80)
#     question = "delicious muffins"
#     results = semantic_retriever.invoke(question)
#     print("Top Results:\n")
#     for i, doc in enumerate(results, 1):
#         print(f"""{i}.
#     Title: {doc.metadata.get("title")}
#     Author: {doc.metadata.get("author")}
#     Details: {doc.metadata.get("book_details")[:100]}
#     """)


# get_rag_response("how to bake a cake", semantic_retriever)
