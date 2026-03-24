import streamlit as st
import replicate
import os
import datetime
import pandas as pd
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from st_supabase_connection import SupabaseConnection

# --- 1. KONFIGURATION & ANSLUTNING ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO 2026", page_icon="⚡", layout="wide")

# Kontrollera Secrets (Viktigt!)
if "connections" not in st.secrets or "supabase" not in st.secrets["connections"]:
    st.error("❌ SUPABASE-INSTÄLLNINGAR SAKNAS! Gå till Settings -> Secrets i Streamlit Cloud.")
    st.info("Klistra in: [connections.supabase] \n url = 'DIN_URL' \n key = 'jgvyqwvcwjjxlnsywqho'")
    st.stop()

# Anslut till Supabase
conn = st.connection("supabase", type=SupabaseConnection)

# --- 2. DATABAS-FUNKTIONER ---
def get_user_data(artist_id):
    try:
        res = conn.table("users").select("*").eq("artist", artist_id).execute()
        return res.data[0] if res.data else None
    except: return None

def update_user_data(user_data):
    conn.table("users").upsert(user_data).execute()

def get_gallery_data():
    res = conn.table("gallery").select("*").order("id", desc=True).limit(20).execute()
    return res.data if res.data else []

def save_to_gallery(entry):
    conn.table("gallery").insert(entry).execute()

# --- 3. DESIGN (CYBERPUNK) ---
main_color = "#bf00ff"
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 20px; border-radius: 15px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 20px; }}
    .neon-title {{ font-family: 'Arial Black'; font-size: 45px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .share-btn {{ background: {main_color}22; border: 1px solid {main_color}; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; font-size: 11px; margin-right: 5px; }}
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; border-radius: 8px; font-weight: bold; width: 100%; }}
    .stButton>button:hover {{ background: {main_color}; color: black; box-shadow: 0 0 20px {main_color}; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY ---
with st.sidebar:
    st.markdown(f'<h2 style="color:{main_color};">MAXIMUSIKAI</h2>', unsafe_allow_html=True)
    artist_id = st.text_input("DITT ARTIST-ID:", "ANONYM").strip().upper()
    
    # Hämta/Skapa användare
    user = get_user_data(artist_id)
    if not user:
        user = {"artist": artist_id, "is_pro": False, "credits": 3}
        update_user_data(user)

    is_admin = (artist_id == "TOMAS2026")
    status = "💎 PRO" if user["is_pro"] else f"⚡ {user['credits']} CREDITS"
    st.info(f"STATUS: {status}")
    
    if not user["is_pro"]:
        with st.expander("UPPGRADERA"):
            if st.button("LÅS UPP PRO (KOD)"):
                if st.text_input("KOD:", type="password") == "PRO2026":
                    user["is_pro"] = True
                    update_user_data(user); st.rerun()

    mood = st.selectbox("STIL:", ["Cyberpunk", "80s Retro", "Dark Techno", "Cinematic"])
    st.caption("v6.0 // BAKNINGS-EDITION 🥐")

# --- 5. SOCIAL DELNING ---
def share_ui(name, url):
    text = f"Kolla min AI-konst: {name} #MAXIMUSIKAI"
    tweet = f"https://twitter.com{urllib.parse.quote(text)}&url={urllib.parse.quote(url)}"
    st.markdown(f'<a class="share-btn" href="{tweet}" target="_blank">𝕏 DELA PÅ X</a>', unsafe_allow_html=True)

# --- 6. HUVUDAPP ---
st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

replicate_token = st.secrets.get("REPLICATE_API_TOKEN")
if replicate_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_token
    tabs = st.tabs(["🪄 SKAPA", "📚 ARKIV", "🌐 FEED"])

    with tabs[0]: # SKAPA
        col1, col2 = st.columns([1, 1])
        with col1:
            prompt = st.text_area("VAD SKALL VI BYGGA?", placeholder="En rymdstation i neon...")
            if st.button("STARTA MAGIN"):
                if user["credits"] > 0 or user["is_pro"]:
                    with st.status("AI:N BAKAR DIN IDÉ... 🥐"):
                        if not user["is_pro"]:
                            user["credits"] -= 1
                            update_user_data(user)
                        
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{prompt}, {mood} style"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music for {prompt}", "duration": 8})
                            img_url = img_f.result()
                            mu_url = mu_f.result()

                        save_to_gallery({
                            "artist": artist_id,
                            "name": prompt[:20] if prompt else "Untitled",
                            "video": str(img_url[0] if isinstance(img_url, list) else img_url),
                            "audio": str(mu_url)
                        })
                        st.rerun()

    with tabs[1]: # ARKIV
        files = [p for p in get_gallery_data() if p["artist"] == artist_id or is_admin]
        for item in files:
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])
                share_ui(item['name'], item['video'])

    with tabs[2]: # FEED
        for item in get_gallery_data():
            c1, c2 = st.columns([1, 2])
            with c1: st.image(item['video'])
            with c2:
                st.write(f"**{item['name']}** - *{item['artist']}*")
                if item.get('audio'): st.audio(item['audio'])
                share_ui(item['name'], item['video'])
            st.divider()
else:
    st.error("REPLICATE_API_TOKEN saknas i Secrets!")













