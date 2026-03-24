import streamlit as st
import replicate
import os
import requests
import time
from moviepy.editor import VideoFileClip, AudioFileClip, vfx

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", page_icon="🎵", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(125deg, #050505, #0a0a0a, #0b001a, #050505);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
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
        font-family: 'Arial Black', sans-serif; font-size: 70px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 40px #bf00ff; margin: 0; 
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 BIBLIOTEK", "🌐 COMMUNITY"])
    
    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", "Cyberpunk stad i neon")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("🏗️ MAXIMUSIKAI arbetar..."):
                    img_raw = replicate.run("black-forest-labs/flux-schnell", input={"prompt": m_ide, "aspect_ratio": "16:9"})
                    st.image(get_url(img_raw))
                    st.success("Nu kör vi! Python 3.11 fungerar!")
else:
    st.error("Lägg till din API-token i Secrets!")


