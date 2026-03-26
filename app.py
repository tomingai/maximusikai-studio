import streamlit as st
import replicate
import os
import time
import json
import random
from datetime import datetime

# --- 1. CORE ENGINE & QUALITY CONTROL ---
st.set_page_config(page_title="MAXIMUSIKAI PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "units" not in st.session_state: st.session_state.units = 50

def enhance_result(user_prompt):
    """Denna funktion garanterar att resultatet ser proffsigt ut"""
    quality_boost = "hyper-realistic, 8k resolution, cinematic lighting, highly detailed, octane render, masterpiece, trending on artstation, sharp focus, vivid colors"
    return f"{user_prompt}, {quality_boost}"

# --- 2. THE ULTIMATE NEBULA UI (ANIMERAD & MOBIL-ANPASSAD) ---
def apply_2026_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* ANIMERAD RUMS-BAKGRUND */
        .stApp {
            background: linear-gradient(125deg, #000428, #004e92, #000428, #050505);
            background-size: 400% 400%;
            animation: nebulaFlow 20s ease infinite;
        }
        @keyframes nebulaFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

        /* SCANLINES / HOLOGRAM FILTER */
        .stApp::before {
            content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 255, 255, 0.02) 50%);
            background-size: 100% 4px; pointer-events: none; z-index: 1000;
        }

        /* MOBIL-OPTIMERADE KONTROLLER (GLASSMORPHISM) */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(25px) !important;
            border: 1px solid rgba(0, 242, 255, 0.3) !important;
            border-radius: 15px; padding: 20px;
        }

        /* KNAPPAR: TOUCH-VÄNLIGA & NEON */
        .stButton>button {
            background: transparent !important; color: #00f2ff !important;
            border: 1px solid #00f2ff !important; border-radius: 5px !important;
            font-family: 'Orbitron'; height: 60px !important; letter-spacing: 3px;
            width: 100%; transition: 0.4s;
        }
        .stButton>button:active { background: #00f2ff !important; color: black !important; box-shadow: 0 0 40px #00f2ff; }

        /* LOGO */
        .logo {
            font-family: 'Orbitron'; font-size: 2.8rem; text-align: center;
            color: #fff; letter-spacing: 8px; text-shadow: 0 0 20px #00f2ff;
            margin: 20px 0;
        }

        /* INPUTS */
        textarea, input {
            background-color: rgba(0,0,0,0.5) !important; color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.2) !important; font-family: 'JetBrains Mono';
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. STUDIO CORE ---
apply_2026_design()
st.markdown('<div class="logo">MAXIMUSIKAI</div>', unsafe_allow_html=True)

# HUD (Statusrad)
c1, c2 = st.columns(2)
with c1: st.write(f"📡 CORE: ACTIVE")
with c2: st.markdown(f"<p style='text-align:right;'>⚡ UNITS: {st.session_state.units}</p>", unsafe_allow_html=True)

# --- 4. COMMAND CENTER (INPUT) ---
st.markdown("### 🪄 NEURAL SYNTHESIS")
prompt = st.text_area("BESKRIV DIN VISION", placeholder="T.ex. En futuristisk stad i regn...", height=120)

col_gen, col_opt = st.columns([2,1])
with col_opt:
    ratio = st.selectbox("FORMAT", ["9:16 (MOBIL)", "1:1 (SQUARE)", "16:9 (WIDE)"])
    map_ratio = {"9:16 (MOBIL)": "9:16", "1:1 (SQUARE)": "1:1", "16:9 (WIDE)": "16:9"}

if col_gen.button("🔥 EXECUTE SYNTHESIS", use_container_width=True):
    if prompt and st.session_state.units > 0:
        with st.status("Linking to AI Cores...") as status:
            try:
                # Förstärk prompten för maxat resultat
                final_prompt = enhance_result(prompt)
                status.write("Optimizing Prompt for 2026 Graphics...")
                
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                
                # BILD-GENERERING (Flux Schnell)
                res = replicate.run("black-forest-labs/flux-schnell", 
                                   input={"prompt": final_prompt, "aspect_ratio": map_ratio[ratio]})
                
                img_url = str(res[0]) if isinstance(res, list) else str(res)
                st.session_state.gallery.append(img_url)
                st.session_state.units -= 1
                
                st.image(img_url, use_container_width=True, caption="RESULTAT: NEURAL SYNC COMPLETE")
                status.update(label="SYNTHESIS COMPLETE", state="complete")
            except Exception as e:
                st.error(f"SYSTEM ERROR: {e}")
    else:
        st.warning("SKRIV EN PROMPT OCH KOLLA DINA UNITS.")

# --- 5. DATA VAULT (ARKIV) ---
if st.session_state.gallery:
    st.divider()
    st.markdown("### 📚 DITT ARKIV")
    cols = st.columns(2) # Bra för mobilscroll
    for idx, img in enumerate(reversed(st.session_state.gallery)):
        with cols[idx % 2]:
            st.image(img, use_container_width=True)
            if st.button(f"LADDA NER #{idx}", key=f"dl_{idx}"):
                st.write("Håll ner fingret på bilden för att spara!")

st.caption(f"MAXIMUSIKAI STUDIO PRO v4.2 | 2026.03.26")

