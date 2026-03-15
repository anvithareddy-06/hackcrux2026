# 🧬 CrowdMed Intelligence Platform

> Turning scattered patient experiences into structured, trusted insights.

**Team:** TeamKaliyug | **Hackathon:** HackCrux V2 | **Problem Statement:** 4

---

## 📌 Problem Statement

Patients searching online for disease information face:
- Information scattered across forums, blogs, Reddit, and research papers
- No way to compare clinical data vs real patient experiences
- Misinformation mixed with genuine insights
- No single platform that structures and trusts this data

---

## 💡 Our Solution

CrowdMed Intelligence aggregates data from **3 sources** simultaneously:
- 📦 **Kaggle** — structured medical dataset (405 diseases, 939 symptoms)
- 🔬 **PubMed** — scientific research articles via NCBI Entrez API
- 💬 **Reddit** — real patient discussions via public JSON API

Runs NLP pipelines on all three, stores in SQLite, and presents unified insights with AI-powered cross-source comparison.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📦 Kaggle Tab | Symptoms & treatments pie charts from medical dataset |
| 🔬 PubMed Tab | Research articles + NLP extracted symptoms/treatments/side effects |
| 💬 Reddit Tab | Patient experience insights table grouped by disease stage |
| 🤖 AI Comparison | Groq LLaMA 3.3 compares all 3 sources, highlights agreements & differences |
| 🩺 Doctor Recommendation | Severity-based doctor advice + specialist recommendation |
| 🗺️ Hospital Finder | Interactive Folium map — click to find specialist hospitals nearby |

---

## 🛠️ Tech Stack

### Libraries & Why We Used Them

#### Web Framework
| Library | Version | Why Used |
|---------|---------|----------|
| `streamlit` | ≥1.35.0 | Rapid web dashboard — turns Python scripts into interactive web apps without HTML/CSS/JS |

#### Data Processing
| Library | Version | Why Used |
|---------|---------|----------|
| `pandas` | ≥2.0.0 | Reading CSV files, SQL queries into DataFrames, data aggregation and value_counts for NLP output |
| `numpy` | ≥1.24.0 | Numerical operations required by pandas and plotly internally |

#### Visualization
| Library | Version | Why Used |
|---------|---------|----------|
| `plotly` | ≥5.18.0 | Interactive donut pie charts for symptoms, treatments, side effects — supports hover tooltips and dark theme |

#### Maps
| Library | Version | Why Used |
|---------|---------|----------|
| `folium` | ≥0.15.0 | Interactive clickable map — click anywhere to search hospitals at that location, draws 10km radius circle |
| `streamlit-folium` | ≥0.18.0 | Bridge between Folium maps and Streamlit — enables map click events to trigger Python callbacks |

#### Medical Data
| Library | Version | Why Used |
|---------|---------|----------|
| `biopython` | ≥1.83 | Provides `Bio.Entrez` module — official Python interface to NCBI PubMed API for searching and fetching articles in XML format |

#### HTTP & APIs
| Library | Version | Why Used |
|---------|---------|----------|
| `requests` | ≥2.31.0 | Used for Reddit JSON API, OpenStreetMap Overpass API, Groq AI API, and IPInfo location API |

#### NLP
| Library | Version | Why Used |
|---------|---------|----------|
| `spacy` | ≥3.7.0 | NLP tokenization for Reddit text — tokenizes post text for recovery time extraction (number + time word detection) |

#### Database
| Library | Version | Why Used |
|---------|---------|----------|
| `sqlite3` | built-in | Lightweight local database — stores all pipeline outputs, no server setup needed, perfect for hackathon |

---

## 🔌 APIs Used

| API | Provider | Cost | Key Required | Purpose |
|-----|----------|------|-------------|---------|
| PubMed Entrez | NCBI (US Gov) | Free | Email only | Fetch scientific research articles |
| Reddit JSON | Reddit | Free | None | Fetch patient discussion posts |
| Groq LLaMA | Groq Cloud | Free tier | Yes | AI cross-source comparison |
| Overpass (OSM) | OpenStreetMap | Free | None | Find nearby hospitals/clinics |
| IPInfo | IPInfo.io | Free tier | None | Auto-detect user location |
| Google Maps | Google | Free (links) | None | View on Maps + Get Directions |

---

## 🗄️ Database Schema

```
disease_intelligence.db
├── disease_data          ← Unified table (Kaggle + PubMed + Reddit)
├── pubmed_articles       ← Raw PubMed articles with full abstracts
├── structured_data       ← NLP-extracted data from PubMed
├── reddit_raw            ← Raw Reddit posts (title, text, url)
└── reddit_structured     ← Aggregated NLP insights from Reddit
```

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/crowdmed-intelligence.git
cd crowdmed-intelligence/disease-intelligence-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 4. Set up Groq API key (free)
Get your free key at: https://console.groq.com

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY="gsk_your-key-here"
```

**Mac/Linux:**
```bash
export GROQ_API_KEY="gsk_your-key-here"
```

### 5. Run the app
```bash
python -m streamlit run app.py
```

---

## 📁 Project Structure

```
disease-intelligence-system/
├── app.py                        ← Main Streamlit dashboard
├── main_pipeline.py              ← CLI orchestrator
├── query_system.py               ← Symptom→Disease prediction engine
├── database_setup.py             ← DB schema (single source of truth)
├── requirements.txt              ← All dependencies
├── README.md
├── datasets/
│   └── Diseases_Symptoms.csv     ← Kaggle dataset (405 diseases)
└── pipelines/
    ├── __init__.py
    ├── kaggle_module.py           ← Kaggle CSV pipeline
    ├── pubmed_pipeline.py         ← PubMed API + XML parsing + NLP
    └── reddit_pipeline.py         ← Reddit API + NLP extraction
```

---

## 🔄 How Data Extraction Works

### Kaggle
```
CSV file → pandas filter by disease → extract symptoms/treatments columns → SQLite
```

### PubMed
```
Disease name → Entrez search → fetch XML → parse abstracts →
keyword NLP matching → extract symptoms/treatments/side effects → SQLite
```

### Reddit
```
Disease name → Reddit JSON API → fetch 50 posts →
keyword NLP → extract symptoms, causes, recovery times,
precautions, foods, stage → aggregate by stage → SQLite
```

### AI Comparison (Groq)
```
SQLite aggregated data → build structured prompt →
Groq LLaMA 3.3 70B → compare 3 sources → return analysis
```

---

## 👥 Team

 Name 

Kallem Architha 
Kallem Anvitha 
Saisri Katipelly 
Aleti Ronith Reddy 

**Team Name:** TeamKaliyug
**Hackathon:** HackCrux V2
**Problem Statement:** 4

---

## ⚠️ Disclaimer

This platform is for informational purposes only and does not constitute medical advice. Always consult a licensed healthcare professional for diagnosis and treatment.
