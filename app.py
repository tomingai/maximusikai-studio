import streamlit as st
import replicate
import os
import time
import requests
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

for key, default in {
    "gallery": [], 
    "user_db": {"ANONYM": 10, "TOMAS2026": 999}, 
    "app_bg": "https://images.unsplash.com", # Standard ljus bg
    "agreed": False, 
    "lang": "Svenska"
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. DESIGN-MOTOR (LJUSARE & STARKARE) ---
def apply_design():
    # Overlay på 0.3 för att låta bakgrundsbilden vara tydlig och ljus
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; 
            background-position: center !important; 
            background-attachment: fixed !important;
        }}
        .logo-text {{
            font-size: 3.5rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
            text-transform: uppercase; letter-spacing: 5px;
            text-shadow: 0 0 20px rgba(0,210,255,0.8), 2px 2px 10px rgba(0,0,0,0.5) !important;
            margin-bottom: 25px;
        }}
        /* Kontrast för läsbarhet på ljus bakgrund */
        p, label, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; 
            text-shadow: 1px 1px 5px rgba(0,0,0,0.8) !important; 
            font-weight: 800 !important;
        }}
        .card {{
            background: rgba(0,0,0,0.4) !important; 
            backdrop-filter: blur(15px);
            border-radius: 20px; padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 10px;
        }}
        div[data-baseweb="base-input"], textarea, input {{
            background-color: rgba(255,255,255,0.2) !important; color: white !important;
            backdrop-filter: blur(10px) !important; border: 1px solid white !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def get_url(res):
    if isinstance(res, list): return str(res[0])
    if hasattr(res, "url"): return str(res.url)
    return str(res)

# --- 3. SIDEBAR & ATMOSFÄR-KONTROLL ---
with st.sidebar:
    st.title("⚡ STUDIO")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    st.metric("DINA UNITS", st.session_state.user_db[artist_id])
    
    st.divider()
    st.subheader("🖼 VÄLJ ATMOSFÄR (LJUS)")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    
    themes = {
        "CYBER 🤖": "High-tech vaporwave city, neon lights, bright purple and cyan, 4k",
        "DRÖM ☁️": "Ethereal dreamscape, bright clouds, golden hour, peaceful, 4k",
        "LYX 💎": "Clean white marble music studio, minimalist gold, bright daylight, 4k",
        "ABSTRAKT 🎨": "Bright liquid explosion of colors, white background, cinematic 4k"
    }

    def set_bg(theme_key):
        with st.spinner("Skapar atmosfär..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes[theme_key]})
            st.session_state.app_bg = get_url(res)
            st.rerun()

    if c1.button("CYBER 🤖"): set_bg("CYBER 🤖")
    if c2.button("DRÖM ☁️"): set_bg("DRÖM ☁️")
    if c3.button("LYX 💎"): set_bg("LYX 💎")
    if c4.button("ABSTRAKT 🎨"): set_bg("ABSTRAKT 🎨")
    
    if st.button("❌ ÅTERSTÄLL DESIGN", use_container_width=True):
        st.session_state.app_bg = "https://images.unsplash.com"
        st.rerun()

# --- 4. HUVUDLOGIK ---
apply_design()
L_text = {
    "Svenska": {"title": "MAXIMUSIKAI STUDIO", "tabs": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"]},
    "English": {"title": "MAXIMUSIKAI STUDIO", "tabs": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "⚙️ ADMIN"]}
}
L = L_text[st.session_state.lang]

st.markdown(f'<div class="logo-text">⚡ {L["title"]} ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("ENTRÉ STUDIO", use_container_width=True): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# API Token
token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(L["tabs"] if is_admin else L["tabs"][:-1])

    # --- TAB 1: MAGI ---
    with tabs[0]:
        col1, col2 = st.columns([2,1])
        with col1:
            prompt = st.text_area("VAD SKALL VI SKAPA?", placeholder="En futuristisk konsert i rymden...")
        with col2:
            aspect = st.selectbox("FORMAT", ["1:1", "16:9", "9:16"])
            gen_btn = st.button("STARTA GENERERING", use_container_width=True)

        if gen_btn and prompt:
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("AI arbetar...", expanded=True) as status:
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect})
                    img_url = get_url(img_res)
                    try:
                        mu_res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", 
                                             input={"prompt": prompt, "duration": 8})
                        mu_url = str(mu_res)
                    except: mu_url = None
                    
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img_url, "audio": mu_url})
                    status.update(label="KLART!", state="complete")
                    st.rerun()

    # --- TAB 2: REGI ---
    with tabs[1]:
        st.subheader("🎬 LUMA DREAM MACHINE")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_imgs: st.info("Skapa en bild först!")
        else:
            selected_name = st.selectbox("Välj bild:", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == selected_name)
            st.image(target["url"], width=400)
            if st.button("ANIMERA (5 UNITS)"):
                if is_admin or st.session_state.user_db[artist_id] >= 5:
                    with st.spinner("Luma renderar din video..."):
                        vid = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": target["url"]})
                        st.video(get_url(vid))
                        if not is_admin: st.session_state.user_db[artist_id] -= 5
                else: st.error("För få units.")

    # --- TAB 3: MUSIK ---
    with tabs[2]:
        mu_in = st.text_input("Beskriv beatet (t.ex. 'Heavy Techno 140bpm'):")
        if st.button("SKAPA LJUD"):
            with st.spinner("Komponerar..."):
                res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": mu_in, "duration": 10})
                st.audio(str(res))

    # --- TAB 4: ARKIV ---
    with tabs[3]:
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SÄTT SOM BG", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]
                    st.rerun()
                if p["audio"]: st.audio(p["audio"])
                st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 5: ADMIN ---
    if is_admin:
        with tabs[4]:
            st.write("ANVÄNDARE:", st.session_state.user_db)
            if st.button("NOLLSTÄLL ALLT"):
                st.session_state.gallery = []
                st.rerun()
else:
    st.warning("Vänligen lägg till REPLICATE_API_TOKEN i Streamlit Secrets.")

