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
from langchain_classic.retrievers import EnsembleRetriever

path_to_src = "src/"
sys.path.insert(0, path_to_src)
from preprocess import preprocess_without_using_stopwords
from rag_pipeline import get_rag_response

# Shiny-related imports
from shiny import App, render, ui, reactive, req

# Some setup
# sys.path.insert(0, str(Path(__file__).parent))
# load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv()

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

semantic_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# load keyword search retriever
with open('data/processed/retriever.pkl', 'rb') as file:
    bm25_retriever = pickle.load(file)

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, semantic_retriever],
    weights=[0.2, 0.8]  # Example: asigning 40% importance to BM25, 60% to Semantic Search
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
        ui.card(
            ui.navset_tab(
                ui.nav_panel("Search",
                    ui.help_text(HELP_TEXT),
                    ui.div(style="margin-top: 12px;"),
                    ui.input_text("search", "", placeholder="Enter Search"),
                    ui.layout_columns(
                        ui.input_action_button("keyword", "Key-Word Search", disabled=True),
                        ui.input_action_button("semantic", "Semantic Search", disabled=True),
                    ),
                ),
                ui.nav_panel("Chat",
                    ui.input_switch("rag_switch", "Use Ensemble Search", False),
                    ui.chat_ui("chat"), 
                ),
            ),
        ),
        ui.card(
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
        ),
        col_widths=(3, 9),
    ),
    FOOTER,
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

    chat = ui.Chat(id="chat") 

    @reactive.effect
    @reactive.event(input.keyword)
    def _():
        search_type.set("keyword")

    @reactive.effect
    @reactive.event(input.semantic)
    def _():
        search_type.set("semantic")

    # @reactive.effect
    @chat.on_user_submit  
    async def _(user_input: str):
        if input.rag_switch():
            search_type.set("rag-ensemble")
        else:
            search_type.set("rag-semantic")

    # perform search
    @reactive.calc
    @reactive.event(input.keyword, input.semantic)
    def search_results():

        search_type_str = search_type.get()

        query = ""
        if search_type_str in ["keyword", "semantic"]:
            query = input.search()
        elif search_type_str in ["rag-semantic", "rag-ensemble"]:
            query = chat.user_input()
        req(query)

        if search_type_str == "keyword":
            tokenized_query = preprocess_without_using_stopwords(query)
            scores = np.sort(bm25_retriever.vectorizer.get_scores(tokenized_query))[::-1][:5]
            documents = bm25_retriever.invoke(query)
            return zip(documents, scores)
        elif search_type_str == "semantic":
            return vector_store.similarity_search_with_score(query, k=5)
        elif search_type_str == "rag-semantic":
            return semantic_retriever.invoke(query)
        elif search_type_str == "rag-ensemble":
            return ensemble_retriever.invoke(query)
    
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

    @chat.on_user_submit  
    async def handle_user_input(user_input: str): 
        if input.rag_switch():
            chat_response = get_rag_response(user_input, ensemble_retriever)
        else:
            chat_response = get_rag_response(user_input, semantic_retriever)
        await chat.append_message(chat_response)

app = App(app_ui, server)
