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
        db[artist_id] = {"units": 20, "bg_choice": "Standard", "gallery": []}
        save_db(db)
    return db[artist_id]

def update_user(artist_id, key, value):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {"units": 20, "bg_choice": "Standard", "gallery": []}
    db[artist_id][key] = value
    save_db(db)

def add_to_gallery(artist, name, img_url, audio_url):
    db = load_db()
    if artist not in db:
        db[artist] = {"units": 20, "bg_choice": "Standard", "gallery": []}
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
# 1. DESIGN & BAKGRUNDS-VAL
# =========================
BACKGROUNDS = {
    "Standard": "https://replicate.delivery",
    "Cyber City": "https://replicate.delivery",
    "Neon Abstract": "https://replicate.delivery",
    "Deep Space": "https://replicate.delivery"
}

def apply_custom_design(bg_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                        url("{bg_url}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
            color: white;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(0, 0, 0, 0.4) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        .stMarkdown, label, p, h1, h2, h3, [data-testid="stMetricValue"], .stSelectbox label {{
            color: white !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0.4);
            border-radius: 10px;
            padding: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# 2. AI-FUNKTIONER (Låst)
# =========================
def generate_image(prompt):
    try:
        res = replicate.run("black-forest-labs/flux-schnell", input={{"prompt": prompt}})
        return str(res[0]) if isinstance(res, list) else str(res)
    except Exception as e:
        st.error(f"AI-fel: {{e}}")
        return None

# =========================
# 3. APP-STRUKTUR
# =========================
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", layout="wide")
init_user_db()

if "artist" not in st.session_state: st.session_state.artist = "ANONYM"
if "agreed" not in st.session_state: st.session_state.agreed = False

# Hämta användardata och applicera bakgrund
user = load_user(st.session_state.artist)
current_bg_name = user.get("bg_choice", "Standard")
apply_custom_design(BACKGROUNDS[current_bg_name])

token = st.secrets.get("REPLICATE_API_TOKEN")
if token: os.environ["REPLICATE_API_TOKEN"] = token

# Sidomeny med bakgrundsväljare
with st.sidebar:
    st.title("⚡ STUDIO")
    artist_input = st.text_input("ARTIST ID:", st.session_state.artist).upper()
    if artist_input and artist_input != st.session_state.artist:
        st.session_state.artist = artist_input
        st.rerun()
    
    st.metric("DINA UNITS", f"⚡ {user['units']}")
    
    st.divider()
    # HÄR ÄR BAKGRUNDSVALET
    new_bg = st.selectbox("VÄLJ BAKGRUND:", list(BACKGROUNDS.keys()), index=list(BACKGROUNDS.keys()).index(current_bg_name))
    if new_bg != current_bg_name:
        update_user(st.session_state.artist, "bg_choice", new_bg)
        st.rerun()

    st.divider()
    st.caption("MAXIMUSIKAI v2.5")

if not st.session_state.agreed:
    st.markdown("<h1 style='text-align:center;'>MAXIMUSIKAI SUPER STUDIO</h1>", unsafe_allow_html=True)
    if st.button("ÖPPNA STUDION", use_container_width=True):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# Flikar
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"])

with tab1: # MAGI
    prompt = st.text_area("Skapa ny vision...", placeholder="Beskriv bilden...")
    if st.button("GENERERA", use_container_width=True):
        if user['units'] > 0 or st.session_state.artist == "TOMAS2026":
            with st.spinner("Laddar..."):
                img = generate_image(prompt)
                if img:
                    if st.session_state.artist != "TOMAS2026":
                        update_user(st.session_state.artist, "units", user['units'] - 1)
                    add_to_gallery(st.session_state.artist, prompt, img, None)
                    st.image(img)
                    st.success("Sparad!")
        else:
            st.error("Slut på Units!")

with tab2: # REGI
    st.info("Här kommer video-funktioner.")

with tab3: # MUSIK
    st.write("Musik-studio redo.")

with tab4: # ARKIV
    gallery = user.get("gallery", [])
    for item in reversed(gallery):
        with st.expander(f"📦 {item['name']}"):
            if item['url']: st.image(item['url'])
            if item['audio']: st.audio(item['audio'])

with tab5: # ADMIN
    if st.session_state.artist == "TOMAS2026":
        st.subheader("Admin")
        db = load_db()
        target = st.selectbox("Användare", list(db.keys()))
        amount = st.number_input("Units", 0, 1000, 20)
        if st.button("Uppdatera"):
            update_user(target, "units", amount)
            st.success("Klart!")
