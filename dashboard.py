import streamlit as st
import sqlite3
import pandas as pd
from kaggle_module import run_kaggle_pipeline
from pubmed_pipeline import run_pubmed_pipeline
from reddit_pipeline import run_reddit_pipeline

conn = sqlite3.connect("../disease_intelligence.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS disease_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease TEXT,
    symptoms TEXT,
    treatments TEXT,
    side_effects TEXT,
    stage TEXT,
    recovery TEXT,
    source TEXT,
    link TEXT
)
""")

conn.commit()
conn.close()
st.set_page_config(page_title="Disease Intelligence System", layout="wide")

st.title("🧠 Disease Intelligence Dashboard")

disease = st.text_input("Enter Disease Name")

if st.button("Search"):

    st.write("Collecting data from sources...")
with st.spinner("Fetching Kaggle, PubMed, and Reddit data..."):
    # Run pipelines
    run_kaggle_pipeline(disease)
    run_pubmed_pipeline(disease)
    run_reddit_pipeline(disease)

    st.success("Data collected successfully")

    conn = sqlite3.connect("../disease_intelligence.db")

    df = pd.read_sql(
        "SELECT * FROM disease_data WHERE disease LIKE ?",
        conn,
        params=(f"%{disease}%",)
    )

    conn.close()

    if df.empty:
        st.warning("No data found")
    else:

        st.success("Data retrieved successfully")

        # -------- Symptoms --------
        symptoms = ",".join(df["symptoms"].dropna())
        symptom_list = [s.strip() for s in symptoms.split(",") if s.strip() != ""]

        symptom_counts = pd.Series(symptom_list).value_counts()

        st.subheader("Top Symptoms")
        st.write(symptom_counts.head(10))

        st.bar_chart(symptom_counts.head(10))

        # -------- Treatments --------
        treatments = ",".join(df["treatments"].dropna())
        treatment_list = [t.strip() for t in treatments.split(",") if t.strip() != ""]

        treatment_counts = pd.Series(treatment_list).value_counts()

        st.subheader("Top Treatments")
        st.write(treatment_counts.head(10))

        st.bar_chart(treatment_counts.head(10))

        # -------- Stages --------
        st.subheader("Disease Stage Info")

        stages = df["stage"].dropna().unique()

        for s in stages:
            if s.strip() != "":
                st.write("-", s)

        # -------- Sources --------
        st.subheader("Data Sources")

        st.write(df["source"].value_counts())

        # -------- Reddit Links --------
        reddit_links = df[df["source"] == "Reddit"]["link"]

        if not reddit_links.empty:
            st.subheader("Reddit Discussions")

            for link in reddit_links.head(5):
                st.write(link)