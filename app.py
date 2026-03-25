import streamlit as st
import replicate
import os
import datetime
import time
import json
import base64
import requests

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg_url" not in st.session_state: st.session_state.app_bg_url = None
if "bg_focus" not in st.session_state: st.session_state.bg_focus = "center"
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "start_btn": "STARTA GENERERING", "prompt_label": "VAD SKALL VI SKAPA?",
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SÄTT SOM BAKGRUND",
        "upload_label": "LADDA UPP EGEN BILD", "upload_btn": "SPARA I ARKIVET",
        "crop_label": "VÄLJ BILD-FOKUS (CROP):", "reset": "ÅTERSTÄLL DESIGN"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "start_btn": "START GENERATING", "prompt_label": "WHAT SHALL WE CREATE?",
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SET AS BACKGROUND",
        "upload_label": "UPLOAD OWN IMAGE", "upload_btn": "SAVE TO ARCHIVE",
        "crop_label": "SELECT IMAGE FOCUS (CROP):", "reset": "RESET DESIGN"
    }
}
L = texts[st.session_state.lang]

# --- 3. DYNAMISK DESIGN ---
with st.sidebar:
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    st.divider()
    bg_color = st.color_picker("BAKGRUNDSFÄRG", "#050505")
    neon_color = st.color_picker("NEON-FÄRG", "#bf00ff")
    st.session_state.bg_focus = st.selectbox(L["crop_label"], ["top", "center", "bottom"], index=1)
    if st.button(L["reset"]):
        st.session_state.app_bg_url = None
        st.rerun()

# SÄKER CSS FÖR BAKGRUND
bg_css = ""
if st.session_state.app_bg_url:
    img_data = st.session_state.app_bg_url
    if not isinstance(img_data, str):
        b64 = base64.b64encode(img_data.getvalue()).decode()
        img_data = f"data:image/png;base64,{b64}"
    
    bg_css = f"""
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{img_data}");
        background-size: cover; background-position: {st.session_state.bg_focus}; background-attachment: fixed;
    }}
    """
else:
    bg_css = f".stApp {{ background-color: {bg_color} !important; }}"

st.markdown(f"""
    <style>
    {bg_css}
    [data-testid="stSidebar"] {{ background-color: rgba(10,10,10,0.8) !important; border-right: 1px solid {neon_color}44; }}
    .neon-container {{ background: rgba(0,0,0,0.5); backdrop-filter: blur(15px); padding: 25px; border-radius: 20px; border: 2px solid {neon_color}; text-align: center; margin-bottom: 25px; }}
    .stButton>button {{ background: rgba(255,255,255,0.1); color: {neon_color}; border: 2px solid {neon_color}; border-radius: 12px; font-weight: bold; width: 100%; }}
    label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: bold !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY & ANVÄNDARE ---
with st.sidebar:
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = {"credits": 10, "is_pro": False}
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    u_creds = user_info.get("credits", 0)
    st.info(f"{L['status']}: {'💎 ADMIN' if is_admin else f'⚡ {u_creds} {L['units']}'}")

# --- 5. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><h1 style="color:white; font-family:Arial Black;">{L["title"]}</h1></div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN VILLKOR & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"], L["tab6"] if is_admin else " "])

    with tabs[0]: # MAGI
        m_ide = st.text_area(L["prompt_label"], value=st.session_state.remix_prompt)
        if st.button(L["start_btn"]):
            if user_info["credits"] > 0 or is_admin:
                with st.status("AI GENERERAR..."):
                    if not is_admin: user_info["credits"] -= 1
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, high quality"})
                    img_url = str(img[0]) if isinstance(img, list) else str(img)
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": m_ide[:15], "video": img_url})
                    st.rerun()

    with tabs[1]: # REGI
        up_v = st.file_uploader("Bild till Video:", type=["jpg", "png"], key="v_up")
        if up_v and st.button("KÖR LUMA"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": up_v})
            st.video(str(res))

    with tabs[2]: # MUSIK
        mu_p = st.text_input("Beat prompt:")
        if st.button("SKAPA LJUD"):
            res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 8})
            st.audio(str(res))

    with tabs[3]: # ARKIV
        st.subheader(L["upload_label"])
        with st.form("up_form"):
            new_img = st.file_uploader("Välj bild:", type=["jpg", "png", "jpeg"])
            if st.form_submit_button(L["upload_btn"]):
                if new_img:
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": "Uppladdning", "video": new_img})
                    st.rerun()
        st.divider()
        my_f = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for item in reversed(my_f):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if st.button(L["set_bg"], key=f"bg_{item['id']}"):
                    st.session_state.app_bg_url = item['video']
                    st.rerun()

    with tabs[4]: # FEED
        for item in reversed(st.session_state.gallery[-10:]):
            st.image(item['video'], caption=f"By: {item['artist']}")
            st.divider()

    if is_admin:
        with tabs[5]:
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API-nyckel saknas i Secrets!")





















