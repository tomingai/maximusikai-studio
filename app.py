import streamlit as st
import replicate
import os
import time
import requests

# --- 1. SETUP & SESSION STATE (STENHÅRT LÅST) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. DESIGN-MOTOR (LÅST DESIGN) ---
def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
                background-size: cover !important; 
                background-position: center !important; 
                background-attachment: fixed !important;
            }}
            .logo-text {{
                font-size: 3rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
                text-transform: uppercase; letter-spacing: 5px;
                text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00d2ff, 0 0 40px #00d2ff !important;
                margin-bottom: 25px;
            }}
            p, label, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
                color: white !important; 
                text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; 
                font-weight: 900 !important;
            }}
            div[data-baseweb="base-input"], div[data-baseweb="textarea"], .stTextArea textarea, .stTextInput input {{
                background-color: rgba(255,255,255,0.12) !important; color: white !important;
                backdrop-filter: blur(20px) !important; border: 1px solid rgba(255,255,255,0.3) !important; border-radius: 12px !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(0,0,0,0.5) !important; border-radius: 10px !important; }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

def get_url(res):
    if isinstance(res, list): return str(res[0])
    if hasattr(res, "url"): return str(res.url)
    return str(res)

# --- 3. SPRÅK & SIDOMENY ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
        "units": "UNITS", "set_bg": "🖼 SÄTT SOM BAKGRUND", "download": "💾 LADDA NER"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED", "⚙️ ADMIN"],
        "units": "UNITS", "set_bg": "🖼 SET AS BACKGROUND", "download": "💾 DOWNLOAD"
    }
}
L = texts[st.session_state.lang]

with st.sidebar:
    st.title("STUDIO")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    u_val = st.session_state.user_db[artist_id]
    u_txt = L["units"]
    st.markdown(f"**STATUS:** {'💎 ADMIN' if is_admin else f'⚡ {u_val} {u_txt}'}")
    
    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2)
    if c1.button("RYMDEN 🌌"):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, 4k"})
        st.session_state.app_bg = get_url(res); st.rerun()
    if c2.button("SKOGEN 🌲"):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Magic forest, sunlight, 4k"})
        st.session_state.app_bg = get_url(res); st.rerun()
        
    if st.button("❌ RESET DESIGN"): st.session_state.app_bg = None; st.rerun()

# --- 4. HUVUDAPP ---
apply_design()
st.markdown(f'<div class="logo-text">⚡ {L["title"]} ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): st.session_state.agreed = True; st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    # SKAPA FLIKAR OCH LÅS DEM MED INDEX
    tabs = st.tabs(L["tab_names"] if is_admin else L["tab_names"][:-1])

    with tabs[0]: # MAGI
        prompt = st.text_area("VAD SKALL VI SKAPA?", key="m_p")
        if st.button("STARTA GENERERING", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("AI arbetar..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    img_url = get_url(img_res)
                    try:
                        mu_res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": prompt, "duration": 8})
                        mu_url = str(mu_res)
                    except: mu_url = None
                    if st.session_state.app_bg is None: st.session_state.app_bg = img_url
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:20], "url": img_url, "audio": mu_url})
                    st.rerun()

    with tabs[1]: # REGI
        st.subheader("🎬 LUMA DREAM MACHINE")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_imgs: st.info("Skapa en bild först!")
        else:
            img_choice = st.selectbox("Välj bild:", [p["name"] for p in my_imgs], key="vid_sel")
            selected_url = next(p["url"] for p in my_imgs if p["name"] == img_choice)
            st.image(selected_url, width=300)
            if st.button("ANIMERA (5 UNITS)", key="vid_btn"):
                if is_admin or st.session_state.user_db[artist_id] >= 5:
                    with st.status("Luma arbetar..."):
                        try:
                            if not is_admin: st.session_state.user_db[artist_id] -= 5
                            vid = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": selected_url})
                            st.video(get_url(vid))
                        except: st.error("Luma är högbelastad.")
                else: st.error("För få units.")

    with tabs[2]: # MUSIK
        mu_in = st.text_input("Beskriv beatet:", key="mu_in_field")
        if st.button("SKAPA", key="mu_btn"):
            res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": mu_in, "duration": 10})
            st.audio(str(res))

    with tabs[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(str(p["url"]))
                c1, c2 = st.columns(2)
                if c1.button(L["set_bg"], key=f"s_{p['id']}"): 
                    st.session_state.app_bg = p["url"]
                    st.rerun()
                try: 
                    img_data = requests.get(p["url"]).content
                    c2.download_button(L["download"], img_data, f"{p['name']}.png", "image/png", key=f"d_{p['id']}")
                except: pass
                if p["audio"]: st.audio(p["audio"])

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            if p["audio"]: st.audio(p["audio"])
            st.divider()

    if is_admin:
        with tabs[5]: # ADMIN
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT", key="admin_clear"): 
                st.session_state.gallery = []
                st.rerun()
else:
    st.error("API TOKEN SAKNAS")












































