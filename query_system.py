"""
query_system.py
───────────────
Two core features:
  1. symptoms_to_diseases()  → given user symptoms, rank matching diseases from Kaggle CSV
  2. get_disease_summary()   → pull aggregated intelligence from the DB for a disease
"""
import pandas as pd
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database_setup import DB_PATH

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "datasets", "Diseases_Symptoms.csv")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Symptom → Disease prediction (Kaggle CSV based)
# ─────────────────────────────────────────────────────────────────────────────

def _load_kaggle() -> pd.DataFrame:
    try:
        return pd.read_csv(CSV_PATH).dropna(subset=["Symptoms"])
    except FileNotFoundError:
        return pd.DataFrame()


def get_all_symptoms() -> list:
    """All unique symptom tokens from the CSV — used to power the autocomplete."""
    df = _load_kaggle()
    if df.empty:
        return []
    tokens = set()
    for row in df["Symptoms"].dropna():
        for part in row.split(","):
            tokens.add(part.strip().lower())
    return sorted(tokens)


def symptoms_to_diseases(user_symptoms: list, top_n: int = 10) -> list:
    """
    Rank diseases by how many of the user's symptoms appear in the disease profile.
    Returns a list of dicts, sorted by match_score descending.
    """
    df = _load_kaggle()
    if df.empty:
        return []

    user = [s.strip().lower() for s in user_symptoms if s.strip()]
    if not user:
        return []

    results = []
    for _, row in df.iterrows():
        disease_syms = [s.strip().lower() for s in str(row["Symptoms"]).split(",")]
        matched = [u for u in user if any(u in ds for ds in disease_syms)]
        score   = len(matched)
        if score == 0:
            continue
        results.append({
            "disease"         : row["Name"],
            "matched_symptoms": matched,
            "all_symptoms"    : disease_syms,
            "match_score"     : score,
            "match_pct"       : round(score / len(user) * 100, 1),
            "treatments"      : row.get("Treatments", "") if pd.notna(row.get("Treatments")) else "",
            "chronic"         : bool(row.get("Chronic",    False)),
            "contagious"      : bool(row.get("Contagious", False)),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Disease summary from DB (all 3 sources)
# ─────────────────────────────────────────────────────────────────────────────

def _count_items(series: pd.Series) -> dict:
    combined = ",".join(series.dropna())
    items    = [s.strip() for s in combined.split(",") if s.strip()]
    return pd.Series(items).value_counts().to_dict()


def get_disease_summary(disease_name: str) -> dict:
    """
    Pull everything from the DB for a disease.
    Returns a rich dict with counts, reddit structured data, articles, etc.
    """
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM disease_data WHERE LOWER(disease) LIKE ?",
        conn, params=(f"%{disease_name.lower()}%",)
    )

    # Reddit structured insights
    rs = pd.read_sql(
        "SELECT * FROM reddit_structured WHERE LOWER(disease) LIKE ?",
        conn, params=(f"%{disease_name.lower()}%",)
    )

    # PubMed article titles
    pm = pd.read_sql(
        "SELECT title, year FROM pubmed_articles WHERE LOWER(disease) LIKE ?",
        conn, params=(f"%{disease_name.lower()}%",)
    )

    conn.close()

    if df.empty:
        return {}

    return {
        "disease"       : disease_name,
        "total_records" : len(df),
        "sources"       : df["source"].value_counts().to_dict(),
        "symptoms"      : _count_items(df["symptoms"]),
        "treatments"    : _count_items(df["treatments"]),
        "side_effects"  : _count_items(df["side_effects"]),
        "benefits"      : _count_items(df["benefits"]),
        "stages"        : df["stage"].dropna().unique().tolist(),
        "reddit_links"  : df[df["source"] == "Reddit"]["link"].dropna().head(5).tolist(),
        "reddit_summary": rs.to_dict("records")[0] if not rs.empty else {},
        "pubmed_articles": pm.to_dict("records"),
        "raw_df"        : df,
    }


if __name__ == "__main__":
    syms    = input("Enter symptoms (comma separated): ").split(",")
    results = symptoms_to_diseases(syms)
    for r in results:
        print(f"  {r['match_score']} match  →  {r['disease']}  ({r['matched_symptoms']})")
