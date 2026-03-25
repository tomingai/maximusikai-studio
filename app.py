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
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "gen_bg": "🪄 GENERERA BAKGRUND",
        "reset": "ÅTERSTÄLL DESIGN",
        "status": "STATUS", "units": "UNITS",
        "atmosphere": "VÄLJ ATMOSFÄR:",
        "atm_space": "Space (Rymden) 🌌",
        "atm_forest": "Forest (Skogen) 🌲",
        "atm_city": "City (Staden) 🌆",
        "atm_bake": "Baking (Bakning) 🥐"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "gen_bg": "🪄 GENERATE BACKGROUND",
        "reset": "RESET DESIGN",
        "status": "STATUS", "units": "UNITS",
        "atmosphere": "CHOOSE ATMOSPHERE:",
        "atm_space": "Space 🌌",
        "atm_forest": "Forest 🌲",
        "atm_city": "City 🌆",
        "atm_bake": "Baking 🥐"
    }
}
L = texts[st.session_state.lang]

# --- 3. DYNAMISK DESIGN & ATMOSFÄR ---
with st.sidebar:
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    st.divider()
    
    st.markdown(f"### 🎨 {L['atmosphere']}")
    # Atmosfär-alternativ inklusive Bakning
    options = [L["atm_space"], L["atm_forest"], L["atm_city"], L["atm_bake"]]
    atm_choice = st.selectbox(L["atmosphere"], options, label_visibility="collapsed")
    
    atm_prompts = {
        L["atm_space"]: "Deep space nebula, cosmic dust, stars and galaxies, cinematic lighting, 4k, minimalist background",
        L["atm_forest"]: "Magic enchanted forest, sunlight through trees, misty atmosphere, high quality, 4k, peaceful nature",
        L["atm_city"]: "Cyberpunk city skyline at night, neon lights, rainy streets, cinematic reflection, futuristic metropolis, 4k",
        L["atm_bake"]: "Cozy rustic bakery, flour on wooden table, freshly baked cinnamon buns, warm golden lighting, aesthetic kitchen, 4k"
    }

    if st.button(L["gen_bg"]):
        token = st.secrets.get("REPLICATE_API_TOKEN")
        if token:
            os.environ["REPLICATE_API_TOKEN"] = token
            with st.spinner(f"AI skapar din {atm_choice}..."):
                try:
                    bg_img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": atm_prompts[atm_choice]})
                    st.session_state.app_bg_url = str(bg_img) if isinstance(bg_img, list) else str(bg_img)
                    st.rerun()
                except Exception as e:
                    st.error(f"Kunde inte skapa bakgrund: {e}")
        else:
            st.error("API-nyckel saknas!")

    if st.button(L["reset"]):
        st.session_state.app_bg_url = None
        st.rerun()

# --- CSS FÖR ANPASSAT GRÄNSSNITT (Synliga flikar) ---
bg_css = ""
if st.session_state.app_bg_url:
    # Mörkt filter (rgba 0.7) + Bakgrundsbild
    bg_css = f"""
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{st.session_state.app_bg_url}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    """
else:
    bg_css = ".stApp { background-color: #050505 !important; }"

st.markdown(f"""
    <style>
    {bg_css}
    /* Gör flikarna (tabs) tydliga och vita */
    .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 5px; }}
    .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: 900 !important; font-size: 16px !important; }}
    .stTabs [aria-selected="true"] {{ border-bottom: 3px solid #bf00ff !important; }}
    
    /* Neon-container för rubrik */
    .neon-container {{ 
        background: rgba(0,0,0,0.4); backdrop-filter: blur(10px); padding: 20px; 
        border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); 
        text-align: center; margin-bottom: 20px; 
    }}
    
    label, p, span, h1, h2, h3 {{ color: white !important; text-shadow: 1px 1px 5px black; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY & ANVÄNDARE ---
with st.sidebar:
    st.divider()
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: 
        st.session_state.user_db[artist_id] = {"credits": 10}
    
    user_info = st.session_state.user_db[artist_id]
    u_creds = user_info.get("credits", 0)
    st.info(f"{L['status']}: ⚡ {u_creds} {L['units']}")

# --- 5. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><h1 style="color:white; margin:0;">{L["title"]}</h1></div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# --- STUDIO TABS ---
token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV"])

    with tabs[0]: # MAGI
        m_ide = st.text_area("VAD SKALL VI SKAPA?")
        if st.button("STARTA GENERERING"):
            if user_info["credits"] > 0:
                with st.status("AI SKAPAR..."):
                    user_info["credits"] -= 1
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": m_ide})
                    img_url = str(img) if isinstance(img, list) else str(img)
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": m_ide[:15], "video": img_url})
                    st.rerun()

    with tabs[3]: # ARKIV
        my_f = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for item in reversed(my_f):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if st.button("SÄTT SOM BAKGRUND", key=f"set_{item['id']}"):
                    st.session_state.app_bg_url = item['video']
                    st.rerun()
else:
    st.error("API-nyckel saknas!")























