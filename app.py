import streamlit as st
import replicate
import os
import datetime
import json
import zipfile
import io
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

STRIPE_SUBSCRIPTION = "https://buy.stripe.com" 
STRIPE_CREDITS = "https://buy.stripe.com" 

DB_FILE = "maximusikai_archive.json"
SYSTEM_FILE = "maximusikai_system.json"
USERS_FILE = "maximusikai_users.json"
ADMIN_KEY = "TOMAS2026"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return [] if "users" in file else {"broadcast": "", "maintenance": False, "total_cost": 0.0}
    return [] if "users" in file else {"broadcast": "", "maintenance": False, "total_cost": 0.0}

def save_data(data, file):
    with open(file, "w") as f: json.dump(data, f)

# --- 2. SESSION STATE & USER LOGIC ---
if "gallery" not in st.session_state: st.session_state.gallery = load_data(DB_FILE)
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"

# --- 3. DESIGN ---
main_color = st.session_state.theme_color
st.markdown(f"""
    <style>
    .stApp, [data-testid="stSidebar"] {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.85); padding: 20px; border-radius: 20px; border: 1px solid {main_color}66; text-align: center; margin-bottom: 20px; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: 45px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .stButton>button {{ background: {main_color}1a; color: {main_color}; border: 1px solid {main_color}; border-radius: 10px; font-weight: bold; width: 100%; }}
    .credit-badge {{ background: #00ffcc; color: black; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: 900; }}
    .admin-card {{ background: rgba(255, 75, 75, 0.05); border: 2px solid #ff4b4b; padding: 20px; border-radius: 15px; margin-bottom: 20px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY (COMMERCIAL ENGINE) ---
with st.sidebar:
    st.markdown(f"""<div style="border: 1px solid {main_color}; padding: 10px; border-radius: 10px; text-align: center;"><p style="color:{main_color}; font-weight:900; margin:0; font-size:12px;">MAXIMUSIKAI ENGINE ONLINE</p></div>""", unsafe_allow_html=True)
    
    artist_name = st.text_input("👤 ARTIST:", "ANONYM")
    
    # Hämta användardata
    user_db = load_data(USERS_FILE)
    current_user = next((u for u in user_db if u["artist"] == artist_name), None)
    
    if not current_user:
        # Registrera ny gratisanvändare
        current_user = {"artist": artist_name, "is_pro": False, "credits": 3}
        user_db.append(current_user)
        save_data(user_db, USERS_FILE)

    # Visa status
    status_label = "PRO MEMBER 💎" if current_user["is_pro"] else f"KREDITER: {current_user['credits']} ⚡"
    st.markdown(f'<div style="text-align:center; margin-bottom:10px;"><span class="credit-badge">{status_label}</span></div>', unsafe_allow_html=True)

    # Köp-knappar
    if not current_user["is_pro"]:
        with st.expander("⭐ UPPGRADERA"):
            st.markdown(f'[Månadsabonnemang (Obegränsat)]({STRIPE_SUBSCRIPTION})')
            st.markdown(f'[Köp 10 extra krediter]({STRIPE_CREDITS})')
            license_key = st.text_input("AKTIVERINGSKOD:", type="password")
            if st.button("AKTIVERA"):
                if license_key == "PRO2026": 
                    current_user["is_pro"] = True
                    st.success("PRO AKTIVERAT!")
                elif license_key == "TOPUP":
                    current_user["credits"] += 10
                    st.success("+10 KREDITER!")
                save_data(user_db, USERS_FILE)
                st.rerun()

    theme_options = {"Neon Purple": "#bf00ff", "Cyber Amber": "#ffaa00", "Electric Blue": "#00f2ff"}
    st.session_state.theme_color = theme_options[st.selectbox("THEME:", list(theme_options.keys()))]
    
    mood = st.selectbox("STYLE:", ["Cyberpunk", "Retro VHS", "Lo-fi", "Dark Techno", "Epic Cinematic"])
    music_duration = st.slider("DURATION:", 10, 240 if current_user["is_pro"] else 11, 10)
    st.caption("v4.4.0 // TOMAS INGVARSSON")

# --- GLOBAL SYSTEM ---
sys_data = load_data(SYSTEM_FILE)
is_admin = artist_name == ADMIN_KEY
st.markdown(f"""<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>""", unsafe_allow_html=True)

# --- 5. HUVUDAPPEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    tabs = st.tabs(["🪄 MAGI", "📚 ARKIV", "🛠️ ADMIN"] if is_admin else ["🪄 MAGI", "📚 ARKIV"])

    with tabs[0]: # MAGI
        can_create = current_user["is_pro"] or current_user["credits"] > 0
        if not can_create:
            st.warning("Slut på krediter! Uppgradera för att fortsätta skapa.")
        else:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=f"A {mood} scene")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("BUILDING..."):
                    try:
                        # Dra kredit om inte PRO
                        if not current_user["is_pro"]:
                            current_user["credits"] -= 1
                            save_data(user_db, USERS_FILE)
                        
                        img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                        entry = {"id": time.time(), "artist": artist_name, "name": m_ide[:15], "video": str(img), "time": datetime.datetime.now().strftime("%H:%M")}
                        st.session_state.gallery.append(entry); save_data(st.session_state.gallery, DB_FILE)
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    with tabs[1]: # ARKIV
        user_gallery = [p for p in st.session_state.gallery if p.get("artist") == artist_name or is_admin]
        for item in reversed(user_gallery):
            with st.expander(f"📁 {item['name']} ({item['artist']})"):
                st.video(item['video'])

    if is_admin:
        with tabs[2]: # ADMIN MASTER
            st.markdown('<h1 style="color:#ff4b4b;">🛠️ TOMAS COMMAND CENTER</h1>', unsafe_allow_html=True)
            st.markdown('<div class="admin-card">', unsafe_allow_html=True)
            st.subheader("👥 USER & CREDIT MANAGEMENT")
            
            # Tabell över användare
            df_users = pd.DataFrame(user_db)
            st.dataframe(df_users)
            
            # Ge krediter manuellt
            target_user = st.selectbox("Välj användare:", [u["artist"] for u in user_db])
            amount = st.number_input("Antal krediter att ge:", 1, 100, 10)
            if st.button(f"Ge {amount} krediter till {target_user}"):
                for u in user_db:
                    if u["artist"] == target_user:
                        u["credits"] += amount
                        save_data(user_db, USERS_FILE)
                        st.success("Klart!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("REPLICATE_API_TOKEN MISSING")
















