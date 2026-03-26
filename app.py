import streamlit as st
import replicate
import os
import time
import requests
import json
import os.path

# --- 0. DATABAS FÖR ANVÄNDARE ---
DB_FILE = "users.json"

def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state:
    st.session_state.gallery = []
if "user_db" not in st.session_state:
    st.session_state.user_db = load_user_db()
if "app_bg" not in st.session_state:
    st.session_state.app_bg = "https://images.unsplash.com"
if "agreed" not in st.session_state:
    st.session_state.agreed = False
if "lang" not in st.session_state:
    st.session_state.lang = "Svenska"

# --- 2. DESIGN ENGINE (FIXAD FÖR BAKGRUND) ---
def apply_design():
    accent = "#00d2ff"
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(
            f"""
            <style>
            /* TARGETAR HUVUDCONTAINERN */
            [data-testid="stAppViewContainer"] {{
                background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.5)), 
                            url("{bg_url}") !important;
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
            }}

            /* GÖR ALLA ANDRA LAGER GENOMSKINLIGA */
            [data-testid="stHeader"], 
            [data-testid="stAppViewBlockContainer"],
            .main, .stApp {{
                background-color: transparent !important;
            }}

            .logo-text {{
                font-size: 3.5rem !important;
                font-weight: 900 !important;
                color: #fff !important;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 8px;
                text-shadow: 0 0 15px {accent}, 0 0 30px {accent} !important;
                padding: 20px;
            }}

            /* INPUTS & TEXT AREAS */
            div[data-baseweb="base-input"], .stTextArea textarea, .stTextInput input {{
                background-color: rgba(0,0,0,0.6) !important;
                color: white !important;
                backdrop-filter: blur(15px) !important;
                border: 1px solid {accent}44 !important;
                border-radius: 15px !important;
            }}

            label, p, span, h1, h2, h3 {{
                color: white !important;
                text-shadow: 2px 2px 10px rgba(0,0,0,0.8) !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

apply_design()

# --- 3. LOGIK & SPRÅK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tabs": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "⚙️ ADMIN"],
        "prompt": "VAD SKALL VI SKAPA?",
        "generate": "STARTA GENERERING",
        "units": "UNITS kvar:"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tabs": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "⚙️ ADMIN"],
        "prompt": "WHAT SHALL WE CREATE?",
        "generate": "START GENERATION",
        "units": "UNITS left:"
    }
}

t = texts[st.session_state.lang]

# --- 4. MAIN INTERFACE ---
st.markdown(f'<div class="logo-text">{t["title"]}</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("### VÄLKOMMEN TILL FRAMTIDEN")
        st.session_state.lang = st.selectbox("Välj språk / Select language", ["Svenska", "English"])
        if st.button("GODKÄNN & ÖPPNA STUDION"):
            st.session_state.agreed = True
            st.rerun()
else:
    tab1, tab2, tab3, tab4 = st.tabs(t["tabs"])

    with tab1:
        prompt = st.text_area(t["prompt"], key="magic_p")
        if st.button(t["generate"]):
            with st.status("AI arbetar..."):
                # Exempel på Flux-generering
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                st.session_state.gallery.append(res[0])
                st.session_state.app_bg = res[0] # Sätter bilden som bakgrund direkt!
                st.rerun()
        
        if st.session_state.gallery:
            st.image(st.session_state.gallery[-1], caption="Senaste skapelsen")

    with tab2:
        st.info("Regi-modulen: Här skapar du video.")
        if st.session_state.gallery:
            selected_img = st.selectbox("Välj bild att animera", st.session_state.gallery)
            if st.button("Skapa Video (SVD)"):
                with st.status("Renderar..."):
                    vid = replicate.run("stability-ai/stable-video-diffusion:3f04571e", input={"input_image": selected_img})
                    st.video(vid)

    with tab3:
        st.write("### 🎧 Musikstudio")
        m_prompt = st.text_input("Beskriv beatet:")
        if st.button("Komponera"):
            with st.status("Skapar ljud..."):
                audio = replicate.run("facebookresearch/musicgen:7b539958", input={"prompt": m_prompt})
                st.audio(audio)

    with tab4:
        st.write("### ⚙️ Systeminställningar")
        if st.button("Nollställ design"):
            st.session_state.app_bg = "https://images.unsplash.com"
            st.rerun()
























