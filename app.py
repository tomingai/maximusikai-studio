import streamlit as st
import sys
import os

# --- AKUT-FIX FÖR PYDANTIC / PYTHON 3.14 FELET ---
try:
    from pydantic.v1 import fields
    if not hasattr(fields.ModelField, '_type_display'):
        fields.ModelField._type_display = lambda x: str(x)
except Exception:
    pass

import replicate
import requests
import time
from moviepy.editor import VideoFileClip, AudioFileClip, vfx
import datetime

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", page_icon="🎵", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(125deg, #050505, #0a0a0a, #0b001a, #050505);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #fff;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stTabs [data-baseweb="tab"] p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 22px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.6);
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] p {
        color: #bf00ff !important;
        text-shadow: 0 0 20px #bf00ff;
    }
    .neon-container {
        background: rgba(10, 10, 10, 0.85);
        padding: 40px; border-radius: 30px; 
        border: 2px solid rgba(191, 0, 255, 0.5);
        box-shadow: 0px 0px 60px rgba(191, 0, 255, 0.2);
        text-align: center; margin-bottom: 40px;
        backdrop-filter: blur(15px);
    }
    .neon-title { 
        font-family: 'Arial Black', sans-serif; font-size: 75px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 40px #bf00ff; margin: 0; 
    }
    .stButton>button {
        background: rgba(191, 0, 255, 0.1); color: #bf00ff; 
        border: 2px solid #bf00ff; width: 100%; font-weight: bold; 
        border-radius: 12px; height: 3.5em; text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #bf00ff; color: #000; box-shadow: 0px 0px 40px #bf00ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

def get_url(output):
    if isinstance(output, list): return str(output[0])
    if hasattr(output, 'url'): return str(output.url)
    return str(output)

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    api_ready = True
else:
    st.warning("Vänligen lägg till din REPLICATE_API_TOKEN i Secrets.")
    api_ready = False

if api_ready:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 BIBLIOTEK", "🌐 COMMUNITY"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA IDAG?", "En futuristisk cyberpunk-stad i neon-lila regn")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("🏗️ MAXIMUSIKAI BYGGER...") as status:
                    try:
                        img_raw = replicate.run("black-forest-labs/flux-schnell", input={"prompt": m_ide, "aspect_ratio": "16:9"})
                        img_url = get_url(img_raw)
                        time.sleep(2)
                        lyrics_res = replicate.run("meta/llama-2-70b-chat", input={"prompt": f"Write 4 lines about: {m_ide}. ONLY lyrics.", "max_new_tokens": 100})
                        lyrics = "".join(lyrics_res).replace('"', '').strip()
                        v_url = get_url(replicate.run("minimax/video-01", input={"prompt": "Cinematic", "first_frame_image": img_url}))
                        status.update(label="✅ KLART!", state="complete")
                        with c2:
                            st.video(v_url)
                            st.markdown(f"<div style='padding:15px; border-left:5px solid #bf00ff;'>{lyrics}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Fel: {e}")

    with tab5:
        st.markdown("<h2 style='text-align:center; color:#bf00ff;'>🌐 COMMUNITY HUB</h2>", unsafe_allow_html=True)
        st.info("Här delar vi allas musik när databasen är på plats!")

st.markdown("<br><center><small>MAXIMUSIKAI // 2024</small></center>", unsafe_allow_html=True)


