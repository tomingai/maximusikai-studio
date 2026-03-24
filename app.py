import streamlit as st
import replicate
import os
import datetime
import json
import zipfile
import io
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & CORE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

STRIPE_PRO = "https://buy.stripe.com" 
DB_FILE = "maximusikai_archive.json"
USERS_FILE = "maximusikai_users.json"
SYSTEM_FILE = "maximusikai_system.json"
ADMIN_KEY = "TOMAS2026"

def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return default
    return default

def save_data(data, file):
    with open(file, "w") as f: json.dump(data, f)

if "gallery" not in st.session_state: st.session_state.gallery = load_data(DB_FILE, [])
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

# --- 2. DESIGN (DEN RENODLADE GRUNDEN) ---
main_color = st.session_state.theme_color
st.markdown(f"""
    <style>
    .stApp, [data-testid="stSidebar"] {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 25px; border-radius: 20px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 25px; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: 50px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    div[data-baseweb="tab-list"] {{ background: transparent !important; border-bottom: 1px solid #222 !important; }}
    button[data-baseweb="tab"] div p {{ font-size: 14px !important; font-weight: 900 !important; text-transform: uppercase; }}
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; border-radius: 5px; font-weight: bold; text-transform: uppercase; }}
    .stButton>button:hover {{ background: {main_color}; color: #000; box-shadow: 0 0 20px {main_color}; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY (USER & STATUS) ---
with st.sidebar:
    st.markdown(f'<p style="color:{main_color}; font-weight:900; letter-spacing:2px;">MAXIMUSIKAI STUDIO</p>', unsafe_allow_html=True)
    artist_name = st.text_input("ARTIST ID:", "ANONYM")
    
    user_db = load_data(USERS_FILE, [])
    current_user = next((u for u in user_db if u["artist"] == artist_name), None)
    if not current_user:
        current_user = {"artist": artist_name, "is_pro": False, "credits": 3}
        user_db.append(current_user); save_data(user_db, USERS_FILE)

    status_txt = "PREMIUM ACCESS 💎" if current_user["is_pro"] else f"POWER: {current_user['credits']} units ⚡"
    st.markdown(f'<div style="font-size:10px; color:{main_color}; border-top:1px solid #333; padding-top:5px;">{status_txt}</div>', unsafe_allow_html=True)
    
    if not current_user["is_pro"]:
        with st.expander("⚡ UPGRADE"):
            st.markdown(f'[ACTIVATE PRO SUBSCRIPTION]({STRIPE_PRO})')
            if st.button("USE MASTER KEY"):
                if st.text_input("KEY:", type="password") == "PRO2026": 
                    current_user["is_pro"] = True; save_data(user_db, USERS_FILE); st.rerun()

    st.divider()
    mood = st.selectbox("MOOD:", ["Cyberpunk", "Retro VHS", "Lo-fi", "Dark Techno", "Epic Cinematic"])
    music_duration = st.slider("LENGTH:", 10, 240 if current_user["is_pro"] else 11, 10)
    st.caption("v4.6.0 // T. INGVARSSON")

# --- 4. HUVUDAPPEN (ALLA FLIKAR ÅTERSTÄLLDA) ---
st.markdown(f"""<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>""", unsafe_allow_html=True)

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    is_admin = (artist_name == ADMIN_KEY)
    
    # Här är din kompletta lista med flikar
    tab_labels = ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"]
    if is_admin: tab_labels.append("⚙️ ADMIN")
    
    tabs = st.tabs(tab_labels)

    with tabs[0]: # --- TOTAL MAGI ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt if st.session_state.remix_prompt else f"A {mood} scene")
            if st.button("STARTA"):
                if current_user["credits"] > 0 or current_user["is_pro"]:
                    with st.status("BUILDING..."):
                        if not current_user["is_pro"]: current_user["credits"] -= 1
                        save_data(user_db, USERS_FILE)
                        img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                        mu = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood} music", "duration": 8})
                        entry = {"id": datetime.datetime.now().timestamp(), "artist": artist_name, "name": m_ide[:15], "video": str(img), "audio": str(mu)}
                        st.session_state.gallery.append(entry); save_data(st.session_state.gallery, DB_FILE); st.rerun()

    with tabs[1]: # --- REGISSÖREN ---
        up_file = st.file_uploader("ANIMERA BILD:", type=["jpg", "png"])
        if up_file and st.button("KÖR ANIMATION"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic zoom", "image_url": up_file})
            st.video(str(res))

    with tabs[2]: # --- BARA MUSIK ---
        mu_prompt = st.text_input("BESKRIV BEATET:", f"{mood} vibes")
        if st.button("SKAPA LJUD"):
            mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_prompt, "duration": 10})
            st.audio(str(mu_res))

    with tabs[3]: # --- ARKIV ---
        my_files = [p for p in st.session_state.gallery if p.get("artist") == artist_name or is_admin]
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.video(item['video'])
                if "audio" in item: st.audio(item['audio'])
                if st.button("REMIX", key=f"rem_{item['id']}"):
                    st.session_state.remix_prompt = item['name']; st.rerun()

    with tabs[4]: # --- COMMUNITY FEED ---
        st.caption("Senaste skapelserna från alla artister")
        for item in reversed(st.session_state.gallery[-5:]):
            st.video(item['video']); st.caption(f"Artist: {item.get('artist', 'Okänd')}")

    if is_admin:
        with tabs[5]: # --- ADMIN COMMAND ---
            st.subheader("SYSTEM OVERVIEW")
            st.write(f"Användare: {len(user_db)}")
            st.dataframe(pd.DataFrame(user_db))
            if st.button("EXPORT ALL DATA"):
                save_data(st.session_state.gallery, "backup.json")
                st.success("Backup sparad.")

else: st.error("API TOKEN SAKNAS")













