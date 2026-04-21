from pathlib import Path
import duckdb

def convert_raw_to_parquet():
    """Convert raw data file to parquet as side effect"""

    if not Path("data/raw/Books.parquet").is_file():
        try:
            duckdb.query("COPY (SELECT * FROM read_json_auto('data/raw/Books.jsonl.gz')) TO 'data/raw/Books.parquet' (FORMAT PARQUET)")
        except:
            print("Parquet file not created.")
            print("Do you have the file 'data/raw/Books.jsonl.gz'?")
    if not Path("data/raw/meta_Books.parquet").is_file():
        try:
            duckdb.query("COPY (SELECT * FROM read_json_auto('data/raw/meta_Books.jsonl.gz', sample_size = 1000000)) TO 'data/raw/meta_Books.parquet' (FORMAT PARQUET)")
        except:
            print("Parquet file not created.")
            print("Do you have the file 'data/raw/met_Books.jsonl.gz'?")

    return None

def get_top_books(con, n_books: int = 10000):
    """Create smaller parquet files (as a side effect) with only data for the top rated books."""

    con.execute(f"""
    CREATE TEMP TABLE top_books AS
    SELECT *
    FROM read_json_auto("data/raw/meta_Books.jsonl.gz", sample_size = 1000000)
    WHERE rating_number > 10
    ORDER BY average_rating DESC
    LIMIT {n_books};
    """)

    # save top book meta data
    con.execute("""
    COPY top_books
    TO "data/raw/top_meta_Books.parquet"
    (FORMAT PARQUET)
    """)

    # get and save top book reviews
    con.execute(f"""
    COPY (
        SELECT *
        FROM read_json_auto("data/raw/Books.jsonl.gz")
        WHERE asin IN (SELECT parent_asin FROM top_books)
    ) TO "data/raw/top_Books.parquet";
    """)

    return None

def create_merged_parquet(con):
    """Create a merged parquet file for the top books with one review per book"""

    con.execute("""
        COPY (
            SELECT 
                meta.title,
                COALESCE(meta.author.name, '') AS author,
                array_to_string(meta.features, ', ') AS book_details,
                array_to_string(meta.categories, ', ') AS categories,
                meta.average_rating,
                meta.rating_number, 
                meta.price, 
                reviews.text AS individual_review,
                reviews.rating AS individual_rating,
                reviews.asin,
                ROW_NUMBER() OVER (
                    PARTITION BY meta.parent_asin
                    ORDER BY reviews.rating DESC
                ) as rating_order
            FROM "data/raw/top_meta_Books.parquet" AS meta
            LEFT JOIN "data/raw/top_Books.parquet" AS reviews
            ON meta.parent_asin = reviews.asin
        ) TO "data/processed/merged.parquet" (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

if __name__ == "__main__":
    con = duckdb.connect()
    convert_raw_to_parquet()
    get_top_books(con, n_books=10000)
    create_merged_parquet(con)
