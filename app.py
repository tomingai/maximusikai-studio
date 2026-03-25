import streamlit as st
import replicate
import os
import datetime
import time

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg_url" not in st.session_state: st.session_state.app_bg_url = None
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

# --- 2. DYNAMISK DESIGN (BAKGRUNDSKONTROLL) ---
with st.sidebar:
    st.markdown("### 🎨 STUDIO DESIGN")
    preset = st.selectbox("STIL:", ["Mörk", "Ljus", "Neon"])
    bg_color = "#050505" if preset == "Mörk" else "#ffffff" if preset == "Ljus" else "#0b001a"
    neon_color = st.color_picker("NEON-FÄRG", "#bf00ff")
    
    if st.button("ÅTERSTÄLL TILL FÄRG"):
        st.session_state.app_bg_url = None
        st.rerun()

# CSS för bakgrund (Bild eller Färg)
bg_style = ""
if st.session_state.app_bg_url:
    bg_style = f"""
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{st.session_state.app_bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    """
else:
    bg_style = f".stApp {{ background-color: {bg_color} !important; }}"

st.markdown(f"""
    <style>
    {bg_style}
    [data-testid="stSidebar"] {{ background-color: rgba(10,10,10,0.8) !important; border-right: 1px solid {neon_color}44; }}
    .neon-container {{ 
        background: rgba(0,0,0,0.5); backdrop-filter: blur(15px); padding: 25px; 
        border-radius: 20px; border: 2px solid {neon_color}; 
        text-align: center; margin-bottom: 25px; 
    }}
    .neon-title {{ font-family: 'Arial Black'; font-size: 50px; font-weight: 900; color: white; text-shadow: 2px 2px 15px {neon_color}; margin: 0; }}
    .stButton>button {{ background: rgba(255,255,255,0.1); color: {neon_color}; border: 2px solid {neon_color}; border-radius: 12px; font-weight: bold; width: 100%; }}
    .stButton>button:hover {{ background: {neon_color}; color: white; box-shadow: 0 0 20px {neon_color}; }}
    label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY (ANVÄNDARE) ---
with st.sidebar:
    st.divider()
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: 
        st.session_state.user_db[artist_id] = {"credits": 10, "is_pro": False}
    
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    # Fixad status-text utan f-string krasch
    if is_admin:
        status_txt = "💎 ADMIN ACCESS"
    elif user_info.get("is_pro"):
        status_txt = "💎 PRO ACCOUNT"
    else:
        status_txt = f"⚡ {user_info.get('credits')} UNITS"
        
    st.info(f"STATUS: {status_txt}")
    mood = st.selectbox("AI MOOD:", ["Cinematic", "Epic Detail", "Surreal", "Vibrant", "Minimalist"])

# --- 4. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    # HÄR ÄR DINA FLIKAR TILLBAKA!
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"])

    with tabs[0]: # --- MAGI ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt)
            if st.button("STARTA GENERERING"):
                if user_info["credits"] > 0 or is_admin:
                    with st.status("AI SKAPAR..."):
                        if not is_admin: user_info["credits"] -= 1
                        img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style, 4k"})
                        mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood} music", "duration": 8})
                        
                        img_url = img_res if isinstance(img_res, list) else img_res
                        st.session_state.gallery.append({
                            "id": datetime.datetime.now().timestamp(), 
                            "artist": artist_id, "name": m_ide[:20] or "Vision", 
                            "video": str(img_url), "audio": str(mu_res)
                        })
                        st.rerun()

    with tabs[1]: # --- REGI ---
        st.subheader("ANIMERA BILDER")
        up_file = st.file_uploader("Ladda upp bild för Luma:", type=["jpg", "png"])
        if up_file and st.button("KÖR LUMA DREAM"):
            with st.spinner("Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up_file})
                st.video(str(res))

    with tabs[2]: # --- MUSIK ---
        mu_p = st.text_input("BESKRIV ENDAST LJUD:", f"{mood} beats")
        if st.button("GENERERA LJUD"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 15})
                st.audio(str(mu_res))

    with tabs[3]: # --- ARKIV ---
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_files: st.info("Ditt arkiv är tomt.")
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if st.button("🖼 SÄTT SOM BAKGRUND", key=f"bg_{item['id']}"):
                    st.session_state.app_bg_url = item['video']
                    st.rerun()
                if item.get('audio'): st.audio(item['audio'])

    with tabs[4]: # --- FEED ---
        for item in reversed(st.session_state.gallery[-10:]):
            st.image(item['video'], caption=f"Av: {item['artist']}")
            if st.button("🖼 ANVÄND BAKGRUND", key=f"feed_bg_{item['id']}"):
                st.session_state.app_bg_url = item['video']
                st.rerun()
            st.divider()
else:
    st.error("API-nyckel saknas i Secrets!")

















