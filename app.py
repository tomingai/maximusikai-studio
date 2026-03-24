import streamlit as st
import replicate
import os
import datetime
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & MINNE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

# --- 2. LJUS DESIGN (CLEAN & MODERN) ---
main_color = "#bf00ff" # Vi behåller din lila signaturfärg
st.markdown(f"""
    <style>
    /* Ljus bakgrund med mjuk gradient */
    .stApp {{ 
        background: linear-gradient(135deg, #ffffff 0%, #f0f2f6 100%) !important; 
        color: #1a1a1a !important; 
    }}
    
    /* Sidomenyn görs ljusgrå */
    [data-testid="stSidebar"] {{ 
        background-color: #f8f9fa !important; 
        border-right: 1px solid #e0e0e0;
    }}

    /* Neon-containern i ljust utförande */
    .neon-container {{ 
        background: white; 
        padding: 25px; 
        border-radius: 20px; 
        border: 1px solid {main_color}33; 
        box-shadow: 0 10px 30px rgba(191, 0, 255, 0.1);
        text-align: center; 
        margin-bottom: 25px; 
    }}
    
    .neon-title {{ 
        font-family: 'Arial Black'; 
        font-size: 50px; 
        font-weight: 900; 
        color: #1a1a1a; 
        text-shadow: 2px 2px 0px {main_color}22; 
        margin: 0; 
    }}

    /* Knappar i ljust läge */
    .stButton>button {{ 
        background: white; 
        color: {main_color}; 
        border: 2px solid {main_color}; 
        border-radius: 12px; 
        font-weight: bold; 
        width: 100%; 
        transition: 0.3s; 
    }}
    .stButton>button:hover {{ 
        background: {main_color}; 
        color: white; 
        box-shadow: 0 5px 15px {main_color}44; 
    }}

    /* Texter och labels */
    label, p, span, h1, h2, h3 {{ color: #1a1a1a !important; }}
    .stTextArea textarea {{ background-color: white !important; color: #1a1a1a !important; border: 1px solid #ccc !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown(f'<h2 style="color:{main_color};">MAXIMUSIKAI</h2>', unsafe_allow_html=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = {"credits": 3, "is_pro": False}
    
    current_user = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    status_txt = "💎 PREMIUM" if (current_user["is_pro"] or is_admin) else f"⚡ {current_user['credits']} UNITS"
    st.success(f"STATUS: {status_txt}")
    
    mood = st.selectbox("MOOD:", ["Bright Pop", "Minimalist White", "Clean Tech", "Nature Soft", "High-Key Photo"])
    st.caption("v6.6 // LIGHT EDITION 🥐")

# --- 4. HUVUDAPPEN ---
st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

token = st.secrets.get("REPLICATE_API_TOKEN")

if not token:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
else:
    os.environ["REPLICATE_API_TOKEN"] = token
    
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"])

    with tabs[0]: # --- 🪄 MAGI ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt, placeholder="En ljus och luftig vision...")
            if st.button("STARTA GENERERING"):
                if current_user["credits"] > 0 or current_user["is_pro"] or is_admin:
                    with st.status("MAGI PÅGÅR..."):
                        if not (current_user["is_pro"] or is_admin): current_user["credits"] -= 1
                        
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style, bright lighting, high quality"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music for {m_ide}", "duration": 8})
                            img_res, mu_res = img_f.result(), mu_f.result()

                        img_url = img_res if isinstance(img_res, list) else img_res
                        entry = {"id": datetime.datetime.now().timestamp(), "artist": artist_id, "name": m_ide[:20], "video": str(img_url), "audio": str(mu_res)}
                        st.session_state.gallery.append(entry)
                        st.rerun()

    with tabs[1]: # --- 🎬 REGI ---
        up_file = st.file_uploader("Ladda upp bild för animation:", type=["jpg", "png"])
        if up_file and st.button("KÖR ANIMERING"):
            with st.spinner("Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up_file})
                st.video(str(res))

    with tabs[2]: # --- 🎧 MUSIK ---
        mu_p = st.text_input("BESKRIV LJUDET:", f"{mood} beats")
        if st.button("GENERERA LJUD"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 15})
                st.audio(str(mu_res))

    with tabs[3]: # --- 📚 ARKIV ---
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_files: st.write("Ditt arkiv är tomt.")
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper() or 'UNNAMED'}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])
                if st.button("REMIX", key=f"rem_{item['id']}"):
                    st.session_state.remix_prompt = item['name']; st.rerun()

    with tabs[4]: # --- 🌐 FEED ---
        for item in reversed(st.session_state.gallery[-10:]):
            c1, c2 = st.columns([1, 1.5])
            with c1: st.image(item['video'])
            with c2: 
                st.write(f"**{item['name']}**")
                st.caption(f"Artist: {item['artist']}")
                if item.get('audio'): st.audio(item['audio'])
            st.divider()















