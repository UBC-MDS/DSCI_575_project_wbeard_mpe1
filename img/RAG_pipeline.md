```{mermaid}
flowchart LR
query[User prompt]
faiss1[FAISS retriever]
faiss2[FAISS retriever]
bm25[BM25 retriever]
search_result[Results dataframe]
prompt[Augmented prompt]
system_prompt[System prompt]
hugging[ChatHuggingFace LLM]
model[model: meta-llama/Meta-Llama-3-8B-Instruct]
response[Response]

subgraph **Retriever**
faiss1
subgraph Ensemble
faiss2
bm25
end
faiss2 & bm25
end

faiss1 --> search_result
Ensemble --> search_result

prompt --> hugging
model --> hugging

subgraph **Generation**
hugging
end

query -. or .-> faiss1 & Ensemble
query & search_result --> prompt
hugging -->  response

system_prompt --> prompt
```