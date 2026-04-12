# Amazon Product Query Assistant

## Table of Contents

## About

- explanation about the subset of data we are using
- we don't have different files to create bm25 and faiss, because we want to create the list of documents once then create the bm25 retriever and the faiss vector store with it.

## Application

- web app link
- demo video link

## Setup

- instructions for TA to setup and run

- download review and meta data from books from <https://amazon-reviews-2023.github.io/>
- save files to `data/raw`
- install `duckdb`? (make sure its in requirements)
- instruction for creating huggingface api key
  - create hugging face account: <https://huggingface.co/login>
  - click on user icon in top right and select access tokens
  - click create new token button (top right)
  - token type: Read
  - create token
  - save token in `.env`: HUGGINGFACEHUB_API_TOKEN="your_api_key_here", see `.env.sample`
- instruction to create vector_store.pkl (can't be on github because it is too large...)

## Github Repo

<https://github.ubc.ca/mds-2025-26/DSCI_575_project_wbeard_mpe1>

## Data

Source: <https://amazon-reviews-2023.github.io/>

## License

MIT