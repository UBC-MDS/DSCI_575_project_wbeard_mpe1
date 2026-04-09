from pathlib import Path
import duckdb

def create_parquets() -> None:
    """Convert Books.jsonl.gz and meta_Books.jsonl.gz to parquet files.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    
    """
    if not Path("../data/raw/Books.parquet").is_file():
        duckdb.query("COPY (SELECT * FROM read_json_auto('../data/raw/Books.jsonl.gz')) TO '../data/raw/Books.parquet' (FORMAT PARQUET)")
    if not Path("../data/raw/meta_Books.parquet").is_file():
        duckdb.query("COPY (SELECT * FROM read_json_auto('../data/raw/meta_Books.jsonl.gz', sample_size = 1000000)) TO '../data/raw/meta_Books.parquet' (FORMAT PARQUET)")

def create_parquet_samples(sample_size = 1000) -> None:
    """Create parquet files from Books.parquet and meta_Books.parquet that are a sample from the full files.
    
    Parameters
    ----------
    sample_size : int
        Size of sample to draw from the full dataset
    
    Returns
    -------
    None
    
    """
    con = duckdb.connect()

    con.execute("""
    SELECT setseed(0.42);
    """)

    # Create a temp table with the sampled rows
    con.execute(f"""
    CREATE TEMP TABLE sample AS
    SELECT *
    FROM read_json_auto('../data/raw/meta_Books.jsonl.gz', sample_size = 1000000)
    USING SAMPLE {sample_size} ROWS
    """)

    # Write sampled Books
    con.execute("""
    COPY sample
    TO '../data/raw/meta_Books_sample.parquet'
    (FORMAT PARQUET)
    """)

    # Use sampled IDs to filter meta_Books
    con.execute("""
    COPY (
        SELECT f2.*
        FROM read_json_auto('../data/raw/Books.jsonl.gz', sample_size = 1000000) f2
        INNER JOIN sample s
        ON f2.asin = s.parent_asin
    ) TO '../data/raw/Books_sample.parquet'
    (FORMAT PARQUET)
    """)
