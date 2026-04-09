"""Good Books Dashboard."""

# Standard imports
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Third-party imports
from dotenv import load_dotenv
import duckdb
import ibis
from ibis import _
import numpy as np
import pandas as pd

# Shiny-related imports
from shiny import App, render, ui, reactive, req
from shinywidgets import render_altair, output_widget


load_dotenv(Path(__file__).parent.parent / ".env")

# CSV = "data/processed/processed_data.csv"
# OUT = "data/processed/processed_data.parquet"

# duckdb.execute(
#     f"""
#     COPY (SELECT * FROM read_csv_auto('{CSV}'))
#     TO '{OUT}' (FORMAT PARQUET)
#     """
# )

# con = ibis.duckdb.connect()
# raw_data = con.read_parquet("data/processed/processed_data.parquet")

dummy_data = pd.DataFrame({
    "Title": [
        "1984",
        "To Kill a Mockingbird",
        "The Great Gatsby",
        "Pride and Prejudice",
        "The Catcher in the Rye",
        "The Hobbit",
        "Fahrenheit 451",
        "Moby-Dick",
        "The Alchemist",
        "Brave New World"
    ],
    "Author": [
        "George Orwell",
        "Harper Lee",
        "F. Scott Fitzgerald",
        "Jane Austen",
        "J.D. Salinger",
        "J.R.R. Tolkien",
        "Ray Bradbury",
        "Herman Melville",
        "Paulo Coelho",
        "Aldous Huxley"
    ],
    "Year": [1949, 1960, 1925, 1813, 1951, 1937, 1953, 1851, 1988, 1932],
    "Rating": [4.2, 4.3, 3.9, 4.4, 3.8, 4.7, 4.1, 3.5, 3.9, 4.0],
    "Genre": [
        "Dystopian",
        "Classic",
        "Classic",
        "Romance",
        "Classic",
        "Fantasy",
        "Dystopian",
        "Adventure",
        "Philosophical",
        "Dystopian"
    ],
    "Price": [9.99, 14.99, 10.99, 8.99, 12.50, 15.75, 11.25, 13.40, 16.00, 14.20]
})

FOOTER = ui.p(
    "Good Books Dashboard"
    " | Authors: Michael Wesley Beard |"
    " Repository: https://github.ubc.ca/mds-2025-26/DSCI_575_project_wbeard_mpe1 |"
    " Last updated: 2026-04-07",
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
    ),
    ui.nav_panel(
        "About",
        ui.layout_columns(
            ui.card("Place holder"),
            fill=False,
        ),
    ),
    sidebar=ui.sidebar(
        ui.help_text("Welcome to the Find Good Books Dashboard."),
        ui.input_radio_buttons(
            "model",
            "Model",
            choices=[
                "BM25",
                "Semantic"
            ],
            selected="Key-word",
        ),
        ui.input_text("query", "Search"),
        ui.input_action_button("sparse", "Sparse Search", disabled=True),
        ui.input_action_button("dense", "Dense Search", disabled=True),
        ui.output_ui("query_submit"),
        ui.chat_ui(
            "chat",
            messages=["Let's find your next read!"],
            placeholder="Search"
        ),
        width=400
    ),
    id="tabs",
    title="Find Good Books",
    fillable=True,
)


def server(input, output, session):

    @reactive.effect
    @reactive.event(input.query)
    def set_button_state():
        if input.query():
            ui.update_action_button("sparse", disabled=False)
            ui.update_action_button("dense", disabled=False)
        else:
            ui.update_action_button("sparse", disabled=True)
            ui.update_action_button("dense", disabled=True)

    @render.ui
    @reactive.event(input.query)
    def query_submit():
        return ui.p(f"Your question, {input.query()}!",)

    @reactive.calc()
    def data_results():
        return dummy_data

    @render.text
    def avg_rating():
        return data_results()["Rating"].mean()

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
        return dummy_data


app = App(app_ui, server)
