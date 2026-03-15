"""
app.py  —  CrowdMed Intelligence Platform
Run with:  streamlit run app.py
"""
import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database_setup import setup_database, DB_PATH
from pipelines.kaggle_module   import run_kaggle_pipeline
from pipelines.pubmed_pipeline import run_pubmed_pipeline
from pipelines.reddit_pipeline import run_reddit_pipeline
from query_system import (
    symptoms_to_diseases,
    get_disease_summary,
    get_all_symptoms,
)

# ── Specialist mapping ────────────────────────────────────────────────────────
SPECIALIST_MAP = {
    # Cardiology
    "heart": ("Cardiologist", "🫀"),
    "cardiac": ("Cardiologist", "🫀"),
    "coronary": ("Cardiologist", "🫀"),
    "myocardial": ("Cardiologist", "🫀"),
    "arrhythmia": ("Cardiologist", "🫀"),
    "hypertension": ("Cardiologist", "🫀"),
    "atherosclerosis": ("Cardiologist", "🫀"),
    # Neurology
    "brain": ("Neurologist", "🧠"),
    "neuro": ("Neurologist", "🧠"),
    "migraine": ("Neurologist", "🧠"),
    "epilepsy": ("Neurologist", "🧠"),
    "seizure": ("Neurologist", "🧠"),
    "alzheimer": ("Neurologist", "🧠"),
    "parkinson": ("Neurologist", "🧠"),
    "stroke": ("Neurologist", "🧠"),
    "meningitis": ("Neurologist", "🧠"),
    "multiple sclerosis": ("Neurologist", "🧠"),
    # Pulmonology
    "lung": ("Pulmonologist", "🫁"),
    "pulmon": ("Pulmonologist", "🫁"),
    "asthma": ("Pulmonologist", "🫁"),
    "pneumonia": ("Pulmonologist", "🫁"),
    "bronchitis": ("Pulmonologist", "🫁"),
    "tuberculosis": ("Pulmonologist", "🫁"),
    "copd": ("Pulmonologist", "🫁"),
    "respiratory": ("Pulmonologist", "🫁"),
    # Endocrinology
    "diabetes": ("Endocrinologist", "🩸"),
    "thyroid": ("Endocrinologist", "🩸"),
    "hormonal": ("Endocrinologist", "🩸"),
    "endocrin": ("Endocrinologist", "🩸"),
    "adrenal": ("Endocrinologist", "🩸"),
    "pituitary": ("Endocrinologist", "🩸"),
    "obesity": ("Endocrinologist", "🩸"),
    "hyperthyroid": ("Endocrinologist", "🩸"),
    "hypothyroid": ("Endocrinologist", "🩸"),
    # Oncology
    "cancer": ("Oncologist", "🎗️"),
    "tumor": ("Oncologist", "🎗️"),
    "carcinoma": ("Oncologist", "🎗️"),
    "lymphoma": ("Oncologist", "🎗️"),
    "leukemia": ("Oncologist", "🎗️"),
    "melanoma": ("Oncologist", "🎗️"),
    # Gastroenterology
    "liver": ("Gastroenterologist", "🫃"),
    "gastro": ("Gastroenterologist", "🫃"),
    "hepatitis": ("Gastroenterologist", "🫃"),
    "crohn": ("Gastroenterologist", "🫃"),
    "colitis": ("Gastroenterologist", "🫃"),
    "colon": ("Gastroenterologist", "🫃"),
    "stomach": ("Gastroenterologist", "🫃"),
    "bowel": ("Gastroenterologist", "🫃"),
    "pancreatitis": ("Gastroenterologist", "🫃"),
    "gallbladder": ("Gastroenterologist", "🫃"),
    # Dermatology
    "skin": ("Dermatologist", "🧴"),
    "dermat": ("Dermatologist", "🧴"),
    "eczema": ("Dermatologist", "🧴"),
    "psoriasis": ("Dermatologist", "🧴"),
    "acne": ("Dermatologist", "🧴"),
    "rosacea": ("Dermatologist", "🧴"),
    "scabies": ("Dermatologist", "🧴"),
    # Orthopedics
    "bone": ("Orthopedic Surgeon", "🦴"),
    "joint": ("Orthopedic Surgeon", "🦴"),
    "arthritis": ("Orthopedic Surgeon", "🦴"),
    "fracture": ("Orthopedic Surgeon", "🦴"),
    "spine": ("Orthopedic Surgeon", "🦴"),
    "osteoporosis": ("Orthopedic Surgeon", "🦴"),
    "scoliosis": ("Orthopedic Surgeon", "🦴"),
    # Nephrology
    "kidney": ("Nephrologist", "🫘"),
    "renal": ("Nephrologist", "🫘"),
    "nephr": ("Nephrologist", "🫘"),
    "dialysis": ("Nephrologist", "🫘"),
    # Ophthalmology
    "eye": ("Ophthalmologist", "👁️"),
    "glaucoma": ("Ophthalmologist", "👁️"),
    "cataract": ("Ophthalmologist", "👁️"),
    "retina": ("Ophthalmologist", "👁️"),
    "myopia": ("Ophthalmologist", "👁️"),
    "conjunctivitis": ("Ophthalmologist", "👁️"),
    # Psychiatry / Mental Health
    "depression": ("Psychiatrist", "🧘"),
    "anxiety": ("Psychiatrist", "🧘"),
    "mental": ("Psychiatrist", "🧘"),
    "bipolar": ("Psychiatrist", "🧘"),
    "schizophrenia": ("Psychiatrist", "🧘"),
    "ptsd": ("Psychiatrist", "🧘"),
    "ocd": ("Psychiatrist", "🧘"),
    "eating disorder": ("Psychiatrist", "🧘"),
    # Rheumatology
    "lupus": ("Rheumatologist", "💊"),
    "rheumat": ("Rheumatologist", "💊"),
    "fibromyalgia": ("Rheumatologist", "💊"),
    "gout": ("Rheumatologist", "💊"),
    # ENT
    "ear": ("ENT Specialist", "👂"),
    "sinus": ("ENT Specialist", "👂"),
    "tonsil": ("ENT Specialist", "👂"),
    "throat": ("ENT Specialist", "👂"),
    "hearing": ("ENT Specialist", "👂"),
    "sinusitis": ("ENT Specialist", "👂"),
    # Urology
    "bladder": ("Urologist", "🔬"),
    "urolog": ("Urologist", "🔬"),
    "prostate": ("Urologist", "🔬"),
    "urinary": ("Urologist", "🔬"),
    # Gynecology
    "ovarian": ("Gynecologist", "🌸"),
    "uterine": ("Gynecologist", "🌸"),
    "cervical": ("Gynecologist", "🌸"),
    "menstrual": ("Gynecologist", "🌸"),
    "pcos": ("Gynecologist", "🌸"),
    "endometriosis": ("Gynecologist", "🌸"),
    # Infectious Disease
    "malaria": ("Infectious Disease Specialist", "🦠"),
    "hiv": ("Infectious Disease Specialist", "🦠"),
    "aids": ("Infectious Disease Specialist", "🦠"),
    "dengue": ("Infectious Disease Specialist", "🦠"),
    "typhoid": ("Infectious Disease Specialist", "🦠"),
    "infection": ("Infectious Disease Specialist", "🦠"),
    "sepsis": ("Infectious Disease Specialist", "🦠"),
    # Pediatrics
    "child": ("Pediatrician", "👶"),
    "pediatr": ("Pediatrician", "👶"),
    "congenital": ("Pediatrician", "👶"),
    "infant": ("Pediatrician", "👶"),
}


def get_specialist(disease_name: str) -> tuple:
    """Return (specialist_title, emoji) for a given disease name."""
    name_lower = disease_name.lower()
    for keyword, (specialist, emoji) in SPECIALIST_MAP.items():
        if keyword in name_lower:
            return specialist, emoji
    return "General Physician", "🏥"


def doctor_recommendation_box(disease_name: str):
    specialist, emoji = get_specialist(disease_name)
    safe_key = "doc_" + "".join(c if c.isalnum() else "_" for c in disease_name.lower())

    # ── Severity classification ───────────────────────────────────────────────
    CRITICAL_KEYWORDS = [
        "cancer","tumor","carcinoma","lymphoma","leukemia","melanoma",
        "stroke","myocardial","heart attack","sepsis","meningitis",
        "hiv","aids","epilepsy","alzheimer","parkinson","multiple sclerosis",
        "kidney failure","renal failure","liver failure","hepatitis",
        "tuberculosis","rabies","cholera","ebola","malaria","dengue",
        "diabetes","coronary","pneumonia","pulmonary","aneurysm",
        "thrombosis","embolism","lupus","schizophrenia","bipolar",
    ]
    MILD_KEYWORDS = [
        "acne","cold","flu","rash","eczema","dandruff","myopia","sinusitis",
        "sprain","bruise","indigestion","bloating","constipation","hiccups",
        "nosebleed","sunburn","warts","mild","minor","common cold",
        "conjunctivitis","motion sickness","insect bite","athlete's foot",
    ]
    name_lower = disease_name.lower()
    is_critical = any(k in name_lower for k in CRITICAL_KEYWORDS)
    is_mild     = any(k in name_lower for k in MILD_KEYWORDS)

    # ── Question box ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#1e293b; border:1.5px solid #334155; border-radius:14px;
                padding:1.2rem 1.6rem; margin:1.2rem 0 0.4rem 0;">
        <div style="font-size:1.1rem; font-weight:700; color:#f1f5f9; margin-bottom:.3rem;">
            🩺 &nbsp; Would you like to visit a doctor for
            <span style="color:#38bdf8;">{disease_name}</span>?
        </div>
        <div style="color:#94a3b8; font-size:.85rem;">
            Based on the analysis above, we can recommend the right specialist for you.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_yes, col_no, col_spacer = st.columns([1, 1, 4])
    with col_yes:
        yes_clicked = st.button("✅  Yes, show me", key=f"{safe_key}_yes",
                                use_container_width=True, type="primary")
    with col_no:
        no_clicked = st.button("❌  No thanks", key=f"{safe_key}_no",
                               use_container_width=True)

    if yes_clicked:
        st.session_state[safe_key] = "yes"
    if no_clicked:
        st.session_state[safe_key] = "no"

    answer = st.session_state.get(safe_key)

    # ── YES ───────────────────────────────────────────────────────────────────
    if answer == "yes":
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0f4c81,#1a3a5c);
                    border:2px solid #3b82f6; border-radius:14px;
                    padding:1.4rem 1.8rem; margin:.4rem 0 1rem 0;
                    box-shadow:0 4px 20px rgba(59,130,246,0.2);">
            <div style="font-size:1rem;font-weight:700;color:#bfdbfe;
                        text-transform:uppercase;letter-spacing:.07em;margin-bottom:.8rem;">
                🏥 &nbsp; Recommended Specialist
            </div>
            <div style="display:flex;align-items:center;gap:1.2rem;
                        background:rgba(255,255,255,0.08);border-radius:10px;
                        padding:.9rem 1.2rem;margin-bottom:1rem;">
                <span style="font-size:2.8rem;">{emoji}</span>
                <div>
                    <div style="color:#93c5fd;font-size:.78rem;text-transform:uppercase;
                                letter-spacing:.08em;margin-bottom:.25rem;">You should visit a</div>
                    <div style="color:#fff;font-size:1.5rem;font-weight:800;">{specialist}</div>
                </div>
            </div>
            <div style="color:#60a5fa;font-size:.82rem;">
                ⚠️ &nbsp;This is not a medical diagnosis. Please consult a licensed healthcare provider.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── NO ────────────────────────────────────────────────────────────────────
    elif answer == "no":
        if is_mild and not is_critical:
            # Non-critical disease → calm green response
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#052e16,#14532d);
                        border:2px solid #22c55e; border-radius:14px;
                        padding:1.4rem 1.8rem; margin:.4rem 0 1rem 0;
                        box-shadow:0 4px 20px rgba(34,197,94,0.15);">
                <div style="font-size:1.2rem;font-weight:800;color:#bbf7d0;margin-bottom:.6rem;">
                    ✅ &nbsp; Okay, sure — that's not critical!
                </div>
                <div style="color:#86efac;font-size:.95rem;line-height:1.6;margin-bottom:.9rem;">
                    <strong style="color:#fff;">{disease_name}</strong> is generally considered
                    a mild or manageable condition. You can monitor your symptoms at home for now.
                </div>
                <div style="background:rgba(0,0,0,0.2);border-radius:10px;
                            padding:.8rem 1.1rem;color:#d1fae5;font-size:.88rem;line-height:1.6;">
                    💡 <strong>Tips:</strong> Stay hydrated, rest well, and keep track of your symptoms.
                    If symptoms persist beyond a week or worsen, consider visiting a
                    <strong>{specialist}</strong>.
                </div>
                <div style="color:#4ade80;font-size:.8rem;margin-top:.8rem;">
                    ℹ️ &nbsp;This is not medical advice. Always consult a doctor if you're unsure.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Critical / serious disease → strong orange warning
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#431407,#7c2d12);
                        border:2px solid #f97316; border-radius:14px;
                        padding:1.4rem 1.8rem; margin:.4rem 0 1rem 0;
                        box-shadow:0 4px 20px rgba(249,115,22,0.2);">
                <div style="font-size:1.2rem;font-weight:800;color:#fed7aa;margin-bottom:.6rem;">
                    ⚠️ &nbsp; We Still Strongly Recommend Seeing a Doctor
                </div>
                <div style="color:#fdba74;font-size:.95rem;line-height:1.6;margin-bottom:.9rem;">
                    <strong style="color:#fff;">{disease_name}</strong> can be a serious condition.
                    Delaying a medical visit could worsen your health. Please don't ignore these signs.
                </div>
                <div style="display:flex;align-items:center;gap:1rem;
                            background:rgba(0,0,0,0.2);border-radius:10px;padding:.8rem 1.1rem;">
                    <span style="font-size:2rem;">{emoji}</span>
                    <div style="color:#fde68a;font-size:.9rem;">
                        A <strong>{specialist}</strong> is the right specialist for this condition.
                        Your health matters — please seek professional advice soon.
                    </div>
                </div>
                <div style="color:#fb923c;font-size:.8rem;margin-top:.8rem;">
                    🏥 &nbsp;This platform provides insights only — not a substitute for medical advice.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Nearby Hospitals ─────────────────────────────────────────────────────────

# Maps specialist type → best OSM amenity tags to search for
SPECIALIST_OSM_TAG = {
    "Cardiologist"                  : ("hospital", "cardiology"),
    "Neurologist"                   : ("hospital", "neurology"),
    "Pulmonologist"                 : ("hospital", "pulmonology"),
    "Endocrinologist"               : ("hospital", "endocrinology"),
    "Oncologist"                    : ("hospital", "oncology"),
    "Gastroenterologist"            : ("hospital", "gastroenterology"),
    "Dermatologist"                 : ("clinic",   "dermatology"),
    "Orthopedic Surgeon"            : ("hospital", "orthopaedics"),
    "Nephrologist"                  : ("hospital", "nephrology"),
    "Ophthalmologist"               : ("clinic",   "ophthalmology"),
    "Psychiatrist"                  : ("clinic",   "psychiatry"),
    "Rheumatologist"                : ("hospital", "rheumatology"),
    "ENT Specialist"                : ("clinic",   "ENT"),
    "Urologist"                     : ("hospital", "urology"),
    "Gynecologist"                  : ("clinic",   "gynaecology"),
    "Infectious Disease Specialist" : ("hospital", "infectious"),
    "Pediatrician"                  : ("hospital", "paediatrics"),
    "General Physician"             : ("hospital", "general"),
}


def fetch_nearby_hospitals(lat: float, lon: float, specialist: str, radius_m: int = 10000) -> list:
    """
    Query OpenStreetMap for hospitals/clinics within radius_m metres,
    filtered to show only facilities relevant to the specialist type.
    """
    import requests, math

    radius_m = int(radius_m)

    # ── Keyword banks per specialist — used to filter results by name ────────
    SPECIALIST_KEYWORDS = {
        "Cardiologist"                  : ["heart","cardiac","cardio","cardiovascular"],
        "Neurologist"                   : ["neuro","brain","neurology","neuroscience","epilepsy"],
        "Pulmonologist"                 : ["lung","pulmon","chest","respiratory","thoracic","breathe"],
        "Endocrinologist"               : ["endocrin","diabetes","thyroid","hormone","metabolic"],
        "Oncologist"                    : ["cancer","oncol","tumor","oncology","chemo","radiation"],
        "Gastroenterologist"            : ["gastro","liver","digestive","hepato","colon","bowel","gi"],
        "Dermatologist"                 : ["skin","dermat","dermato","cosmet"],
        "Orthopedic Surgeon"            : ["ortho","bone","joint","spine","fracture","orthopedic","musculo"],
        "Nephrologist"                  : ["kidney","renal","nephro","dialysis","urology"],
        "Ophthalmologist"               : ["eye","ophthal","vision","retina","ocular"],
        "Psychiatrist"                  : ["mental","psychiatr","psycho","mind","behav","counsel"],
        "Rheumatologist"                : ["rheumat","arthrit","autoimmune","lupus"],
        "ENT Specialist"                : ["ent","ear","nose","throat","sinus","audiolog"],
        "Urologist"                     : ["urol","urinary","bladder","prostate","kidney"],
        "Gynecologist"                  : ["gynae","gyneco","women","obstet","maternal","fertility"],
        "Infectious Disease Specialist" : ["infecti","tropical","fever","malaria","hiv","aids","tb","tuberculosis"],
        "Pediatrician"                  : ["child","pediatr","paediatr","infant","neonat","kid"],
        "General Physician"             : ["general","multispecial","multi-special","hospital","medical","health"],
    }

    keywords = SPECIALIST_KEYWORDS.get(specialist, ["hospital","medical","health","clinic"])

    # ── Build Overpass query — fetch all hospitals/clinics in radius ──────────
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="clinic"](around:{radius_m},{lat},{lon});
      node["healthcare"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="clinic"](around:{radius_m},{lat},{lon});
      way["healthcare"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """
    try:
        resp = requests.post(overpass_url, data={"data": query}, timeout=25)
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
    except Exception:
        return []

    hospitals = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or ""
        if not name:
            continue

        # ── Filter: only keep if name/tags contain specialist keywords ────────
        name_lower = name.lower()
        # Also check OSM healthcare speciality tags
        speciality_tags = " ".join([
            tags.get("healthcare:speciality", ""),
            tags.get("speciality", ""),
            tags.get("medical_speciality", ""),
            tags.get("description", ""),
        ]).lower()
        combined_text = name_lower + " " + speciality_tags

        # For General Physician, accept all hospitals (no keyword filter)
        is_match = (specialist == "General Physician") or \
                   any(kw in combined_text for kw in keywords)

        if not is_match:
            continue

        # ── Coordinates ──────────────────────────────────────────────────────
        if el["type"] == "node":
            hlat, hlon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center", {})
            hlat, hlon = center.get("lat"), center.get("lon")

        if not hlat or not hlon:
            continue

        # ── Address ──────────────────────────────────────────────────────────
        addr_parts = [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:city", ""),
        ]
        address = ", ".join(p for p in addr_parts if p) or "Address not available"

        phone   = tags.get("phone") or tags.get("contact:phone") or "—"
        website = tags.get("website") or tags.get("contact:website") or ""
        amenity = tags.get("amenity") or tags.get("healthcare") or "hospital"

        # ── Haversine distance ────────────────────────────────────────────────
        R    = 6371
        dlat = math.radians(hlat - lat)
        dlon = math.radians(hlon - lon)
        a    = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(hlat)) * math.sin(dlon/2)**2
        dist_km = round(R * 2 * math.asin(math.sqrt(a)), 2)

        hospitals.append({
            "name"          : name,
            "lat"           : hlat,
            "lon"           : hlon,
            "address"       : address,
            "phone"         : phone,
            "website"       : website,
            "type"          : amenity.title(),
            "dist_km"       : dist_km,
            "is_specialized": is_match and specialist != "General Physician",
        })

    hospitals.sort(key=lambda x: x["dist_km"])

    # If strict filter returns nothing, fall back to all hospitals in radius
    if not hospitals:
        return fetch_all_hospitals_fallback(lat, lon, radius_m)

    return hospitals[:50]


def fetch_all_hospitals_fallback(lat: float, lon: float, radius_m: int) -> list:
    """Fallback: return all hospitals when specialist filter finds nothing."""
    import requests, math

    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """
    try:
        resp = requests.post(overpass_url, data={"data": query}, timeout=20)
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
    except Exception:
        return []

    hospitals = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or "Unnamed Hospital"
        if el["type"] == "node":
            hlat, hlon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center", {})
            hlat, hlon = center.get("lat"), center.get("lon")
        if not hlat or not hlon:
            continue
        R    = 6371
        dlat = math.radians(hlat - lat)
        dlon = math.radians(hlon - lon)
        a    = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(hlat)) * math.sin(dlon/2)**2
        dist_km = round(R * 2 * math.asin(math.sqrt(a)), 2)
        hospitals.append({
            "name"          : name,
            "lat"           : hlat,
            "lon"           : hlon,
            "address"       : "Address not available",
            "phone"         : tags.get("phone","—"),
            "website"       : "",
            "type"          : "Hospital",
            "dist_km"       : dist_km,
            "is_specialized": False,
        })
    hospitals.sort(key=lambda x: x["dist_km"])
    return hospitals[:50]


def get_ip_location():
    """Auto-detect location via IP — no GPS permission needed."""
    try:
        import requests as _r
        r = _r.get("https://ipinfo.io/json", timeout=3)
        if r.status_code == 200:
            loc = r.json().get("loc", "")
            if loc:
                return float(loc.split(",")[0]), float(loc.split(",")[1])
    except Exception:
        pass
    return 20.5937, 78.9629  # Default: India centre


def nearby_hospitals_section(disease_name: str):
    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        st.warning("⚠️ Install folium and streamlit-folium to use the interactive map:\n```\npip install folium streamlit-folium\n```")
        return

    specialist, emoji = get_specialist(disease_name)
    safe_key = "map_" + "".join(c if c.isalnum() else "_" for c in disease_name.lower())

    st.markdown(f"""
    <div style="background:#1e293b; border:1.5px solid #334155; border-radius:14px;
                padding:1.2rem 1.6rem; margin:1rem 0 0.5rem 0;">
        <div style="font-size:1.1rem; font-weight:700; color:#f1f5f9; margin-bottom:.3rem;">
            🗺️ &nbsp; Specialized Doctors & Hospitals Near You
        </div>
        <div style="color:#94a3b8; font-size:.88rem; line-height:1.5;">
            Showing <strong style="color:#38bdf8;">{specialist}</strong> hospitals within 10 km.
            <br>Click <b>📍 Auto-Detect</b> or <b>click anywhere on the map</b> to search that location.
            <br><span style="color:#f97316;">⭐ Orange pins</span> = specialist hospitals &nbsp;|&nbsp;
            <span style="color:#3b82f6;">🔵 Blue pins</span> = general hospitals
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-detect button ────────────────────────────────────────────────────
    if st.button("📍 Auto-Detect My Location", key=f"{safe_key}_autodetect"):
        lat, lon = get_ip_location()
        st.session_state[f"{safe_key}_center"]  = (lat, lon)
        st.session_state[f"{safe_key}_clicked"] = (lat, lon)
        st.session_state[f"{safe_key}_zoom"]    = 12
        with st.spinner("🔍 Finding specialist hospitals near you…"):
            hospitals = fetch_nearby_hospitals(lat, lon, specialist, radius_m=10000)
            st.session_state[f"{safe_key}_results"] = hospitals

    # ── Handle map click ──────────────────────────────────────────────────────
    map_state = st.session_state.get(f"{safe_key}_st_map")
    if map_state and map_state.get("last_clicked"):
        new_lat = map_state["last_clicked"]["lat"]
        new_lon = map_state["last_clicked"]["lng"]
        if st.session_state.get(f"{safe_key}_clicked") != (new_lat, new_lon):
            st.session_state[f"{safe_key}_clicked"] = (new_lat, new_lon)
            st.session_state[f"{safe_key}_center"]  = (new_lat, new_lon)
            st.session_state[f"{safe_key}_zoom"]    = 12
            with st.spinner("🔍 Searching specialist hospitals at clicked location…"):
                hospitals = fetch_nearby_hospitals(new_lat, new_lon, specialist, radius_m=10000)
                st.session_state[f"{safe_key}_results"] = hospitals

    # ── Default map center ────────────────────────────────────────────────────
    if f"{safe_key}_center" not in st.session_state:
        st.session_state[f"{safe_key}_center"] = (20.5937, 78.9629)
        st.session_state[f"{safe_key}_zoom"]   = 5

    clat, clon = st.session_state[f"{safe_key}_center"]
    zoom       = st.session_state.get(f"{safe_key}_zoom", 5)

    # ── Build Folium map ──────────────────────────────────────────────────────
    m = folium.Map(location=[clat, clon], zoom_start=zoom, tiles="CartoDB dark_matter")

    clicked_coords = st.session_state.get(f"{safe_key}_clicked")
    if clicked_coords:
        olat, olon = clicked_coords
        # Search radius circle
        folium.Circle(
            location=[olat, olon], radius=10000,
            color="#38bdf8", fill=True, fill_opacity=0.1, weight=2
        ).add_to(m)
        # Centre pin
        folium.Marker(
            [olat, olon], popup="📍 Search Centre",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
        ).add_to(m)

        results = st.session_state.get(f"{safe_key}_results", [])
        for h in results:
            color = "orange" if h["is_specialized"] else "blue"
            icon  = "star"   if h["is_specialized"] else "h-square"
            gmaps = f"https://www.google.com/maps/dir/?api=1&destination={h['lat']},{h['lon']}"
            popup_html = f"""
            <div style="min-width:180px; font-family:sans-serif;">
                <b style="font-size:13px;">{h['name']}</b><br>
                <span style="color:{'#f97316' if h['is_specialized'] else '#64748b'}; font-size:11px;">
                    {'⭐ ' + specialist if h['is_specialized'] else '🏥 General'}
                </span><br>
                📍 {h['dist_km']} km away<br>
                📞 {h['phone']}<br>
                <a href="{gmaps}" target="_blank" style="color:#3b82f6; font-weight:bold;">🧭 Get Directions</a>
            </div>
            """
            folium.Marker(
                [h["lat"], h["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color=color, icon=icon, prefix="fa")
            ).add_to(m)

    # ── Render map ────────────────────────────────────────────────────────────
    st_folium(m, height=450, width=None, use_container_width=True,
              key=f"{safe_key}_st_map", returned_objects=["last_clicked"])

    # ── Hospital cards ────────────────────────────────────────────────────────
    if clicked_coords:
        hospitals = st.session_state.get(f"{safe_key}_results", [])
        if hospitals:
            spec_count = sum(1 for h in hospitals if h["is_specialized"])
            gen_count  = len(hospitals) - spec_count
            st.success(
                f"✅ Found **{len(hospitals)}** facilities — "
                f"⭐ **{spec_count}** {specialist} specialist + 🏥 **{gen_count}** general"
            )
            for h in hospitals:
                badge_color = "#f97316" if h["is_specialized"] else "#64748b"
                badge_text  = f"⭐ {specialist}" if h["is_specialized"] else f"🏥 General {h['type']}"
                gmaps_url   = f"https://www.google.com/maps/dir/?api=1&destination={h['lat']},{h['lon']}"
                gmaps_view  = f"https://www.google.com/maps/search/{h['name'].replace(' ', '+')}+near+me"

                with st.container():
                    col_info, col_dist = st.columns([5, 1])
                    with col_info:
                        st.markdown(
                            f"**{h['name']}** &nbsp;"
                            f"<span style='background:{badge_color}; color:white; "
                            f"padding:2px 8px; border-radius:10px; font-size:.75rem;'>"
                            f"{badge_text}</span>",
                            unsafe_allow_html=True
                        )
                        phone_text = h["phone"] if h["phone"] != "—" else "Not available"
                        st.caption(f"📞 {phone_text}")
                        bc1, bc2 = st.columns(2)
                        with bc1:
                            st.link_button("🗺️ View on Maps",   gmaps_view, use_container_width=True)
                        with bc2:
                            st.link_button("🧭 Get Directions", gmaps_url,  use_container_width=True)
                    with col_dist:
                        st.markdown(
                            f"<div style='text-align:center; padding-top:.8rem;'>"
                            f"<span style='color:#38bdf8; font-size:1.2rem; font-weight:700;'>{h['dist_km']} km</span>"
                            f"<br><span style='color:#64748b; font-size:.75rem;'>away</span></div>",
                            unsafe_allow_html=True
                        )
                    st.divider()
        else:
            st.warning("No hospitals found at this location. Try clicking a more populated area or use Auto-Detect.")


# ── Page config ───────────────────────────────────────────────────────────────


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CrowdMed Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

setup_database()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }
  .header-box {
    background: linear-gradient(135deg, #0f4c81, #1a8a6e);
    padding: 2rem 2.5rem; border-radius: 14px;
    color: white; margin-bottom: 1.5rem;
  }
  .header-box h1 { margin: 0; font-size: 2rem; }
  .header-box p  { margin: .3rem 0 0; opacity: .85; }
  .card {
    background: #1e293b; border-radius: 10px;
    padding: 1.1rem 1.4rem; border: 1px solid #334155;
    margin-bottom: .8rem;
  }
  .badge {
    display:inline-block; padding:3px 10px; border-radius:20px;
    font-size:.75rem; font-weight:700; margin:2px;
  }
  .b-kaggle { background:#20beff22; color:#20beff; border:1px solid #20beff; }
  .b-pubmed { background:#ff6b6b22; color:#ff6b6b; border:1px solid #ff6b6b; }
  .b-reddit { background:#ff4500;   color:#fff; }
  .match-bar { height:8px; border-radius:4px; background:#0ea5e9; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <h1>🧬 CrowdMed Intelligence Platform</h1>
  <p>Turning scattered patient experiences into structured, trusted insights</p>
  <p style="font-size:.8rem;opacity:.7">Sources: Kaggle Dataset &nbsp;•&nbsp; PubMed Research &nbsp;•&nbsp; Reddit Discussions</p>
</div>
""", unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════════════════════════
# Disease Search
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Search by Disease Name")

c1, c2 = st.columns([4, 1])
with c1:
    disease_input = st.text_input("Disease", placeholder="e.g. diabetes, asthma, malaria…",
                                  label_visibility="collapsed")
with c2:
    fetch = st.button("🚀 Fetch Data", use_container_width=True, type="primary")

if fetch and disease_input.strip():
    d = disease_input.strip().lower()

    # Clear old data
    conn = sqlite3.connect(DB_PATH)
    for tbl in ("disease_data","pubmed_articles","structured_data",
                "reddit_raw","reddit_structured"):
        conn.execute(f"DELETE FROM {tbl} WHERE LOWER(disease)=?", (d,))
    conn.commit(); conn.close()

    prog = st.progress(0, "Starting…")
    info = st.empty()

    info.info("📦 Fetching Kaggle dataset…")
    run_kaggle_pipeline(d);   prog.progress(33, "Kaggle ✓")

    info.info("🔬 Fetching PubMed articles…")
    run_pubmed_pipeline(d);   prog.progress(66, "PubMed ✓")

    info.info("💬 Fetching Reddit discussions…")
    run_reddit_pipeline(d);   prog.progress(100, "Done!")

    info.success(f"✅ Data collected for **{d.title()}**")

# ── Results ───────────────────────────────────────────────────────────────
if disease_input.strip():
    summary = get_disease_summary(disease_input.strip())

    if not summary:
        st.warning("No data found. Click **Fetch Data** to collect information first.")
        st.stop()

    df = summary["raw_df"]

    # ── Overview metrics ──
    st.markdown("### 📈 Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records",    summary["total_records"])
    m2.metric("Data Sources",     len(summary["sources"]))
    m3.metric("Unique Symptoms",  len(summary["symptoms"]))
    m4.metric("Treatments Found", len(summary["treatments"]))

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════
    # SOURCE TABS — each with its own AI analysis
    # ════════════════════════════════════════════════════════════════════
    tab_kaggle, tab_pubmed, tab_reddit, tab_compare = st.tabs([
        "📦 Kaggle Dataset",
        "🔬 PubMed Research",
        "💬 Reddit Discussions",
        "🤖 AI Comparison",
    ])

    # ── helper: call Groq AI (free, no credit card) ──────────────────────
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

    def ai_analyze(prompt: str, cache_key: str) -> str:
        """Call Groq API — free tier, no credit card needed."""
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        if not GROQ_API_KEY:
            return (
                "⚠️ GROQ_API_KEY not set.\n\n"
                "Get a FREE key (no credit card) at https://console.groq.com\n\n"
                "Then in PowerShell:\n"
                "$env:GROQ_API_KEY='gsk_your-key-here'\n"
                "python -m streamlit run app.py"
            )

        import requests as _req, time, re

        url  = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model"    : "llama-3.3-70b-versatile",
            "messages" : [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
            "temperature": 0.4,
        }

        debug = st.empty()

        for attempt in range(5):
            try:
                debug.info(f"🔄 Attempt {attempt+1}/5 — contacting Groq AI…")
                resp = _req.post(url, headers=headers, json=body, timeout=60)

                if resp.status_code == 429:
                    err_msg = resp.json().get("error", {}).get("message", "")
                    match   = re.search(r"try again in ([\d.]+)s", err_msg)
                    wait    = int(float(match.group(1))) + 3 if match else 30
                    for remaining in range(wait, 0, -1):
                        debug.warning(f"⏳ Rate limited — retrying in **{remaining}s** (attempt {attempt+1}/5)")
                        time.sleep(1)
                    continue

                if resp.status_code != 200:
                    err = resp.json().get("error", {}).get("message", resp.text)
                    debug.error(f"❌ HTTP {resp.status_code}: {err}")
                    return f"⚠️ Error {resp.status_code}: {err}"

                result = resp.json()["choices"][0]["message"]["content"]
                debug.empty()
                st.session_state[cache_key] = result
                return result

            except Exception as e:
                debug.error(f"❌ Attempt {attempt+1} failed: {str(e)}")
                if attempt < 4:
                    time.sleep(5)
                    continue
                return f"⚠️ Failed after 5 attempts: {str(e)}"

        return "⚠️ Failed after all retries."

    def render_ai_box(text: str, color: str, label: str):
        """Render the styled AI response box."""
        border_map = {"blue": "#1e40af", "red": "#991b1b",
                      "orange": "#7c2d12", "purple": "#581c87"}
        label_color_map = {"blue": "#93c5fd", "red": "#fca5a5",
                           "orange": "#fdba74", "purple": "#d8b4fe"}
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid {border_map.get(color,'#1e40af')};
                    border-radius:12px; padding:1.2rem 1.5rem; margin-top:.5rem;">
            <div style="color:{label_color_map.get(color,'#93c5fd')}; font-size:.8rem;
                        font-weight:700; text-transform:uppercase;
                        letter-spacing:.07em; margin-bottom:.7rem;">
                🤖 {label}
            </div>
            <div style="color:#e2e8f0; font-size:.93rem; line-height:1.7;">
                {text.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── pie chart helper ─────────────────────────────────────────────────────
    def source_pie(data_dict: dict, title: str, colors: list):
        """Render one donut pie chart from a {label: count} dict."""
        if not data_dict:
            st.info(f"No data available for {title}.")
            return
        items  = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:12]
        labels = [i[0] for i in items]
        values = [i[1] for i in items]
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.42,
            marker=dict(
                colors=colors[:len(labels)],
                line=dict(color="#ffffff", width=2)
            ),
            # Show only percent inside slices — no label text inside
            textinfo="percent",
            textposition="inside",
            textfont=dict(size=12, color="#000000"),
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            # Show full labels in legend instead
            showlegend=True,
        ))
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color="#1e293b", size=14, family="Arial"),
                x=0.5
            ),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#1e293b", size=11),
            legend=dict(
                font=dict(size=11, color="#1e293b"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#e2e8f0",
                borderwidth=1,
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
            ),
            margin=dict(t=40, b=10, l=10, r=160),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    BLUE_PALETTE   = ["#0ea5e9","#38bdf8","#7dd3fc","#bae6fd","#0284c7",
                      "#0369a1","#075985","#164e63","#06b6d4","#22d3ee",
                      "#67e8f9","#a5f3fc"]
    GREEN_PALETTE  = ["#22c55e","#4ade80","#86efac","#16a34a","#15803d",
                      "#166534","#14532d","#bbf7d0","#4ade80","#6ee7b7",
                      "#34d399","#10b981"]
    ORANGE_PALETTE = ["#f97316","#fb923c","#fdba74","#ea580c","#c2410c",
                      "#9a3412","#7c2d12","#fed7aa","#fbbf24","#fcd34d",
                      "#fde68a","#fef3c7"]
    RED_PALETTE    = ["#ef4444","#f87171","#fca5a5","#dc2626","#b91c1c",
                      "#991b1b","#7f1d1d","#fee2e2","#f97316","#fb923c",
                      "#fdba74","#fed7aa"]

    # ════════════════════════════════════════════════════════
    # TAB 1 — KAGGLE
    # ════════════════════════════════════════════════════════
    with tab_kaggle:
        st.markdown("#### 📦 Kaggle Dataset Analysis")
        kdf = df[df["source"] == "Kaggle"]
        if kdf.empty:
            st.warning("No Kaggle data found. Click **Fetch Data** first.")
        else:
            def _counts(col):
                combined = ",".join(kdf[col].dropna())
                items = [s.strip() for s in combined.split(",") if s.strip()]
                return pd.Series(items).value_counts().to_dict()

            k_sym  = _counts("symptoms")
            k_tr   = _counts("treatments")
            stages = kdf["stage"].dropna().unique().tolist()

            # ── Metrics ──
            k1, k2, k3 = st.columns(3)
            k1.metric("Records",         len(kdf))
            k2.metric("Unique Symptoms",  len(k_sym))
            k3.metric("Treatments Found", len(k_tr))

            # ── Two pie charts side by side ──
            pc1, pc2 = st.columns(2)
            with pc1:
                source_pie(k_sym, "🤒 Symptoms Distribution", BLUE_PALETTE)
            with pc2:
                source_pie(k_tr,  "💊 Treatments Distribution", GREEN_PALETTE)

            # Stage info
            if stages:
                st.markdown("##### 📋 Disease Properties")
                for s in stages:
                    st.markdown(f"- {s}")

            with st.expander("🗃️ Raw Kaggle Records"):
                st.dataframe(kdf.drop(columns=["id","created_at"], errors="ignore"),
                             use_container_width=True)

    # ════════════════════════════════════════════════════════
    # TAB 2 — PUBMED
    # ════════════════════════════════════════════════════════
    with tab_pubmed:
        st.markdown("#### 🔬 PubMed Research Analysis")

        # ── Always re-extract live from pubmed_articles in DB ──────────
        # (disease_data PubMed rows may have empty fields from old pipeline)
        conn_pm = sqlite3.connect(DB_PATH)
        pm_rows = pd.read_sql(
            "SELECT title, abstract FROM pubmed_articles WHERE LOWER(disease) LIKE ?",
            conn_pm, params=(f"%{disease_input.strip().lower()}%",)
        )
        conn_pm.close()

        articles = summary["pubmed_articles"]

        if pm_rows.empty and not articles:
            st.warning("No PubMed data found. Click **Fetch Data** first.")
        else:
            from pipelines.pubmed_pipeline import extract_structured as pm_extract

            # Re-extract from full titles+abstracts stored in DB
            all_syms, all_treats, all_sides = [], [], []
            for _, row in pm_rows.iterrows():
                s, t, se = pm_extract(
                    row.get("abstract","") or "",
                    row.get("title","")    or ""
                )
                all_syms  += [x.strip() for x in s.split(",")  if x.strip()]
                all_treats+= [x.strip() for x in t.split(",")  if x.strip()]
                all_sides += [x.strip() for x in se.split(",") if x.strip()]

            p_sym  = pd.Series(all_syms ).value_counts().to_dict()
            p_tr   = pd.Series(all_treats).value_counts().to_dict()
            p_side = pd.Series(all_sides ).value_counts().to_dict()

            # If still empty, warn and show re-fetch button
            if not p_sym and not p_tr and not p_side:
                st.warning(
                    "⚠️ PubMed abstracts in your database are truncated (old data). "
                    "Click **Re-fetch PubMed** below to get fresh full abstracts."
                )
                if st.button("🔄 Re-fetch PubMed Data", key="refetch_pubmed", type="primary"):
                    d = disease_input.strip().lower()
                    conn_c = sqlite3.connect(DB_PATH)
                    conn_c.execute("DELETE FROM pubmed_articles   WHERE LOWER(disease)=?", (d,))
                    conn_c.execute("DELETE FROM structured_data   WHERE LOWER(disease)=?", (d,))
                    conn_c.execute("DELETE FROM disease_data WHERE LOWER(disease)=? AND source='PubMed'", (d,))
                    conn_c.commit(); conn_c.close()
                    with st.spinner("Re-fetching PubMed articles with full abstracts…"):
                        run_pubmed_pipeline(d)
                    st.success("✅ PubMed re-fetched! Scroll up and the charts will update.")
                    st.rerun()
            else:
                # ── Metrics ──
                p1, p2, p3 = st.columns(3)
                p1.metric("Articles Retrieved", len(pm_rows))
                p2.metric("Symptoms Extracted", len(p_sym))
                p3.metric("Side Effects Found",  len(p_side))

                # ── Three pie charts side by side ──
                pc1, pc2, pc3 = st.columns(3)
                with pc1:
                    source_pie(p_sym,  "🤒 Symptoms",    BLUE_PALETTE)
                with pc2:
                    source_pie(p_tr,   "💊 Treatments",  GREEN_PALETTE)
                with pc3:
                    source_pie(p_side, "⚠️ Side Effects", RED_PALETTE)

            # Article list always shown
            if articles:
                st.markdown("##### 📄 Retrieved Articles")
                for art in articles[:15]:
                    year  = art.get("year",  "")
                    title = art.get("title", "")
                    st.markdown(f"""
                    <div style="background:#1e293b; border-left:3px solid #ff6b6b;
                                border-radius:6px; padding:.6rem 1rem; margin:.3rem 0;
                                color:#e2e8f0; font-size:.88rem;">
                        <span style="color:#ff6b6b; font-weight:700;">{year}</span>
                        &nbsp;—&nbsp; {title}
                    </div>
                    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 3 — REDDIT
    # ════════════════════════════════════════════════════════
    with tab_reddit:
        st.markdown("#### 💬 Reddit Patient Discussions Analysis")
        rdf = df[df["source"] == "Reddit"]
        rs  = summary["reddit_summary"]

        if rdf.empty:
            st.warning("No Reddit data found. Click **Fetch Data** first.")
        else:
            def _rcounts(col):
                combined = ",".join(rdf[col].dropna())
                items = [s.strip() for s in combined.split(",") if s.strip()]
                return pd.Series(items).value_counts().to_dict()

            r_sym = _rcounts("symptoms")
            r_tr  = _rcounts("treatments")

            # ── Metrics ──
            r1, r2, r3 = st.columns(3)
            r1.metric("Posts Analyzed",   len(rdf))
            r2.metric("Symptoms Found",   len(r_sym))
            r3.metric("Treatments Found", len(r_tr))

            # ── Two pie charts side by side ──
            pc1, pc2 = st.columns(2)
            with pc1:
                source_pie(r_sym, "🤒 Symptoms by Patients",   BLUE_PALETTE)
            with pc2:
                source_pie(r_tr,  "💊 Treatments by Patients", ORANGE_PALETTE)

            # ── Deep Patient Insights — structured table from reddit_raw ──
            if rs:
                st.markdown("##### 🧠 Patient Experience Insights Table")
                st.caption("Each row is extracted from a real Reddit post — showing what stage, symptoms, treatments, recovery time, and causes that patient reported.")

                # Pull raw posts from DB for this disease
                conn_r = sqlite3.connect(DB_PATH)
                raw_posts = pd.read_sql(
                    "SELECT title, text, url FROM reddit_raw WHERE LOWER(disease) LIKE ?",
                    conn_r, params=(f"%{disease_input.strip().lower()}%",)
                )
                conn_r.close()

                STAGE_KW    = ["stage 1","stage 2","stage 3","stage 4","early","advanced",
                               "late","chronic","acute","recovery","remission"]
                SYMPTOM_KW  = ["fatigue","headache","nausea","vomiting","fever","cough",
                               "pain","dizziness","weakness","rash","swelling","anxiety",
                               "depression","weight loss","chest pain","breathing"]
                TREATMENT_KW= ["insulin","metformin","chemotherapy","radiation","surgery",
                               "therapy","antibiotics","medication","steroids","ibuprofen",
                               "paracetamol","levothyroxine","tamoxifen"]
                CAUSE_KW    = ["stress","smoking","infection","genetics","obesity",
                               "alcohol","poor diet","hormonal","iodine deficiency"]
                TIME_WORDS  = ["days","weeks","months","years","day","week","month","year"]

                def _extract_post(text):
                    t = text.lower()
                    words = t.split()

                    stage    = next((k for k in STAGE_KW    if k in t), "—")
                    symptoms = ", ".join([k for k in SYMPTOM_KW  if k in t]) or "—"
                    treats   = ", ".join([k for k in TREATMENT_KW if k in t]) or "—"
                    causes   = ", ".join([k for k in CAUSE_KW    if k in t]) or "—"

                    recovery = "—"
                    for i, w in enumerate(words):
                        if w.isdigit() and i + 1 < len(words):
                            if words[i+1] in TIME_WORDS:
                                recovery = f"{w} {words[i+1]}"
                                break

                    return stage, symptoms, treats, causes, recovery

                if not raw_posts.empty:
                    table_rows = []
                    for _, post in raw_posts.iterrows():
                        combined = (post.get("title","") or "") + " " + (post.get("text","") or "")
                        if not combined.strip():
                            continue
                        stage, syms, treats, causes, recovery = _extract_post(combined)
                        if syms == "—" and treats == "—" and stage == "—":
                            continue
                        table_rows.append({
                            "stage"   : stage,
                            "symptoms": syms,
                            "treats"  : treats,
                            "causes"  : causes,
                            "recovery": recovery,
                            "url"     : post.get("url",""),
                        })

                    if table_rows:
                        # ── Group by stage — each stage appears only once ──
                        from collections import defaultdict
                        grouped = defaultdict(lambda: {
                            "symptoms": set(), "treats": set(),
                            "causes": set(), "recovery": set(), "urls": []
                        })

                        for row in table_rows:
                            key = row["stage"]
                            if row["symptoms"] != "—":
                                grouped[key]["symptoms"].update(
                                    [s.strip() for s in row["symptoms"].split(",") if s.strip()])
                            if row["treats"] != "—":
                                grouped[key]["treats"].update(
                                    [t.strip() for t in row["treats"].split(",") if t.strip()])
                            if row["causes"] != "—":
                                grouped[key]["causes"].update(
                                    [c.strip() for c in row["causes"].split(",") if c.strip()])
                            if row["recovery"] != "—":
                                grouped[key]["recovery"].add(row["recovery"])
                            if row["url"]:
                                grouped[key]["urls"].append(row["url"])

                        # ── Helper: convert recovery strings to days, average, convert back ──
                        def avg_recovery(recovery_set: set) -> str:
                            """Convert a set of '3 weeks', '2 months' etc to a single averaged value."""
                            TO_DAYS = {
                                "day": 1,   "days": 1,
                                "week": 7,  "weeks": 7,
                                "month": 30,"months": 30,
                                "year": 365,"years": 365,
                            }
                            total_days = []
                            for r in recovery_set:
                                parts = r.strip().split()
                                if len(parts) == 2 and parts[0].isdigit():
                                    num  = int(parts[0])
                                    unit = parts[1].lower()
                                    if unit in TO_DAYS:
                                        total_days.append(num * TO_DAYS[unit])

                            if not total_days:
                                return "—"

                            avg = sum(total_days) / len(total_days)

                            # Convert back to most readable unit
                            if avg >= 365:
                                val = round(avg / 365, 1)
                                return f"~{val} year{'s' if val != 1 else ''}"
                            elif avg >= 30:
                                val = round(avg / 30, 1)
                                return f"~{val} month{'s' if val != 1 else ''}"
                            elif avg >= 7:
                                val = round(avg / 7, 1)
                                return f"~{val} week{'s' if val != 1 else ''}"
                            else:
                                val = round(avg)
                                return f"~{val} day{'s' if val != 1 else ''}"

                        merged_rows = []
                        for stage_key, data in grouped.items():
                            merged_rows.append({
                                "📍 Stage"         : stage_key,
                                "🤒 Symptoms"      : ", ".join(sorted(data["symptoms"])) or "—",
                                "💊 Treatments"    : ", ".join(sorted(data["treats"]))   or "—",
                                "🦠 Causes"        : ", ".join(sorted(data["causes"]))   or "—",
                                "⏱️ Avg Recovery"  : avg_recovery(data["recovery"]),
                                "🔗 Sources"       : data["urls"],
                            })

                        # Sort: named stages first, then "—"
                        stage_order = ["stage 1","stage 2","stage 3","stage 4",
                                       "early","advanced","late","chronic","acute",
                                       "recovery","remission","—"]
                        merged_rows.sort(key=lambda x: stage_order.index(x["📍 Stage"])
                                         if x["📍 Stage"] in stage_order else 99)

                        insight_df = pd.DataFrame(merged_rows)

                        st.dataframe(
                            insight_df.drop(columns=["🔗 Sources"]),
                            use_container_width=True,
                            hide_index=True,
                            height=min(450, 60 + len(insight_df) * 45),
                        )

                        # Source links grouped by stage
                        with st.expander(f"🔗 View Source Links by Stage"):
                            for row in merged_rows:
                                urls = row["🔗 Sources"]
                                if urls:
                                    st.markdown(f"**{row['📍 Stage'].title()}** — {len(urls)} post(s)")
                                    for url in urls[:3]:
                                        st.markdown(f"""
                                        <div style="background:#1e293b; border-left:3px solid #ff4500;
                                                    border-radius:6px; padding:.4rem 1rem; margin:.2rem 0 .2rem 1rem;">
                                            <a href="{url}" target="_blank"
                                               style="color:#fb923c; font-size:.82rem;">{url}</a>
                                        </div>
                                        """, unsafe_allow_html=True)
                    else:
                        st.info("No structured data could be extracted from the Reddit posts for this disease.")
                else:
                    # Fallback: show aggregated summary as a clean table
                    summary_rows = [
                        {"Category": "🦠 Causes",           "Details": rs.get("causes","—")            or "—"},
                        {"Category": "🛡️ Precautions",      "Details": rs.get("precautions","—")       or "—"},
                        {"Category": "🍎 Recommended Foods", "Details": rs.get("recommended_food","—")  or "—"},
                        {"Category": "⏱️ Recovery Times",   "Details": rs.get("recovery_time","—")     or "—"},
                        {"Category": "✅ Treatment Benefits","Details": rs.get("treatment_benefits","—")or "—"},
                        {"Category": "📍 Disease Stage",     "Details": rs.get("stage","—")             or "—"},
                    ]
                    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

            # Reddit links
            if summary["reddit_links"]:
                st.markdown("##### 🔗 Discussion Links")
                for link in summary["reddit_links"]:
                    st.markdown(f"""
                    <div style="background:#1e293b; border-left:3px solid #ff4500;
                                border-radius:6px; padding:.5rem 1rem; margin:.3rem 0;">
                        <a href="{link}" target="_blank"
                           style="color:#fb923c; font-size:.85rem;">{link}</a>
                    </div>
                    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 4 — AI COMPARISON
    # ════════════════════════════════════════════════════════
    with tab_compare:
        st.markdown("#### 🤖 AI Cross-Source Comparison")
        st.caption("Claude compares what Kaggle, PubMed, and Reddit say about this disease — highlighting agreements, differences, and unique insights from each source.")

        # ── API key status ────────────────────────────────────────────────
        if not GROQ_API_KEY:
            st.error("""
**⚠️ GROQ_API_KEY not set — AI Comparison won't work.**

Get a **100% free** key (no credit card) at: https://console.groq.com

Then in PowerShell:
```powershell
$env:GROQ_API_KEY="gsk_your-key-here"
python -m streamlit run app.py
```
            """)
        else:
            st.success(f"✅ Groq API key detected ({GROQ_API_KEY[:8]}…)")

        ai_key_cmp = f"ai_compare_{disease_input.strip().lower()}"

        # Gather data from all 3 sources for the prompt
        kdf_cmp = df[df["source"] == "Kaggle"]
        pdf_cmp = df[df["source"] == "PubMed"]
        rdf_cmp = df[df["source"] == "Reddit"]
        rs_cmp  = summary["reddit_summary"]

        def _src_counts(src_df, col):
            combined = ",".join(src_df[col].dropna())
            items = [s.strip() for s in combined.split(",") if s.strip()]
            return list(pd.Series(items).value_counts().head(8).index)

        k_syms  = ", ".join(_src_counts(kdf_cmp, "symptoms"))   or "none"
        k_treats= ", ".join(_src_counts(kdf_cmp, "treatments"))  or "none"
        p_syms  = ", ".join(_src_counts(pdf_cmp, "symptoms"))   or "none"
        p_treats= ", ".join(_src_counts(pdf_cmp, "treatments"))  or "none"
        p_sides = ", ".join(_src_counts(pdf_cmp, "side_effects"))or "none"
        r_syms  = ", ".join(_src_counts(rdf_cmp, "symptoms"))   or "none"
        r_treats= ", ".join(_src_counts(rdf_cmp, "treatments"))  or "none"
        r_causes= rs_cmp.get("causes","none") if rs_cmp else "none"
        r_recov = rs_cmp.get("recovery_time","none") if rs_cmp else "none"
        r_food  = rs_cmp.get("recommended_food","none") if rs_cmp else "none"
        articles_count = len(summary["pubmed_articles"])
        reddit_count   = len(rdf_cmp)

        if st.button("✨ Generate AI Comparison", key="btn_ai_compare", type="primary"):
            prompt = f"""You are a medical AI expert. Compare and contrast what three different data sources say about "{disease_input.strip()}":

--- KAGGLE DATASET (Structured medical database) ---
Symptoms: {k_syms}
Treatments: {k_treats}

--- PUBMED RESEARCH ({articles_count} scientific articles) ---
Symptoms from abstracts: {p_syms}
Treatments in literature: {p_treats}
Side effects documented: {p_sides}

--- REDDIT PATIENT DISCUSSIONS ({reddit_count} posts) ---
Symptoms patients report: {r_syms}
Treatments patients mention: {r_treats}
Causes attributed by patients: {r_causes}
Recovery times mentioned: {r_recov}
Foods recommended: {r_food}

Provide a thorough cross-source comparison covering:
1. **What All Three Sources Agree On** — symptoms/treatments consistent across Kaggle, PubMed, and Reddit
2. **Clinical Data vs Patient Reality** — where PubMed/Kaggle and Reddit differ, and why that matters
3. **Unique Insights per Source**
   - Kaggle only: structured facts not mentioned elsewhere
   - PubMed only: research findings not in patient discussions
   - Reddit only: patient experiences not captured in clinical data
4. **Treatment Consensus** — which treatments appear across multiple sources vs ones only mentioned by patients
5. **Trust & Reliability Assessment** — how much to trust each source for this disease
6. **Overall Recommendation** — synthesized advice combining all three sources

Be analytical, balanced, and highlight genuinely useful differences. Do not diagnose."""
            st.info("🤖 Sending to Gemini AI… auto-retrying if rate limited (up to 5 min).")
            result = ai_analyze(prompt, ai_key_cmp)
            st.session_state[ai_key_cmp] = result
            st.rerun()

        if ai_key_cmp in st.session_state:
            render_ai_box(st.session_state[ai_key_cmp], "purple", "AI Cross-Source Comparison")
        else:
            # Show a preview card of the data before analysis
            st.markdown("##### 📊 Data Available for Comparison")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("""
                <div style="background:#1e293b;border-left:4px solid #20beff;
                            border-radius:8px;padding:1rem;text-align:center;">
                    <div style="color:#20beff;font-size:.8rem;font-weight:700;
                                text-transform:uppercase;margin-bottom:.4rem;">📦 Kaggle</div>
                    <div style="color:#f1f5f9;font-size:1.4rem;font-weight:800;">
                """ + str(len(kdf_cmp)) + """</div>
                    <div style="color:#94a3b8;font-size:.8rem;">structured records</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("""
                <div style="background:#1e293b;border-left:4px solid #ff6b6b;
                            border-radius:8px;padding:1rem;text-align:center;">
                    <div style="color:#ff6b6b;font-size:.8rem;font-weight:700;
                                text-transform:uppercase;margin-bottom:.4rem;">🔬 PubMed</div>
                    <div style="color:#f1f5f9;font-size:1.4rem;font-weight:800;">
                """ + str(articles_count) + """</div>
                    <div style="color:#94a3b8;font-size:.8rem;">research articles</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown("""
                <div style="background:#1e293b;border-left:4px solid #ff4500;
                            border-radius:8px;padding:1rem;text-align:center;">
                    <div style="color:#ff4500;font-size:.8rem;font-weight:700;
                                text-transform:uppercase;margin-bottom:.4rem;">💬 Reddit</div>
                    <div style="color:#f1f5f9;font-size:1.4rem;font-weight:800;">
                """ + str(reddit_count) + """</div>
                    <div style="color:#94a3b8;font-size:.8rem;">patient posts</div>
                </div>
                """, unsafe_allow_html=True)
            st.info("👆 Click **Generate AI Comparison** to get Claude's full cross-source analysis.")

    # ── Doctor Recommendation — ABOVE the map ────────────────────────────────
    st.markdown("---")
    doctor_recommendation_box(disease_input.strip())

    # ── Nearby Hospitals — only show if user clicked Yes ─────────────────────
    safe_doc_key = "doc_" + "".join(
        c if c.isalnum() else "_" for c in disease_input.strip().lower()
    )
    if st.session_state.get(safe_doc_key) == "yes":
        st.markdown("---")
        nearby_hospitals_section(disease_input.strip())



