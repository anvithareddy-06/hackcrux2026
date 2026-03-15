import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_setup import DB_PATH

# ── Full keyword banks from your reddit_model.ipynb ──────────────────────────
STAGE_KEYWORDS      = ["stage 1","stage 2","stage 3","stage 4","early","advanced",
                        "late","recovery","remission","chronic","acute"]
SYMPTOMS_LIST       = ["fatigue","headache","nausea","vomiting","fever","cough",
                        "pain","dizziness","weakness","breathing","tired",
                        "swelling","rash","chest pain","weight loss","anxiety","depression"]
MEDICATION_LIST     = ["ibuprofen","paracetamol","acetaminophen","aspirin","sumatriptan",
                        "metformin","levothyroxine","insulin","chemotherapy","radiation",
                        "tamoxifen","morphine","antibiotics","steroids","medication","therapy"]
SIDE_EFFECTS_LIST   = ["headache","nausea","vomiting","dizziness","fatigue",
                        "weakness","insomnia","rash","dry mouth","irritation"]
CAUSE_KEYWORDS      = ["stress","smoking","infection","genetics","hormonal imbalance",
                        "iodine deficiency","obesity","poor diet","alcohol"]
PRECAUTION_KEYWORDS = ["avoid smoking","exercise","regular checkup","healthy diet",
                        "reduce stress","sleep well","avoid alcohol","stay hydrated"]
BENEFIT_KEYWORDS    = ["improved","recovered","better","relief","controlled symptoms","normalized"]
FOOD_KEYWORDS       = ["vegetables","fruits","whole grains","protein","iodine rich foods",
                        "nuts","fish","leafy greens","balanced diet"]
TIME_WORDS          = ["day","days","week","weeks","month","months","year","years"]


def _fetch_posts(disease: str) -> list:
    """Fetch Reddit posts via public JSON API."""
    import requests
    url     = f"https://www.reddit.com/search.json?q={disease}+symptoms&limit=50&sort=relevance"
    headers = {"User-Agent": "health-research-bot/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data  = r.json()
        posts = data.get("data", {}).get("children", [])
        return [p["data"] for p in posts if p["data"].get("selftext","").strip()]
    except Exception as e:
        print(f"[Reddit] Fetch error: {e}")
        return []


def _nlp_extract(text: str) -> dict:
    """Keyword-based NLP extraction (mirrors your notebook logic)."""
    text_lower = text.lower()
    words      = text_lower.split()

    result = {
        "symptoms"   : set(),
        "treatments" : set(),
        "side_effects": set(),
        "stages"     : set(),
        "recovery"   : set(),
        "causes"     : set(),
        "precautions": set(),
        "benefits"   : set(),
        "food"       : set(),
    }

    for w in words:
        if w in SYMPTOMS_LIST:       result["symptoms"].add(w)
        if w in MEDICATION_LIST:     result["treatments"].add(w)
        if w in SIDE_EFFECTS_LIST:   result["side_effects"].add(w)
        if w in BENEFIT_KEYWORDS:    result["benefits"].add(w)

    for kw in STAGE_KEYWORDS:
        if kw in text_lower:         result["stages"].add(kw)
    for kw in CAUSE_KEYWORDS:
        if kw in text_lower:         result["causes"].add(kw)
    for kw in PRECAUTION_KEYWORDS:
        if kw in text_lower:         result["precautions"].add(kw)
    for kw in FOOD_KEYWORDS:
        if kw in text_lower:         result["food"].add(kw)

    for i, w in enumerate(words):
        if w.isdigit() and i + 1 < len(words):
            if words[i + 1] in TIME_WORDS:
                result["recovery"].add(f"{w} {words[i+1]}")

    return result


def run_reddit_pipeline(disease: str):
    print("[Reddit] Running pipeline...")
    disease = disease.strip().lower()

    posts = _fetch_posts(disease)
    if not posts:
        print(f"[Reddit] No posts found for '{disease}'")
        return

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    # Aggregate NLP across all posts for reddit_structured
    agg = {k: set() for k in
           ["symptoms","treatments","side_effects","stages",
            "recovery","causes","precautions","benefits","food"]}

    raw_count = 0
    for post in posts:
        title = post.get("title", "")
        text  = post.get("selftext", "")
        url   = "https://www.reddit.com" + post.get("permalink", "")

        # Store raw post
        try:
            c.execute(
                "INSERT INTO reddit_raw (disease,title,text,url) VALUES (?,?,?,?)",
                (disease, title, text, url)
            )
            raw_count += 1
        except sqlite3.IntegrityError:
            pass  # duplicate URL

        # Per-post NLP → disease_data
        extracted = _nlp_extract(title + " " + text)
        for key in agg:
            agg[key].update(extracted[key])

        # Insert per-post row into main unified table
        c.execute("""
        INSERT INTO disease_data
            (disease, symptoms, treatments, side_effects, benefits, stage, source, link)
        VALUES (?,?,?,?,?,?,?,?)""", (
            disease,
            ",".join(extracted["symptoms"]),
            ",".join(extracted["treatments"]),
            ",".join(extracted["side_effects"]),
            ",".join(extracted["benefits"]),
            " | ".join(list(extracted["stages"]) + list(extracted["recovery"])),
            "Reddit",
            url
        ))

    # Upsert aggregated summary into reddit_structured
    c.execute("""
    INSERT OR REPLACE INTO reddit_structured
        (disease, symptoms, treatments, stage, side_effects,
         recovery_time, causes, precautions, treatment_benefits, recommended_food)
    VALUES (?,?,?,?,?,?,?,?,?,?)""", (
        disease,
        ", ".join(agg["symptoms"]),
        ", ".join(agg["treatments"]),
        ", ".join(agg["stages"]),
        ", ".join(agg["side_effects"]),
        ", ".join(agg["recovery"]),
        ", ".join(agg["causes"]),
        ", ".join(agg["precautions"]),
        ", ".join(agg["benefits"]),
        ", ".join(agg["food"]),
    ))

    conn.commit()
    conn.close()
    print(f"[Reddit] Stored {raw_count} post(s), aggregated insights saved.")
