import streamlit as st
import replicate
import os
import datetime
import time
import json
import urllib.parse

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "VAD SKALL VI SKAPA?", "start_btn": "STARTA GENERERING",
        "status": "STATUS", "units": "UNITS", "mood": "STÄMNING", "set_bg": "🖼 SÄTT SOM BAKGRUND",
        "atm_space": "RYMDEN 🌌", "atm_forest": "SKOGEN 🌲", "atm_city": "STADEN 🌆", "atm_bake": "BAKNING 🥐"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "WHAT SHALL WE CREATE?", "start_btn": "START GENERATING",
        "status": "STATUS", "units": "UNITS", "mood": "MOOD", "set_bg": "🖼 SET AS BACKGROUND",
        "atm_space": "SPACE 🌌", "atm_forest": "FOREST 🌲", "atm_city": "CITY 🌆", "atm_bake": "BAKING 🥐"
    }
}
L = texts[st.session_state.lang]

# --- 3. DYNAMISK DESIGN (FIXAD FÖR BILDER) ---
bg_img = st.session_state.app_bg
if bg_img:
    bg_url = bg_img[0] if isinstance(bg_img, list) else str(bg_img)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{bg_url}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        /* Gör flikarna och texten vita och tydliga */
        label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; text-shadow: 1px 1px 3px black !important; font-weight: bold !important; 
        }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255,255,255,0.1); border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 4. SIDOMENY (KONTROLLER) ---
with st.sidebar:
    st.title("STUDIO SETTINGS")
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    st.info(f"{L['status']}: {'💎 ADMIN' if is_admin else f'⚡ {st.session_state.user_db[artist_id]} {L['units']}'}")
    
    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2)
    if c1.button(L["atm_space"]):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, stars, 4k"})
        st.session_state.app_bg = res; st.rerun()
    if c2.button(L["atm_forest"]):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Magic forest, cinematic, 4k"})
        st.session_state.app_bg = res; st.rerun()
    if c1.button(L["atm_city"]):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Futuristic city night, 4k"})
        st.session_state.app_bg = res; st.rerun()
    if c2.button(L["atm_bake"]):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Cozy bakery, bread, golden light, 4k"})
        st.session_state.app_bg = res; st.rerun()
    
    if st.button("❌ RESET DESIGN"):
        st.session_state.app_bg = None; st.rerun()

# --- 5. HUVUDAPPEN ---
st.markdown(f'<h1 style="text-align:center; color:white;">{L["title"]}</h1>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True; st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"], L["tab6"] if is_admin else " "])

    with tabs[0]: # MAGIC
        prompt = st.text_area(L["prompt_label"], value=st.session_state.remix_prompt)
        if st.button(L["start_btn"]):
            if st.session_state.user_db[artist_id] > 0 or is_admin:
                with st.status("AI..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    mu = replicate.run("facebookresearch/musicgen", input={"prompt": "cinematic music", "duration": 5})
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:20], "url": img, "audio": mu})
                    st.rerun()

    with tabs[1]: # DIRECTOR (LUMA)
        up = st.file_uploader("Image:", type=["jpg", "png"], key="l_up")
        if up and st.button("KÖR ANIMATION"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": up})
            st.video(str(res))

    with tabs[2]: # MUSIC
        mu_p = st.text_input("Describe beat:")
        if st.button("CREATE AUDIO"):
            res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 10})
            st.audio(str(res))

    with tabs[3]: # ARCHIVE
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(p["url"])
                if st.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = p["url"]; st.rerun()
                if p.get("audio"): st.audio(p["audio"])

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            st.divider()

    if is_admin:
        with tabs[5]:
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API KEY MISSING")
























