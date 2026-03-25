import streamlit as st
import replicate
import os
import datetime
import requests
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Initiera lokalt minne (Session State)
if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

# --- 2. DYNAMISK DESIGN (REGLERBAR) ---
with st.sidebar:
    st.markdown("### 🎨 STUDIO DESIGN")
    bg_color = st.color_picker("BAKGRUNDSFÄRG", "#ffffff")
    neon_color = st.color_picker("NEON / DETALJER", "#bf00ff")
    
    # Smart textfärg (svart eller vit baserat på bakgrund)
    def get_text_color(hex_color):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        return "#000000" if brightness > 128 else "#ffffff"

    text_color = get_text_color(bg_color)

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_color} !important; border-right: 1px solid {neon_color}44; }}
    .neon-container {{ 
        background: {bg_color}; padding: 25px; border-radius: 20px; 
        border: 2px solid {neon_color}; box-shadow: 0 10px 30px {neon_color}33;
        text-align: center; margin-bottom: 25px; 
    }}
    .neon-title {{ 
        font-family: 'Arial Black'; font-size: 50px; font-weight: 900; 
        color: {text_color}; text-shadow: 2px 2px 10px {neon_color}66; margin: 0; 
    }}
    .stButton>button {{ 
        background: transparent; color: {neon_color}; border: 2px solid {neon_color}; 
        border-radius: 12px; font-weight: bold; width: 100%; transition: 0.3s; 
    }}
    .stButton>button:hover {{ background: {neon_color}; color: {bg_color}; box-shadow: 0 5px 15px {neon_color}88; }}
    label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ color: {text_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY (ANVÄNDARE) ---
with st.sidebar:
    st.divider()
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    # Registrera användare i minnet
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = {"credits": 5, "is_pro": False}
    
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    status_msg = "💎 PRO ACCOUNT" if (user_info["is_pro"] or is_admin) else f"⚡ {user_info['credits']} UNITS"
    st.info(status_msg)
    mood = st.selectbox("MOOD:", ["Bright Pop", "Dark Techno", "Cinematic", "Cyberpunk", "Minimalist"])
    st.caption("v7.5 // ADMIN & BAKE 🥐")

# --- 4. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

token = st.secrets.get("REPLICATE_API_TOKEN")

if not token:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
else:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN" if is_admin else ""])

    with tabs[0]: # --- MAGI ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt)
            if st.button("STARTA GENERERING"):
                if user_info["credits"] > 0 or is_admin or user_info["is_pro"]:
                    with st.status("AI:N BAKAR... 🥐"):
                        if not (is_admin or user_info["is_pro"]): user_info["credits"] -= 1
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music", "duration": 8})
                            img_res, mu_res = img_f.result(), mu_f.result()

                        img_url = img_res if isinstance(img_res, list) else img_res
                        entry = {"id": datetime.datetime.now().timestamp(), "artist": artist_id, "name": m_ide[:20] or "Untitled", "video": str(img_url), "audio": str(mu_res)}
                        st.session_state.gallery.append(entry)
                        st.rerun()

    with tabs[1]: # --- REGI ---
        st.subheader("ANIMERA BILDER")
        up_file = st.file_uploader("Ladda upp bild:", type=["jpg", "png"])
        if up_file and st.button("ANIMERA"):
            with st.spinner("Luma arbetar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up_file})
                st.video(str(res))

    with tabs[2]: # --- MUSIK ---
        mu_p = st.text_input("BESKRIV LJUD:", f"{mood} beats")
        if st.button("SKAPA BEAT"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 15})
                st.audio(str(mu_res))

    with tabs[3]: # --- ARKIV ---
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])
                if st.button("REMIX", key=f"rem_{item['id']}"):
                    st.session_state.remix_prompt = item['name']; st.rerun()

    with tabs[4]: # --- FEED ---
        for item in reversed(st.session_state.gallery[-10:]):
            st.image(item['video'], caption=f"Artist: {item['artist']}")
            if item.get('audio'): st.audio(item['audio'])
            st.divider()

    if is_admin:
        with tabs[5]: # --- ADMIN ---
            st.markdown("### 🛠 ADMIN DASHBOARD")
            col_1, col_2 = st.columns(2)
            
            with col_1:
                st.subheader("👤 ANVÄNDARE")
                for u, data in st.session_state.user_db.items():
                    c_a, c_b = st.columns([2,1])
                    c_a.write(f"**{u}**: {data['credits']} pts | Pro: {data['is_pro']}")
                    if c_b.button("+10", key=f"add_{u}"):
                        data['credits'] += 10; st.rerun()

            with col_2:
                st.subheader("🗑 MODERERING")
                for i, item in enumerate(st.session_state.gallery):
                    if st.button(f"Radera: {item['name']} ({item['artist']})", key=f"del_{i}"):
                        st.session_state.gallery.pop(i); st.rerun()

            st.divider()
            # Backup
            gallery_json = json.dumps(st.session_state.gallery, indent=4)
            st.download_button("LADDA NER BACKUP (JSON)", gallery_json, "backup.json")














