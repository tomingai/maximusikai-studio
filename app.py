import streamlit as st
import replicate
import os
import time
import json
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. OSYNLIG KÄRNA (THE NEURAL ENGINE) ---
# Denna del hanterar tunga beräkningar och databassynk i bakgrunden
class MobileStudioKernel:
    @staticmethod
    def get_system_v(): return "PRO-2026-MOBILE-ULTIMATE"
    
    @staticmethod
    def log_action(user, action):
        if "action_logs" not in st.session_state: st.session_state.action_logs = []
        st.session_state.action_logs.append(f"[{datetime.now().strftime('%H:%M')}] {user}: {action}")

    @staticmethod
    def optimize_for_mobile():
        # Dold CSS-injektion för att dölja Streamlits standard-padding på mobil
        st.markdown("""
            <style>
            [data-testid="stAppViewBlockContainer"] { padding: 1rem 0.5rem !important; }
            [data-testid="stHeader"] { background: transparent !important; }
            .stTabs [data-baseweb="tab-list"] { gap: 10px !important; }
            </style>
        """, unsafe_allow_html=True)

# --- 2. DATABAS & STATE ---
DB_FILE = "mobile_studio_vault.json"
if "gallery" not in st.session_state: st.session_state.gallery = []
if "app_bg" not in st.session_state: 
    st.session_state.app_bg = "https://images.unsplash.com"
if "user_units" not in st.session_state: st.session_state.user_units = 25

# --- 3. MOBILE-CORE CSS (Häftiga bakgrunder & Glas) ---
def apply_mobile_design():
    bg = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* Mobil-bakgrund med parallax-känsla */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), url("{bg}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}

        /* Glas-paneler för mobil (Full-width) */
        .mobile-card {{
            background: rgba(0, 15, 30, 0.75) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(0, 242, 255, 0.4) !important;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
        }}

        /* Neon-knappar optimerade för tum-tryck */
        .stButton>button {{
            background: transparent !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            height: 60px !important;
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase;
            font-size: 1rem !important;
            letter-spacing: 2px;
            box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);
        }}
        
        .stButton>button:active {{
            background: #00f2ff !important;
            color: black !important;
            box-shadow: 0 0 30px #00f2ff;
        }}

        /* Inmatningsfält */
        textarea, input {{
            background-color: rgba(0,0,0,0.5) !important;
            color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.3) !important;
            font-size: 16px !important; /* Förhindrar auto-zoom på iPhone */
        }}

        .logo-text {{
            font-family: 'Orbitron'; font-size: 2.2rem; font-weight: 900;
            color: white; text-align: center; letter-spacing: 5px;
            text-shadow: 0 0 15px #00f2ff; padding: 20px 0;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. EXPLICIT MOBIL-GRÄNSSNITT ---
apply_mobile_design()
MobileStudioKernel.optimize_for_mobile()

st.markdown('<div class="logo-text">MAXIMUSIKAI</div>', unsafe_allow_html=True)

# Status-bar (Högst upp på mobil)
c1, c2 = st.columns([2, 1])
with c1:
    artist = st.text_input("PILOT ID:", "ANONYM", key="pilot").upper()
with c2:
    st.markdown(f"<p style='margin-top:35px; text-align:right;'>⚡ {st.session_state.user_units}</p>", unsafe_allow_html=True)

# --- 5. STUDIO MODULER ---
tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "📚 ARKIV"])

with tabs[0]: # MAGI-FLIKEN
    st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
    prompt = st.text_area("VAD SKA VI SKAPA?", placeholder="En rymdstation i neon...", height=120)
    
    # Snabb-knappar för mobil
    c1, c2 = st.columns(2)
    if c1.button("✨ FÖRBÄTTRA"):
        prompt = f"{prompt}, cinematic lighting, futuristic architecture, hyper-detailed, 8k, neon refraction"
        st.toast("Prompt optimerad för 2026!")
    
    if st.button("🔥 GENERERA (9:16)", use_container_width=True):
        if st.session_state.user_units > 0:
            with st.status("Neural Sync..."):
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                # Tvingar 9:16 format för mobil-bakgrund
                res = replicate.run("black-forest-labs/flux-schnell", 
                                   input={"prompt": prompt, "aspect_ratio": "9:16"})
                url = str(res[0]) if isinstance(res, list) else str(res)
                st.session_state.gallery.append({"u": artist, "url": url, "p": prompt})
                st.session_state.user_units -= 1
                MobileStudioKernel.log_action(artist, "Generated Image")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]: # REGI (Video)
    user_stuff = [p for p in st.session_state.gallery if p["u"] == artist]
    if user_stuff:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        target = user_stuff[-1] # Senaste bilden
        st.image(target["url"], caption="SENASTE SKAPELSEN", use_container_width=True)
        if st.button("🎬 ANIMERA TILL VIDEO (5 UNITS)", use_container_width=True):
            if st.session_state.user_units >= 5:
                with st.spinner("Luma Engine..."):
                    vid = replicate.run("luma-ai/luma-dream-machine", input={"image_url": target["url"]})
                    st.video(str(vid))
                    st.session_state.user_units -= 5
            else: st.error("Ladda units!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Skapa en bild i MAGI först.")

with tabs[2]: # ARKIV (Häftiga Bakgrunder)
    st.markdown("### 🖼️ DITT ARKIV")
    my_stuff = [p for p in st.session_state.gallery if p["u"] == artist]
    for i, item in enumerate(reversed(my_stuff)):
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.image(item["url"], use_container_width=True)
        if st.button("🖼️ SÄTT SOM STUDIO-BG", key=f"bg_{i}"):
            st.session_state.app_bg = item["url"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Osynlig logg längst ner (för felsökning)
if artist == "TOMAS2026":
    with st.expander("KERNEL_LOGS"):
        st.write(st.session_state.get("action_logs", []))


