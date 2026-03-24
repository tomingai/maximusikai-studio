import streamlit as st
import replicate
import os
import datetime
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & CORE ENGINE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Konfiguration
STRIPE_PRO = "https://buy.stripe.com" 
DB_FILE = "maximusikai_archive.json"
USERS_FILE = "maximusikai_users.json"
ADMIN_KEY = "TOMAS2026"

def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return default
    return default

def save_data(data, file):
    with open(file, "w") as f: json.dump(data, f)

# Session State
if "gallery" not in st.session_state: st.session_state.gallery = load_data(DB_FILE, [])
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"

# --- 2. DEN RENODLADE DESIGN-MOTORN ---
main_color = st.session_state.theme_color
st.markdown(f"""
    <style>
    .stApp, [data-testid="stSidebar"] {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    [data-testid="stSidebar"] .stMarkdown h3, [data-testid="stSidebar"] label p {{ color: {main_color} !important; font-weight: 900 !important; font-size: 14px !important; text-transform: uppercase; }}
    
    /* Neon Header */
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 30px; border-radius: 20px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 25px; box-shadow: 0 0 30px {main_color}11; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: 55px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; letter-spacing: -2px; }}
    
    /* Clean Tabs */
    div[data-baseweb="tab-list"] {{ background: transparent !important; border-bottom: 1px solid #222 !important; }}
    button[data-baseweb="tab"] div p {{ font-size: 16px !important; font-weight: 900 !important; }}
    
    /* Status Line (Credits) */
    .status-line {{ font-size: 10px; letter-spacing: 2px; color: {main_color}; border-top: 1px solid {main_color}44; padding-top: 5px; margin-top: 5px; text-transform: uppercase; }}
    
    /* Buttons */
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; border-radius: 5px; font-weight: bold; text-transform: uppercase; transition: 0.3s; }}
    .stButton>button:hover {{ background: {main_color}; color: #000; box-shadow: 0 0 20px {main_color}; }}
    
    /* Stripe Link */
    .stripe-link {{ color: {main_color}; text-decoration: none; font-size: 12px; font-weight: bold; border: 1px solid {main_color}44; padding: 8px; border-radius: 5px; display: block; text-align: center; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY (MINIMALISTISK) ---
with st.sidebar:
    st.markdown(f'<p style="color:{main_color}; font-weight:900; letter-spacing:2px;">MAXIMUSIKAI ENGINE</p>', unsafe_allow_html=True)
    
    artist_name = st.text_input("ARTIST ID:", "ANONYM")
    
    # User Logic
    user_db = load_data(USERS_FILE, [])
    current_user = next((u for u in user_db if u["artist"] == artist_name), None)
    if not current_user:
        current_user = {"artist": artist_name, "is_pro": False, "credits": 3}
        user_db.append(current_user)
        save_data(user_db, USERS_FILE)

    # Clean Credit/Pro display
    status_txt = "PREMIUM ACCESS" if current_user["is_pro"] else f"POWER: {current_user['credits']} units"
    st.markdown(f'<div class="status-line">{status_txt}</div>', unsafe_allow_html=True)

    st.divider()
    
    # Store (Hidden in expander to save space)
    if not current_user["is_pro"]:
        with st.expander("⚡ UPGRADE"):
            st.markdown(f'<a href="{STRIPE_PRO}" class="stripe-link">UNLOCK PRO</a>', unsafe_allow_html=True)
            code = st.text_input("ENTER KEY:", type="password")
            if st.button("ACTIVATE"):
                if code == "PRO2026": current_user["is_pro"] = True
                save_data(user_db, USERS_FILE); st.rerun()

    mood = st.selectbox("STYLE:", ["Cyberpunk", "Retro VHS", "Lo-fi", "Dark Techno", "Epic Cinematic"])
    music_duration = st.slider("LENGTH:", 10, 240 if current_user["is_pro"] else 11, 10)
    
    st.caption(f"VER 4.5.0 // T. INGVARSSON")

# --- 4. HUVUDAPPEN ---
st.markdown(f"""<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>""", unsafe_allow_html=True)

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    is_admin = (artist_name == ADMIN_KEY)
    
    tabs = st.tabs(["🪄 MAGIC", "📚 ARCHIVE", "⚙️ COMMAND"] if is_admin else ["🪄 MAGIC", "📚 ARCHIVE"])

    with tabs[0]: # MAGIC
        if not current_user["is_pro"] and current_user["credits"] <= 0:
            st.error("OUT OF POWER. PLEASE UPGRADE.")
        else:
            m_ide = st.text_area("DESCRIBE YOUR VISION:", value=f"A {mood} masterpiece")
            if st.button("EXECUTE"):
                with st.status("GENERATING..."):
                    try:
                        if not current_user["is_pro"]: current_user["credits"] -= 1
                        save_data(user_db, USERS_FILE)
                        
                        img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                        entry = {"id": datetime.datetime.now().timestamp(), "artist": artist_name, "name": m_ide[:20], "video": str(img)}
                        st.session_state.gallery.append(entry); save_data(st.session_state.gallery, DB_FILE)
                        st.rerun()
                    except Exception as e: st.error(f"ENGINE ERROR: {e}")

    with tabs[1]: # ARCHIVE
        my_files = [p for p in st.session_state.gallery if p.get("artist") == artist_name or is_admin]
        if not my_files: st.info("ARCHIVE EMPTY.")
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.video(item['video'])

    if is_admin:
        with tabs[2]: # ADMIN COMMAND
            st.markdown(f'<h3 style="color:{main_color}">SYSTEM COMMAND</h3>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write("**USER BASE**")
                st.dataframe(pd.DataFrame(user_db), use_container_width=True)
            with col2:
                target = st.selectbox("SELECT USER:", [u["artist"] for u in user_db])
                if st.button(f"GRANT +10 CREDITS TO {target}"):
                    for u in user_db:
                        if u["artist"] == target: u["credits"] += 10
                    save_data(user_db, USERS_FILE); st.rerun()

else: st.error("API TOKEN MISSING")














