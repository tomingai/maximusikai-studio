import streamlit as st
import replicate
import os
import datetime
import time
import json

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

# --- 2. BAKGRUNDS-PRESETS & DESIGN ---
with st.sidebar:
    st.markdown("### 🎨 STUDIO PRESETS")
    preset = st.selectbox("VÄLJ STIL:", ["Default Dark", "Cloud Studio (Ljus)", "Cyberpunk (Neon)", "Chocolate (Baking Mode)"])
    styles = {
        "Default Dark": {"bg": "#050505", "neon": "#bf00ff", "text": "#ffffff"},
        "Cloud Studio (Ljus)": {"bg": "#ffffff", "neon": "#007bff", "text": "#1a1a1a"},
        "Cyberpunk (Neon)": {"bg": "#0b001a", "neon": "#ff0055", "text": "#ffffff"},
        "Chocolate (Baking Mode)": {"bg": "#2d1b0d", "neon": "#e67e22", "text": "#fdf5e6"}
    }
    s = styles[preset]
    bg_color = st.color_picker("BAKGRUND", s["bg"])
    neon_color = st.color_picker("NEON", s["neon"])
    text_color = s["text"]

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_color} !important; border-right: 1px solid {neon_color}44; }}
    .neon-container {{ background: {bg_color}; padding: 25px; border-radius: 20px; border: 2px solid {neon_color}; box-shadow: 0 10px 40px {neon_color}22; text-align: center; margin-bottom: 25px; }}
    .neon-title {{ font-family: 'Arial Black'; font-size: 50px; font-weight: 900; color: {text_color}; text-shadow: 2px 2px 15px {neon_color}66; margin: 0; }}
    .stButton>button {{ background: transparent; color: {neon_color}; border: 2px solid {neon_color}; border-radius: 12px; font-weight: bold; width: 100%; transition: 0.3s; }}
    .stButton>button:hover {{ background: {neon_color}; color: {bg_color}; box-shadow: 0 0 25px {neon_color}; }}
    label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ color: {text_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY (USER) ---
with st.sidebar:
    st.divider()
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: 
        st.session_state.user_db[artist_id] = {"credits": 10, "is_pro": False}
    
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    # Status med säker stränghantering
    status_msg = "💎 PRO" if (user_info["is_pro"] or is_admin) else f"⚡ {user_info['credits']} UNITS"
    st.info(f"STATUS: {status_msg}")
    
    mood = st.selectbox("AI MOOD:", ["Cinematic", "Epic Detail", "Surreal", "Vibrant", "Minimalist"])

# --- 4. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN" if is_admin else " "])

    with tabs[0]: # MAGI
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt)
            use_canny = st.checkbox("Följ konturer från bild (ControlNet)")
            ref_img = st.file_uploader("Ladda upp bild/skiss:", type=["jpg", "png", "jpeg"]) if use_canny else None
            
            if st.button("STARTA GENERERING"):
                if user_info["credits"] > 0 or is_admin:
                    with st.status("MAGI PÅGÅR..."):
                        try:
                            if not is_admin: user_info["credits"] -= 1
                            
                            # STEG 1: SKAPA BILD
                            st.write("🎨 Skapar bild...")
                            if use_canny and ref_img:
                                img_res = replicate.run("lucataco/flux-canny:1134015699b8", input={"image": ref_img, "prompt": f"{m_ide}, {mood} style"})
                            else:
                                img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                            
                            # KORT PAUS FÖR ATT UNDVIKA 429
                            time.sleep(1.5)
                            
                            # STEG 2: SKAPA MUSIK
                            st.write("🎧 Komponerar musik...")
                            mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood} music for {m_ide}", "duration": 8})
                            
                            # SPARA
                            img_url = img_res if isinstance(img_res, list) else img_res
                            st.session_state.gallery.append({
                                "id": datetime.datetime.now().timestamp(), 
                                "artist": artist_id, 
                                "name": m_ide[:20], 
                                "video": str(img_url), 
                                "audio": str(mu_res)
                            })
                            st.success("KLART!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ett fel uppstod med Replicate: {e}")

    with tabs[1]: # REGI
        st.subheader("ANIMERA BILDER")
        luma_file = st.file_uploader("Ladda upp för Luma:", type=["jpg", "png"], key="l_up")
        if luma_file and st.button("KÖR LUMA"):
            with st.spinner("Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": luma_file})
                st.video(str(res))

    with tabs[3]: # ARKIV
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])

    with tabs[4]: # FEED
        for item in reversed(st.session_state.gallery[-10:]):
            st.image(item['video'], caption=f"Artist: {item['artist']}")
            st.divider()

else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
















