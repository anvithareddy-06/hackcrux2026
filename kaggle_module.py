import pandas as pd
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_setup import DB_PATH

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "datasets", "Diseases_Symptoms.csv")


def run_kaggle_pipeline(disease_name: str):
    print("[Kaggle] Running pipeline...")
    disease_name = disease_name.strip().lower()

    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        print(f"[Kaggle] CSV not found at {CSV_PATH}")
        return

    matched = df[df["Name"].str.lower().str.contains(disease_name, na=False)]

    if matched.empty:
        print(f"[Kaggle] No match for '{disease_name}'")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    count = 0

    for _, row in matched.iterrows():
        symptoms  = row["Symptoms"]  if pd.notna(row.get("Symptoms"))  else ""
        treatments= row["Treatments"]if pd.notna(row.get("Treatments"))else ""
        chronic   = str(row.get("Chronic",    ""))
        contagious= str(row.get("Contagious", ""))
        stage     = f"Chronic: {chronic} | Contagious: {contagious}"

        c.execute("""
        INSERT INTO disease_data
            (disease, symptoms, treatments, side_effects, benefits, stage, source, link)
        VALUES (?,?,?,?,?,?,?,?)""",
        (row["Name"].lower(), symptoms, treatments, "", "", stage, "Kaggle", ""))
        count += 1

    conn.commit()
    conn.close()
    print(f"[Kaggle] Inserted {count} record(s).")
