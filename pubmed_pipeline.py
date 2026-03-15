import sqlite3
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_setup import DB_PATH

# ── Expanded keyword banks ────────────────────────────────────────────────────
SYMPTOMS = [
    "fatigue","tiredness","lethargy","weakness","malaise","fever","chills",
    "night sweats","weight gain","weight loss","loss of appetite","anorexia",
    "pain","headache","chest pain","joint pain","abdominal pain","back pain",
    "muscle pain","myalgia","arthralgia","cramps","sore throat",
    "dizziness","confusion","seizures","numbness","tingling","tremor",
    "memory loss","cognitive decline","insomnia",
    "cough","shortness of breath","dyspnea","wheezing","breathlessness",
    "nausea","vomiting","diarrhea","constipation","bloating","indigestion",
    "abdominal discomfort","rectal bleeding",
    "rash","itching","pruritus","jaundice","swelling","edema","hair loss",
    "alopecia","dry skin","lesions","ulcers",
    "palpitations","tachycardia","hypertension","hypotension","syncope",
    "blurred vision","dry mouth","frequent urination","polyuria","polydipsia",
    "depression","anxiety","mood swings","irritability","redness","inflammation",
]

TREATMENTS = [
    "levothyroxine","insulin","metformin","aspirin","ibuprofen","acetaminophen",
    "paracetamol","amoxicillin","penicillin","doxycycline","azithromycin",
    "ciprofloxacin","prednisone","prednisolone","dexamethasone","omeprazole",
    "atorvastatin","lisinopril","amlodipine","warfarin","heparin","clopidogrel",
    "tamoxifen","trastuzumab","bevacizumab","rituximab","pembrolizumab",
    "nivolumab","imatinib","erlotinib","gefitinib","sorafenib","sunitinib",
    "morphine","oxycodone","codeine","tramadol","gabapentin","pregabalin",
    "methotrexate","hydroxychloroquine","sulfasalazine","leflunomide",
    "adalimumab","infliximab","etanercept","tocilizumab","secukinumab",
    "valacyclovir","acyclovir","oseltamivir","remdesivir",
    "chemotherapy","radiation","radiotherapy","surgery","immunotherapy",
    "hormone therapy","targeted therapy","biological therapy","gene therapy",
    "dialysis","transplant","stem cell transplant","bone marrow transplant",
    "antibiotics","antifungals","antivirals","steroids","corticosteroids",
    "vaccine","vaccination","physiotherapy","rehabilitation","psychotherapy",
    "cognitive behavioral therapy","laser therapy","phototherapy",
    "blood transfusion","oxygen therapy","mechanical ventilation",
]

SIDE_EFFECTS = [
    "nausea","vomiting","diarrhea","constipation","fatigue","weakness",
    "headache","dizziness","rash","itching","hair loss","alopecia",
    "insomnia","anxiety","depression","weight gain","weight loss",
    "dry mouth","dry skin","swelling","edema","bleeding","bruising",
    "infection","immunosuppression","neutropenia","anemia","thrombocytopenia",
    "liver toxicity","hepatotoxicity","nephrotoxicity","cardiotoxicity",
    "peripheral neuropathy","numbness","tingling","muscle weakness",
    "bone pain","joint pain","hot flashes","night sweats","mood changes",
    "cognitive impairment","memory loss","photosensitivity","mucositis",
    "stomatitis","dysphagia","dyspnea","pneumonitis","colitis",
    "hypertension","hypotension","tachycardia","bradycardia","arrhythmia",
    "hyperglycemia","hypoglycemia","hypothyroidism","adrenal insufficiency",
]


def fetch_pubmed_articles(disease: str, max_results: int = 20) -> list:
    """
    Fetch PubMed articles using XML format — gives FULL untruncated abstracts.
    Returns list of (disease, title, abstract, year) tuples directly.
    """
    try:
        from Bio import Entrez
        import xml.etree.ElementTree as ET

        Entrez.email = "saisrireddy25@gmail.com"

        # Step 1: search for IDs
        handle  = Entrez.esearch(db="pubmed", term=disease, retmax=max_results)
        results = Entrez.read(handle)
        ids     = results["IdList"]
        if not ids:
            print(f"[PubMed] No IDs found for '{disease}'")
            return []

        # Step 2: fetch as XML — no line-wrapping, full abstracts
        fetch  = Entrez.efetch(db="pubmed", id=ids, rettype="xml", retmode="xml")
        xml_data = fetch.read()

        articles = []
        root = ET.fromstring(xml_data)

        for article in root.findall(".//PubmedArticle"):
            # Title
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""

            # Abstract — join all AbstractText sections (some have multiple)
            abstract_parts = []
            for ab in article.findall(".//AbstractText"):
                label = ab.get("Label", "")
                text  = "".join(ab.itertext()).strip()
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)

            # Year
            year_el = article.find(".//PubDate/Year")
            year    = year_el.text if year_el is not None else ""

            if title:
                articles.append((disease.lower(), title, abstract, year))

        print(f"[PubMed] Fetched {len(articles)} articles via XML")
        return articles

    except Exception as e:
        print(f"[PubMed] Fetch error: {e}")
        return []


def extract_structured(abstract: str, title: str = ""):
    """Match keywords against full abstract + title."""
    text         = (title + " " + abstract).lower()
    symptoms     = list(dict.fromkeys([w for w in SYMPTOMS     if w in text]))
    treatments   = list(dict.fromkeys([w for w in TREATMENTS   if w in text]))
    side_effects = list(dict.fromkeys([w for w in SIDE_EFFECTS if w in text]))
    return ",".join(symptoms), ",".join(treatments), ",".join(side_effects)


def run_pubmed_pipeline(disease: str):
    print("[PubMed] Running pipeline...")
    disease  = disease.strip().lower()
    articles = fetch_pubmed_articles(disease)

    if not articles:
        print(f"[PubMed] No articles found for '{disease}'")
        return

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    c.executemany(
        "INSERT INTO pubmed_articles (disease, title, abstract, year) VALUES (?,?,?,?)",
        articles
    )
    conn.commit()

    matched = 0
    for _, title, abstract, _ in articles:
        syms, treats, sides = extract_structured(abstract, title)

        c.execute(
            "INSERT INTO structured_data (disease, symptoms, treatments, side_effects) VALUES (?,?,?,?)",
            (disease, syms, treats, sides)
        )
        c.execute("""
        INSERT INTO disease_data
            (disease, symptoms, treatments, side_effects, stage, source, link)
        VALUES (?,?,?,?,?,?,?)""",
        (disease, syms, treats, sides, "", "PubMed", ""))

        if syms or treats or sides:
            matched += 1

    conn.commit()
    conn.close()
    print(f"[PubMed] Done — {len(articles)} articles, {matched} with extracted data.")
