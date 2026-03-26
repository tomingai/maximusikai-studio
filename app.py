import streamlit as st
import replicate
import os
import time
import requests
from datetime import datetime

# --- 1. KONFIGURATION & SESSION ---
st.set_page_config(page_title="MAXIMUSIKAI 2026", page_icon="⚡", layout="wide")

# Initiera session state om det saknas
for key, default in {
    "gallery": [], 
    "user_db": {"ANONYM": 10, "TOMAS2026": 999}, 
    "app_bg": None, 
    "agreed": False, 
    "lang": "Svenska"
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. CSS-MOTOR (FÖRBÄTTRAD DESIGN) ---
def apply_design():
    bg_style = f'background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{st.session_state.app_bg}") !important;' if st.session_state.app_bg else 'background-color: #0a0a0a !important;'
    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} background-size: cover !important; background-attachment: fixed !important; }}
        .stButton>button {{
            border-radius: 20px; border: 1px solid #00d2ff; background: rgba(0,210,255,0.1);
            color: white; transition: 0.3s; font-weight: bold; width: 100%;
        }}
        .stButton>button:hover {{ background: #00d2ff; color: black; box-shadow: 0 0 15px #00d2ff; }}
        .card {{
            background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        }}
        </style>
    """, unsafe_allow_html=True)

def get_url(res):
    try:
        if isinstance(res, list): return str(res[0])
        return str(res)
    except: return None

# --- 3. SIDEBAR & LOGIK ---
with st.sidebar:
    st.title("⚡ MAXIMUSIKAI")
    st.session_state.lang = st.radio("Språk", ["Svenska", "English"], horizontal=True)
    artist_id = st.text_input("ARTIST ID", "ANONYM").strip().upper()
    
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    st.metric("UNITS", st.session_state.user_db[artist_id])
    
    if st.button("🌌 GENERERA NY BAKGRUND"):
        with st.spinner("Skapar atmosfär..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Abstract cinematic neon cyber landscape, 4k"})
            st.session_state.app_bg = get_url(res)
            st.rerun()

# --- 4. HUVUDAPP ---
apply_design()
L = {"Svenska": ["MAGI", "REGI", "MUSIK", "ARKIV", "ADMIN"], "English": ["MAGIC", "DIRECTOR", "MUSIC", "ARCHIVE", "ADMIN"]}[st.session_state.lang]

if not st.session_state.agreed:
    st.markdown("# VÄLKOMMEN TILL FRAMTIDEN")
    if st.button("ENTRÉ STUDIO"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# API-Check
token = st.secrets.get("REPLICATE_API_TOKEN")
if not token:
    st.error("TOKEN SAKNAS! Lägg till REPLICATE_API_TOKEN i Streamlit Secrets.")
    st.stop()
os.environ["REPLICATE_API_TOKEN"] = token

tabs = st.tabs(L if is_admin else L[:-1])

# --- FLIK 1: MAGI (BILD + MUSIK) ---
with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        prompt = st.text_area("BESKRIV DIN VISION", placeholder="En cyberpunk-stad i regn...")
    with col2:
        aspect = st.selectbox("FORMAT", ["1:1", "16:9", "9:16"])
        generate = st.button("🔥 GENERERA ALLT")

    if generate and prompt:
        if st.session_state.user_db[artist_id] > 0 or is_admin:
            with st.status("AI-KÄRNAN ARBETAR...", expanded=True) as status:
                st.write("Genererar bild med FLUX...")
                img_url = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect}))
                
                st.write("Komponerar musik med MusicGen...")
                try:
                    mu_url = get_url(replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", 
                                                input={"prompt": f"Lo-fi electronic: {prompt}", "duration": 8}))
                except: mu_url = None
                
                if not is_admin: st.session_state.user_db[artist_id] -= 1
                
                item = {"id": time.time(), "artist": artist_id, "prompt": prompt, "img": img_url, "audio": mu_url, "date": datetime.now().strftime("%H:%M")}
                st.session_state.gallery.append(item)
                status.update(label="KLART!", state="complete")
                st.rerun()
        else: st.error("Slut på units!")

# --- FLIK 2: REGI (VIDEO) ---
with tabs[1]:
    st.subheader("🎬 ANIMERA DINA BILDER")
    user_items = [i for i in st.session_state.gallery if i["artist"] == artist_id]
    if not user_items:
        st.info("Skapa en bild i MAGI-fliken först.")
    else:
        selected_prompt = st.selectbox("Välj bild att animera", [i["prompt"][:50] for i in user_items])
        target = next(i for i in user_items if i["prompt"][:50] == selected_prompt)
        st.image(target["img"], width=400)
        
        if st.button("🎬 SKAPA VIDEO (5 UNITS)"):
            if st.session_state.user_db[artist_id] >= 5 or is_admin:
                with st.spinner("Luma Dream Machine renderar..."):
                    try:
                        vid_url = get_url(replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion, slow camera pan", "image_url": target["img"]}))
                        st.video(vid_url)
                        if not is_admin: st.session_state.user_db[artist_id] -= 5
                    except Exception as e:
                        st.error(f"Kunde inte skapa video: {e}")
            else: st.error("För få units.")

# --- FLIK 3: MUSIK (BEATS) ---
with tabs[2]:
    st.subheader("🎧 BEAT GENERATOR")
    m_prompt = st.text_input("Vilken typ av beat?")
    duration = st.slider("Längd (sek)", 5, 20, 10)
    if st.button("🎶 SKAPA BEAT"):
        with st.spinner("Skapar ljudvågor..."):
            res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", 
                               input={"prompt": m_prompt, "duration": duration})
            st.audio(get_url(res))

# --- FLIK 4: ARKIV (GRID LAYOUT) ---
with tabs[3]:
    st.subheader("📚 DITT GALLERI")
    my_stuff = [i for i in st.session_state.gallery if i["artist"] == artist_id]
    
    cols = st.columns(3)
    for idx, item in enumerate(reversed(my_stuff)):
        with cols[idx % 3]:
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            st.image(item["img"])
            st.caption(f"🕒 {item['date']} - {item['prompt'][:30]}...")
            if item["audio"]: st.audio(item["audio"])
            if st.button("🖼 BAKGRUND", key=f"bg_{item['id']}"):
                st.session_state.app_bg = item["img"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()

# --- FLIK 5: ADMIN ---
if is_admin:
    with tabs[4]:
        st.subheader("⚙️ SYSTEM CONTROL")
        st.write("Användare:", st.session_state.user_db)
        if st.button("RENSA ALL DATA"):
            st.session_state.gallery = []
            st.rerun()
