"""Good Books Dashboard."""

# Standard imports
from pathlib import Path
import sys
import os
import pickle

# Third-party imports
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from preprocess import preprocess_without_using_stopwords

# Shiny-related imports
from shiny import App, render, ui, reactive, req

# Some setup
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv(Path(__file__).parent.parent / ".env")

# load keyword search retriever
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

# shiny app

HELP_TEXT = "Welcome to the Find Good Books Dashboard. " \
    "Type in your query and select either of the search types to display the top results. " \
    "Once you've tried one system, click the other button to try the other!"

FOOTER = ui.p(
    "Find Good Books Dashboard"
    " | Authors: Michael Eirikson & Wesley Beard |"
    " Repository: https://github.ubc.ca/UBC-MDS/DSCI_575_project_wbeard_mpe1 |"
    " Last updated: 2026-04-12",
    class_="text-center text-muted",
)

app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel(
        "Search Results",
        ui.layout_columns(
            ui.value_box(
                title="Price Range",
                value=ui.output_text("price_range"),
            ),
            ui.value_box(
                title="Average Rating",
                value=ui.output_text("avg_rating")
            ),
            ui.value_box(
                title="Total Results",
                value=ui.output_text("book_count")
            ),
            fill=False,
        ),
        ui.card(ui.output_data_frame("data")),
        FOOTER
    ),
    # TODO: update if we want this
    # ui.nav_panel(
    #     "About",
    #     ui.layout_columns(
    #         ui.card(ui.output_text(("search_results"))),
    #         fill=False,
    #     ),
    # ),
    sidebar=ui.sidebar(
        ui.help_text(HELP_TEXT),
        ui.input_text("search", "", placeholder="Enter Search"),
        ui.layout_columns(
            ui.input_action_button("keyword", "Key-Word Search", disabled=True),
            ui.input_action_button("semantic", "Semantic Search", disabled=True),
        ),
        # ui.chat_ui(
        #     "chat",
        #     messages=["Let's find your next read!"],
        #     placeholder="Search"
        # ),
        width=400
    ),
    id="tabs",
    title="Find Good Books Dashboard",
    fillable=True,
)


def server(input, output, session):

    @reactive.effect
    @reactive.event(input.search)
    def set_button_state():
        if input.search():
            ui.update_action_button("keyword", disabled=False)
            ui.update_action_button("semantic", disabled=False)
        else:
            ui.update_action_button("keyword", disabled=True)
            ui.update_action_button("semantic", disabled=True)

    # track which button was just pressed

    search_type = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.keyword)
    def _():
        search_type.set("keyword")

    @reactive.effect
    @reactive.event(input.semantic)
    def _():
        search_type.set("semantic")

    # perform search

    @reactive.calc
    @reactive.event(input.keyword, input.semantic)
    def search_results():
        query = input.search()
        req(query)

        if search_type.get() == "keyword":
            tokenized_query = preprocess_without_using_stopwords(query)
            scores = np.sort(retriever.vectorizer.get_scores(tokenized_query))[::-1][:5]
            documents = retriever.invoke(query)
            return zip(documents, scores)
        elif search_type.get() == "semantic":
            return vector_store.similarity_search_with_score(query, k=5)

    # display search results

    @reactive.calc
    @reactive.event(input.keyword, input.semantic)
    def data_results():
        documents = search_results()

        rows = []
        for doc, score in documents:
            rows.append({
                "Title": doc.metadata.get("title"),
                "Author": doc.metadata.get("author"),
                "Categories": doc.metadata.get("categories"),
                "Average Rating": doc.metadata.get("average_rating"),
                "Review": doc.metadata.get("individual_review")[:200],
                "Price": doc.metadata.get("price"),
                "Search Score": f"{score:.3f}"
            })

        return pd.DataFrame(rows)

    @render.text
    def avg_rating():
        df = data_results()

        max_avg_rating = df["Average Rating"].max()
        min_avg_rating = df["Average Rating"].min()

        return f"{min_avg_rating} - {max_avg_rating}"

    @render.text
    def book_count():
        return data_results().shape[0]

    @render.text
    def price_range():
        df = data_results()

        max_price = df["Price"].max()
        min_price = df["Price"].min()

        return f"${min_price} - ${max_price}"

    @render.data_frame
    def data():
        df = data_results()

        return df


app = App(app_ui, server)
