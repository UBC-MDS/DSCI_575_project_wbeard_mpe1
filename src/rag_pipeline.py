
import os

from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
hf_token = os.getenv("HF_TOKEN")

llm_endpoint = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=100,
)

llm = ChatHuggingFace(llm=llm_endpoint)

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
    there are no relevant books available in the books sample.
    Be very brief, answer is less then 40 words.
    """


def build_prompt(query, context):
    """Build the full augmented prompt for RAG"""

    augmented_prompt = f"""{SYSTEM_PROMPT}
        context:
        {context}
        question:
        {query}
        Answer based on the Amazon datasets: """

    return augmented_prompt

def get_rag_response(question, retriever_type):
    """Get RAG response from llm based on user questions and retriever"""

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
