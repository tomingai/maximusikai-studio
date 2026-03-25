import streamlit as st
import replicate
import os
import time
import requests

# --- 1. SETUP & SESSION STATE (LÅST GRUND) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. DESIGN-MOTOR (HELT LÅST) ---
def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
                background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
            }}
            .logo-text {{
                font-size: 3rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
                text-transform: uppercase; letter-spacing: 5px;
                text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00d2ff, 0 0 40px #00d2ff !important;
                margin-bottom: 20px;
            }}
            div[data-baseweb="base-input"], div[data-baseweb="textarea"], .stTextArea textarea, .stTextInput input {{
                background-color: rgba(255,255,255,0.1) !important; color: white !important;
                backdrop-filter: blur(15px) !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important;
            }}
            label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
                color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; font-weight: 800 !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(0,0,0,0.4) !important; border-radius: 10px !important; }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 3. HJÄLPFUNKTION FÖR URL ---
def get_url(res):
    if isinstance(res, list): return str(res[0])
    if hasattr(res, 'url'): return str(res.url)
    return str(res)

# --- 4. SPRÅK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "RYMDEN 🌌", "atm_forest": "SKOGEN 🌲", "atm_city": "STADEN 🌆", "atm_bake": "BAKNING 🥐",
        "status": "STATUS", "units": "UNITS", "set_bg": "🖼 SÄTT SOM BAKGRUND", "download": "💾 LADDA NER"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "SPACE 🌌", "atm_forest": "FOREST 🌲", "atm_city": "CITY 🌆", "atm_bake": "BAKING 🥐",
        "status": "STATUS", "units": "UNITS", "set_bg": "🖼 SET AS BACKGROUND", "download": "💾 DOWNLOAD"
    }
}
L = texts[st.session_state.lang]

# --- 5. SIDOMENY ---
with st.sidebar:
    st.title("STUDIO")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    u_creds = st.session_state.user_db[artist_id]
    
    # --- FIXAD F-STRING (Dubbla citattecken för ordboksnyckeln) ---
    u_units_label = L["units"]
    status_msg = "💎 ADMIN" if is_admin else f"⚡ {u_creds} {u_units_label}"
    st.info(f"{L['status']}: {status_msg}")
    
    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2); c3, c4 = st.columns(2)
    
    if c1.button(L["atm_space"]):
        st.session_state.app_bg = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, 4k"})); st.rerun()
    if c2.button(L["atm_forest"]):
        st.session_state.app_bg = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Magic forest, sunlight, 4k"})); st.rerun()
    if c3.button(L["atm_city"]):
        st.session_state.app_bg = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Cyberpunk city neon, 4k"})); st.rerun()
    if c4.button(L["atm_bake"]):
        st.session_state.app_bg = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Artisan bakery, 4k"})); st.rerun()
    if st.button("❌ NOLLSTÄLL DESIGN"):
        st.session_state.app_bg = None; st.rerun()

# --- 6. HUVUDAPP ---
apply_design()
st.markdown(f'<div class="logo-text">⚡ {L["title"]} ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): st.session_state.agreed = True; st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tab_list = L["tab_names"] if is_admin else L["tab_names"][:-1]
    tabs = st.tabs(tab_list)

    with tabs[0]: # MAGI
        prompt = st.text_area("VAD SKALL VI SKAPA?", key="main_p")
        if st.button("STARTA GENERERING", use_container_width=True):
            if u_creds > 0 or is_admin:
                with st.status("AI arbetar..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    img_url = get_url(img_res)
                    mu_url = None
                    try:
                        mu_res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", 
                                               input={"prompt": prompt, "duration": 8})
                        mu_url = str(mu_res)
                    except: mu_url = None
                    if st.session_state.app_bg is None: st.session_state.app_bg = img_url
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:20], "url": img_url, "audio": mu_url})
                    st.rerun()

    with tabs[1]: # REGI
        st.subheader("🎬 LUMA DREAM MACHINE")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_imgs: st.info("Skapa en bild i MAGI först!")
        else:
            img_choice = st.selectbox("Välj bild:", [p["name"] for p in my_imgs])
            selected_url = next(p["url"] for p in my_imgs if p["name"] == img_choice)
            st.image(selected_url, width=300)
            vid_p = st.text_input("Instruktion:", "Cinematic motion")
            if st.button("SKAPA VIDEO (5 UNITS)"):
                if u_creds >= 5 or is_admin:
                    with st.status("Luma arbetar..."):
                        try:
                            if not is_admin: st.session_state.user_db[artist_id] -= 5
                            vid_res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": vid_p, "image_url": selected_url})
                            st.video(get_url(vid_res))
                        except: st.error("Luma är upptagen eller kräver betalkonto.")
                else: st.error("För få Units!")

    with tabs[2]: # MUSIK
        mu_in = st.text_input("Beskriv beatet:", key="mu_input")
        if st.button("SKAPA LJUD"):
            with st.spinner("Komponerar..."):
                res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", 
                                   input={"prompt": mu_in, "duration": 10})
                st.audio(str(res))

    with tabs[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my: st.info("Inga sparade verk.")
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(str(p["url"])) 
                c1, c2 = st.columns(2)
                if c1.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = str(p["url"]); st.rerun()
                try:
                    img_data = requests.get(p["url"]).content
                    c2.download_button(L["download"], data=img_data, file_name=f"{p['name']}.png", mime="image/png", key=f"dl_{p['id']}")
                except: pass
                if p["audio"]: st.audio(str(p["audio"]))

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(str(p["url"]), caption=f"Artist: {p['artist']}")
            if p["audio"]: st.audio(str(p["audio"]))
            st.divider()

    if is_admin and len(tabs) > 5:
        with tabs[5]: # ADMIN
            st.write(st.session_state.user_db)
            if st.button("RENSA"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API TOKEN SAKNAS")










































