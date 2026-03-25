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
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "VAD SKALL WE SKAPA?", "start_btn": "STARTA GENERERING",
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

# --- 3. DYNAMISK DESIGN (GLASSMORPHISM TEXTRUTOR) ---
if st.session_state.app_bg:
    raw_bg = st.session_state.app_bg
    bg_url = raw_bg if isinstance(raw_bg, list) else str(raw_bg)
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.2)), url("{bg_url}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        
        /* TEXT & RUBRIKER */
        label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; 
            text-shadow: 2px 2px 5px rgba(0,0,0,0.8) !important; 
            font-weight: 700 !important; 
        }}

        /* GENOMSKINLIGA TEXTRUTOR (FIXADE) */
        .stTextArea textarea, .stTextInput input {{
            background-color: rgba(255, 255, 255, 0.07) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }}
        
        /* TEXTRUTOR VID FOCUS */
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            background-color: rgba(255, 255, 255, 0.12) !important;
        }}

        /* TRANSPARENTA FLIKAR */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 8px;
        }}
        
        /* KNAPPAR */
        .stButton button {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(5px);
            border-radius: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 4. SIDOMENY ---
with st.sidebar:
    st.title("STUDIO")
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: 
        st.session_state.user_db[artist_id] = 10
    
    is_admin = (artist_id == "TOMAS2026")
    u_creds = st.session_state.user_db[artist_id]
    
    st.info(f"{L['status']}: {'💎 ADMIN' if is_admin else f'⚡ {u_creds} {L['units']}'}")
    
    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2)
    
    if c1.button(L["atm_space"]):
        st.session_state.app_bg = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, 4k"})
        st.rerun()
    if c2.button(L["atm_forest"]):
        st.session_state.app_bg = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Magic forest sunbeams, 4k"})
        st.rerun()
    
    if st.button("❌ RESET DESIGN"):
        st.session_state.app_bg = None
        st.rerun()

# --- 5. HUVUDAPP ---
st.markdown(f'<h1 style="text-align:center;">{L["title"]}</h1>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    
    tab_list = [L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"]]
    if is_admin: tab_list.append(L["tab6"])
    tabs = st.tabs(tab_list)

    with tabs[0]: # MAGI
        prompt = st.text_area(L["prompt_label"], key="main_p", height=150)
        if st.button(L["start_btn"], use_container_width=True):
            if st.session_state.user_db[artist_id] > 0 or is_admin:
                with st.status("AI arbetar..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img_out = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    mu_out = replicate.run("facebookresearch/musicgen", input={"prompt": prompt, "duration": 8})
                    st.session_state.gallery.append({
                        "id": time.time(), "artist": artist_id, "name": prompt[:20], 
                        "url": img_out if isinstance(img_out, list) else str(img_out), 
                        "audio": str(mu_out)
                    })
                    st.rerun()

    with tabs[1]: # REGI
        st.subheader("BILD TILL VIDEO")
        up_img = st.file_uploader("Ladda upp:", type=["jpg", "png"])
        if up_img and st.button("ANIMERA"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic move"})
            st.video(str(res))

    with tabs[2]: # MUSIK
        mu_prompt = st.text_input("Beskriv ljudet:", key="mu_in")
        if st.button("SKAPA MUSIK"):
            res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_prompt, "duration": 10})
            st.audio(str(res))

    with tabs[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(p["url"])
                if st.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = p["url"]
                    st.rerun()

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            st.divider()

    if is_admin:
        with tabs[5]: # ADMIN
            st.write(st.session_state.user_db)
            if st.button("RENSA"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API Token saknas!")

























