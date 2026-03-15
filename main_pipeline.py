"""
main_pipeline.py
Run this to fetch data from all 3 sources for a disease.
Usage: python main_pipeline.py
"""
import sqlite3
import pandas as pd
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database_setup import setup_database, DB_PATH, get_connection
from pipelines.kaggle_module  import run_kaggle_pipeline
from pipelines.pubmed_pipeline import run_pubmed_pipeline
from pipelines.reddit_pipeline import run_reddit_pipeline


def run_all_pipelines(disease: str):
    disease = disease.strip().lower()

    setup_database()

    # Clear stale data for this disease
    conn = get_connection()
    for table in ("disease_data", "pubmed_articles", "structured_data",
                  "reddit_raw", "reddit_structured"):
        conn.execute(f"DELETE FROM {table} WHERE LOWER(disease) = ?", (disease,))
    conn.commit()
    conn.close()

    print(f"\n{'='*55}")
    print(f"  Fetching intelligence for: {disease.title()}")
    print(f"{'='*55}")

    run_kaggle_pipeline(disease)
    run_pubmed_pipeline(disease)
    run_reddit_pipeline(disease)

    print(f"\n{'='*55}")
    print("  All pipelines complete!")
    print(f"{'='*55}")

    conn = get_connection()
    summary = pd.read_sql(
        "SELECT source, COUNT(*) as records FROM disease_data "
        "WHERE LOWER(disease) LIKE ? GROUP BY source",
        conn, params=(f"%{disease}%",)
    )
    conn.close()
    print("\nRecords collected per source:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    disease = input("Enter disease name: ")
    run_all_pipelines(disease)
