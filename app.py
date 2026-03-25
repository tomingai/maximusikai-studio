import streamlit as st
import replicate
import os
import time
import requests

# --- 1. SETUP & SESSION STATE (STENHÅRT LÅST) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

for key, val in {"gallery": [], "user_db": {}, "app_bg": None, "agreed": False, "lang": "Svenska"}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. DESIGN-MOTOR (LÅST DESIGN) ---
def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("{bg_url}") !important;
                background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
            }}
            .logo-text {{
                font-size: 3.2rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
                text-transform: uppercase; letter-spacing: 5px;
                text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00d2ff, 0 0 40px #00d2ff !important;
                margin-bottom: 25px;
            }}
            p, label, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
                color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,1) !important; font-weight: 900 !important;
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

# --- 3. ATMOSFÄR-BIBLIOTEK (10 FASTA BILDER) ---
atmospheres = {
    "Svenska": {
        "Välj Atmosfär 🖼": None,
        "Rymden 🌌": "https://images.unsplash.com",
        "Magisk Skog 🌲": "https://images.unsplash.com",
        "Cyberpunk City 🌆": "https://images.unsplash.com",
        "Undervattnet 🌊": "https://images.unsplash.com",
        "Arktisk Is ❄️": "https://images.unsplash.com",
        "Guld-Öken 🏜️": "https://images.unsplash.com",
        "Neon-Laboratorium 🧪": "https://images.unsplash.com",
        "Gotiskt Slott 🏰": "https://images.unsplash.com",
        "Bageri 🥐": "https://images.unsplash.com",
        "Abstrakt Konst 🌈": "https://images.unsplash.com"
    },
    "English": {
        "Choose Atmosphere 🖼": None,
        "Deep Space 🌌": "https://images.unsplash.com",
        "Magic Forest 🌲": "https://images.unsplash.com",
        "Cyber City 🌆": "https://images.unsplash.com",
        "Underwater 🌊": "https://images.unsplash.com",
        "Arctic Ice ❄️": "https://images.unsplash.com",
        "Golden Desert 🏜️": "https://images.unsplash.com",
        "Tech Lab 🧪": "https://images.unsplash.com",
        "Dark Castle 🏰": "https://images.unsplash.com",
        "Bakery 🥐": "https://images.unsplash.com",
        "Abstract Art 🌈": "https://images.unsplash.com"
    }
}

# --- 4. SPRÅK & SIDOMENY ---
lang = st.session_state.lang
L = atmospheres[lang]

with st.sidebar:
    st.title("STUDIO SETTINGS")
    new_lang = st.radio("Language:", ["Svenska", "English"], index=0 if lang=="Svenska" else 1, horizontal=True)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.divider()
    # RULLMENY FÖR 10 ATMOSFÄRER
    choice = st.selectbox(list(L.keys())[0], list(L.keys()))
    if L[choice] != st.session_state.app_bg and L[choice] is not None:
        st.session_state.app_bg = L[choice]
        st.rerun()

    st.divider()
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    u_val = st.session_state.user_db[artist_id]
    st.markdown(f"**STATUS:** {'💎 ADMIN' if is_admin else f'⚡ {u_val} UNITS'}")
    if st.button("❌ RESET"): st.session_state.app_bg = None; st.rerun()

# --- 5. HUVUDAPP ---
apply_design()
st.markdown(f'<div class="logo-text">⚡ {st.session_state.lang == "Svenska" and "MAXIMUSIKAI STUDIO" or "MAXIMUSIKAI STUDIO"} ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): st.session_state.agreed = True; st.rerun()
    st.stop()

# --- FLIKAR ---
token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs_labels = ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"]
    if is_admin: tabs_labels.append("⚙️ ADMIN")
    t = st.tabs(tabs_labels)

    with t[0]: # MAGI
        prompt = st.text_area("VAD SKALL VI SKAPA?", key="m_p")
        if st.button("STARTA GENERERING", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("AI arbetar..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    img_url = str(img_res[0]) if isinstance(img_res, list) else str(img_res)
                    try:
                        mu_res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": prompt, "duration": 8})
                        mu_url = str(mu_res)
                    except: mu_url = None
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:20], "url": img_url, "audio": mu_url})
                    st.rerun()

    with t[1]: # REGI
        st.subheader("🎬 VIDEO ANIMATION")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_imgs: st.info("Skapa en bild först!")
        else:
            img_choice = st.selectbox("Välj bild:", [p["name"] for p in my_imgs], key="v_sel")
            selected_url = next(p["url"] for p in my_imgs if p["name"] == img_choice)
            st.image(selected_url, width=300)
            if st.button("ANIMERA (5 UNITS)"):
                if is_admin or st.session_state.user_db[artist_id] >= 5:
                    with st.status("Luma arbetar..."):
                        try:
                            if not is_admin: st.session_state.user_db[artist_id] -= 5
                            vid = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": selected_url})
                            st.video(str(vid))
                        except: st.error("Luma är högbelastad just nu.")

    with t[2]: # MUSIK
        mu_in = st.text_input("Beskriv ljudet:", key="mu_in_f")
        if st.button("SKAPA"):
            res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": mu_in, "duration": 10})
            st.audio(str(res))

    with t[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(p["url"])
                if st.button("SÄTT SOM BAKGRUND", key=f"s_{p['id']}"): 
                    st.session_state.app_bg = p["url"]
                    st.rerun()
                if p["audio"]: st.audio(p["audio"])

    with t[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            if p["audio"]: st.audio(p["audio"])
            st.divider()

    if is_admin:
        with t[5]: # ADMIN
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API TOKEN SAKNAS")













































