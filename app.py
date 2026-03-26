import streamlit as st
import replicate
import os
import json
import time

# =========================
# 0. DATABAS-LOGIK (Låst)
# =========================
DB_FILE = "users.json"

def init_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_user(artist_id):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {"units": 20, "bg": None, "gallery": []}
        save_db(db)
    return db[artist_id]

def update_user(artist_id, key, value):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {"units": 20, "bg": None, "gallery": []}
    db[artist_id][key] = value
    save_db(db)

def add_to_gallery(artist, name, img_url, audio_url):
    db = load_db()
    if artist not in db:
        db[artist] = {"units": 20, "bg": None, "gallery": []}
    entry = {
        "id": time.time(),
        "artist": artist,
        "name": name[:30] if name else "UNTITLED",
        "url": img_url,
        "audio": audio_url
    }
    db[artist]["gallery"].append(entry)
    save_db(db)

# =========================
# 1. DESIGN & STYLING (Låst med sidebar-fix)
# =========================
def apply_custom_design():
    st.markdown(
        """
        <style>
        /* Huvudappen */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                        url("https://replicate.delivery") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
            color: white;
        }

        /* Sidomenyn (Vänster flik) */
        [data-testid="stSidebar"] {
            background: rgba(0, 0, 0, 0.3) !important; /* Gör den genomskinlig */
            backdrop-filter: blur(10px); /* Valfritt: ger en snygg glaseffekt */
            border-right: 1px solid rgba(255,255,255,0.1);
        }

        /* Textfärger för allt */
        .stMarkdown, label, p, h1, h2, h3, [data-testid="stMetricValue"] {
            color: white !important;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(0,0,0,0.4);
            border-radius: 10px;
            padding: 5px;
        }
        
        /* Input fält */
        .stTextInput input, .stTextArea textarea {
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# 2. AI-FUNKTIONER (Låst)
# =========================
def generate_image(prompt):
    try:
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
        return str(res) if isinstance(res, list) else str(res)
    except Exception as e:
        st.error(f"AI-fel: {e}")
        return None

def generate_music(prompt):
    try:
        res = replicate.run(
            "facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47",
            input={"prompt": prompt, "duration": 8}
        )
        return str(res)
    except Exception as e:
        st.error(f"Musik-fel: {e}")
        return None

# =========================
# 3. APP-STRUKTUR
# =========================
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", layout="wide")
init_user_db()
apply_custom_design()

if "artist" not in st.session_state: st.session_state.artist = "ANONYM"
if "agreed" not in st.session_state: st.session_state.agreed = False

token = st.secrets.get("REPLICATE_API_TOKEN")
if token: os.environ["REPLICATE_API_TOKEN"] = token

# Sidomeny (Nu stylad)
with st.sidebar:
    st.title("⚡ STUDIO")
    artist_input = st.text_input("ARTIST ID:", st.session_state.artist).upper()
    if artist_input: st.session_state.artist = artist_input
    
    user = load_user(st.session_state.artist)
    st.metric("DINA UNITS", f"⚡ {user['units']}")
    st.divider()
    st.caption("MAXIMUSIKAI v2.0")

# Startskärm
if not st.session_state.agreed:
    st.markdown("<h1 style='text-align:center;'>MAXIMUSIKAI SUPER STUDIO</h1>", unsafe_allow_html=True)
    if st.button("ÖPPNA STUDION", use_container_width=True):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# Flikar
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"])

with tab1: # MAGI
    prompt = st.text_area("Beskriv din vision...", placeholder="En cyborg i en regnig neonstad...")
    if st.button("GENERERA", use_container_width=True):
        if user['units'] > 0 or st.session_state.artist == "TOMAS2026":
            with st.spinner("Skapar..."):
                img = generate_image(prompt)
                if img:
                    if st.session_state.artist != "TOMAS2026":
                        update_user(st.session_state.artist, "units", user['units'] - 1)
                    add_to_gallery(st.session_state.artist, prompt, img, None)
                    st.image(img)
                    st.success("Sparad i Arkivet!")
        else:
            st.error("Slut på Units!")

with tab2: # REGI
    st.info("Här kommer video-generering att aktiveras snart.")

with tab3: # MUSIK
    m_prompt = st.text_input("Vad för sorts musik?")
    if st.button("SKAPA LJUD"):
        with st.spinner("Komponerar..."):
            audio = generate_music(m_prompt)
            if audio:
                st.audio(audio)
                add_to_gallery(st.session_state.artist, f"Beat: {m_prompt}", "", audio)

with tab4: # ARKIV
    gallery = load_db().get(st.session_state.artist, {}).get("gallery", [])
    if not gallery:
        st.write("Tomt i arkivet.")
    for item in reversed(gallery):
        with st.expander(f"📦 {item['name']}"):
            if item['url']: st.image(item['url'])
            if item['audio']: st.audio(item['audio'])

with tab5: # ADMIN
    if st.session_state.artist == "TOMAS2026":
        st.subheader("Admin Panel")
        db = load_db()
        target = st.selectbox("Välj användare", list(db.keys()))
        amount = st.number_input("Units", 0, 1000, 20)
        if st.button("Ge Units"):
            update_user(target, "units", amount)
            st.success("Uppdaterat!")
    else:
        st.warning("Endast för TOMAS2026.")
