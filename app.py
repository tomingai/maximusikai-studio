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

# --- 3. DYNAMISK DESIGN (BUGGFIXAD) ---
bg_data = st.session_state.app_bg
if bg_data:
    # Säkerställ att vi får en ren URL-sträng
    bg_url = bg_data[0] if isinstance(bg_data, list) else str(bg_data)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("{bg_url}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; text-shadow: 1px 1px 4px black !important; font-weight: bold !important; 
        }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255,255,255,0.15); border-radius: 10px; padding: 5px; }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 4. SIDOMENY ---
with st.sidebar:
    st.title("STUDIO")
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    # Buggfix: Separera f-string variabler
    u_creds = st.session_state.user_db[artist_id]
    u_unit_txt = L["units"]
    u_stat_txt = L["status"]
    
    if is_admin:
        st.info(f"{u_stat_txt}: 💎 ADMIN")
    else:
        st.info(f"{u_stat_txt}: ⚡ {u_creds} {u_unit_txt}")
    
    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2)
    
    if c1.button(L["atm_space"]):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, 4k"})
        st.session_state.app_bg = res; st.rerun()
    if c2.button(L["atm_forest"]):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Magic forest, sunlight, 4k"})
        st.session_state.app_bg = res; st.rerun()
    
    if st.button("❌ RESET DESIGN"):
        st.session_state.app_bg = None; st.rerun()

# --- 5. HUVUDAPP ---
st.markdown(f'<h1 style="text-align:center; color:white;">{L["title"]}</h1>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True; st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    
    # Skapa flikar (inkluderar admin om Tomas är inloggad)
    tab_list = [L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"]]
    if is_admin: tab_list.append(L["tab6"])
    tabs = st.tabs(tab_list)

    with tabs[0]: # MAGI
        prompt = st.text_area(L["prompt_label"], key="main_p")
        if st.button(L["start_btn"]):
            if st.session_state.user_db[artist_id] > 0 or is_admin:
                with st.status("AI..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img_out = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    mu_out = replicate.run("facebookresearch/musicgen", input={"prompt": "cinematic beat", "duration": 5})
                    
                    # Säkerställ URL
                    img_url = img_out[0] if isinstance(img_out, list) else str(img_out)
                    
                    st.session_state.gallery.append({
                        "id": time.time(), 
                        "artist": artist_id, 
                        "name": prompt[:15], 
                        "url": img_url, 
                        "audio": str(mu_out)
                    })
                    st.rerun()

    with tabs[1]: # REGI
        up_img = st.file_uploader("Bild:", type=["jpg", "png"], key="reg_up")
        if up_img and st.button("KÖR LUMA"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": up_img})
            st.video(str(res))

    with tabs[2]: # MUSIK
        mu_prompt = st.text_input("Beskriv beatet:", key="mu_in")
        if st.button("SKAPA LJUD"):
            res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_prompt, "duration": 10})
            st.audio(str(res))

    with tabs[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my: st.info("Tomt här än!")
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(p["url"])
                if st.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = p["url"]; st.rerun()
                if p["audio"]: st.audio(p["audio"])

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            st.divider()

    if is_admin:
        with tabs[5]: # ADMIN
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API KEY MISSING IN SECRETS")

























