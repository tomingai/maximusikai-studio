import streamlit as st
import os
import json
import time

# --- 0. DATABAS-LOGIK ---
DB_FILE = "users.json"

def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_user_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def update_user(user_id, data):
    db = load_user_db()
    if user_id in db:
        db[user_id].update(data)
        save_user_db(db)

# --- 1. SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI 2026", page_icon="⚡", layout="wide")

# Init Session State
if "units" not in st.session_state: st.session_state.units = 20
if "current_user" not in st.session_state: st.session_state.current_user = None
if "gallery" not in st.session_state: st.session_state.gallery = []

# --- 2. THE ULTIMATE CYBER DESIGN ---
def apply_neon_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        .stApp {
            background: radial-gradient(circle at 50% 50%, #0d0d1a 0%, #050505 100%) !important;
            color: #e0e0e0 !important;
        }

        /* Glassmorphism Containers */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(0, 210, 255, 0.2) !important;
            padding: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8) !important;
        }

        /* Neon Title */
        .logo-text {
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem !important;
            background: linear-gradient(90deg, #00d2ff, #9d50bb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.5));
            letter-spacing: 8px;
        }

        /* Animated Buttons */
        .stButton > button {
            width: 100%;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5) !important;
            border: none !important;
            color: white !important;
            font-weight: 900 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 20px #00d2ff !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_neon_theme()

# --- 3. UI - HEADER ---
st.markdown('<h1 class="logo-text">MAXIMUSIKAI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.6;'>POWERED BY NEURAL ENGINE 2026</p>", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚡ STUDIO CORE")
    artist_id = st.text_input("ARTIST ID", placeholder="Ditt namn...")
    if st.button("LOGIN"):
        db = load_user_db()
        if artist_id not in db:
            db[artist_id] = {"units": 20, "gallery": []}
            save_user_db(db)
        user = db[artist_id]
        st.session_state.current_user = artist_id
        st.session_state.units = user["units"]
        st.session_state.gallery = user["gallery"]
        st.success(f"Välkommen, {artist_id}!")

    st.divider()
    st.metric("ENERGY UNITS", f"{st.session_state.units} ⚡")

# --- 5. TABS LOGIC ---
tab_magi, tab_regi, tab_arkiv = st.tabs(["🪄 MAGI (IMAGE)", "🎬 REGI (VIDEO)", "📚 ARKIV"])

with tab_magi:
    col1, col2 = st.columns([2, 1])
    with col1:
        prompt = st.text_area("PROMPT ENGINE", placeholder="Beskriv din vision...")
    with col2:
        style = st.selectbox("STIL", ["Photorealistic", "Cyberpunk", "Anime", "Oil Painting"])
        if st.button("GENERATE IMAGE (2 ⚡)"):
            if st.session_state.units >= 2:
                with st.spinner("Vibrerar molekyler..."):
                    time.sleep(2) # Simulering
                    img_url = f"https://picsum.photos{time.time()}/800/600"
                    st.session_state.units -= 2
                    new_item = {"url": img_url, "prompt": prompt}
                    st.session_state.gallery.append(new_item)
                    update_user(st.session_state.current_user, {
                        "units": st.session_state.units,
                        "gallery": st.session_state.gallery
                    })
                    st.image(img_url, use_container_width=True)
            else:
                st.error("Slut på energi!")

with tab_regi:
    st.info("Luma Dream Machine API integreras här...")
    if not st.session_state.gallery:
        st.warning("Skapa en bild i MAGI först för att rendera video.")
    else:
        selected_img = st.selectbox("Välj bild som bas:", [i["prompt"][:30] for i in st.session_state.gallery])
        st.button("RENDER MOTION (5 ⚡)")

with tab_arkiv:
    if st.session_state.gallery:
        cols = st.columns(3)
        for idx, item in enumerate(reversed(st.session_state.gallery)):
            with cols[idx % 3]:
                st.image(item["url"])
                st.caption(item["prompt"])
    else:
        st.write("Ditt arkiv är tomt.")
