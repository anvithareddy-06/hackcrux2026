import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "disease_intelligence.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def setup_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS disease_data (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        disease      TEXT,
        symptoms     TEXT,
        treatments   TEXT,
        side_effects TEXT,
        benefits     TEXT,
        stage        TEXT,
        source       TEXT,
        link         TEXT,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS pubmed_articles (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        disease  TEXT,
        title    TEXT,
        abstract TEXT,
        year     TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS structured_data (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        disease      TEXT,
        symptoms     TEXT,
        treatments   TEXT,
        side_effects TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reddit_raw (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        disease TEXT,
        title   TEXT,
        text    TEXT,
        url     TEXT UNIQUE
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reddit_structured (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        disease            TEXT UNIQUE,
        symptoms           TEXT,
        treatments         TEXT,
        stage              TEXT,
        side_effects       TEXT,
        recovery_time      TEXT,
        causes             TEXT,
        precautions        TEXT,
        treatment_benefits TEXT,
        recommended_food   TEXT
    )""")

    conn.commit()
    conn.close()
    print("[DB] All tables ready.")


if __name__ == "__main__":
    setup_database()
