import streamlit as st
import replicate
import os
import requests
import time
from moviepy.editor import VideoFileClip, AudioFileClip, vfx
import datetime

# --- 1. SETUP & DESIGN (EXTRA TYDLIGA FLIKAR) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", page_icon="🎵", layout="wide")

st.markdown("""
    <style>
    /* Bakgrunds-animation */
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

    /* FIX FÖR FLIKAR: KRITVIT TEXT SOM SYNS TYDLIGT */
    .stTabs [data-baseweb="tab"] p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 22px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.6);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stTabs [aria-selected="true"] p {
        color: #bf00ff !important;
        text-shadow: 0 0 20px #bf00ff;
    }

    /* Neon-behållare för titeln */
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

    /* Snyggare knappar */
    .stButton>button {
        background: rgba(191, 0, 255, 0.1); color: #bf00ff; 
        border: 2px solid #bf00ff; width: 100%; font-weight: bold; 
        border-radius: 12px; height: 3.5em; text-transform: uppercase;
        transition: 0.4s;
    }
    .stButton>button:hover {
        background: #bf00ff; color: #000; box-shadow: 0px 0px 40px #bf00ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p><p style="color:#bf00ff; letter-spacing: 5px;">AI MUSIC & VIDEO STUDIO</p></div>', unsafe_allow_html=True)

# HJÄLPFUNKTION FÖR URL
def get_url(output):
    if isinstance(output, list): return str(output[0])
    if hasattr(output, 'url'): return str(output.url)
    return str(output)

# API-KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    api_ready = True
else:
    st.warning("Vänligen lägg till din REPLICATE_API_TOKEN i Secrets.")
    api_ready = False

# --- 2. HUVUDMENY ---
if api_ready:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 MITT ARKIV", "🌐 COMMUNITY"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKA VI SKAPA IDAG?", "En futuristisk cyberpunk-stad i neon-lila regn")
            m_stil = st.selectbox("STIL:", ["Cyberpunk", "Cinematic", "Anime", "Vintage 8mm"])
            
            if st.button("🚀 STARTA FULL MAXI-PRODUKTION"):
                with st.status("🏗️ MAXIMUSIKAI BYGGER...") as status:
                    try:
                        # 1. Bild
                        img_raw = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {m_stil} style", "aspect_ratio": "16:9"})
                        img_url = get_url(img_raw)
                        time.sleep(5)
                        
                        # 2. Text
                        lyrics_res = replicate.run("meta/llama-2-70b-chat", input={"prompt": f"Write 4 short rhyming lines about: {m_ide}. ONLY lyrics."})
                        lyrics = "".join(lyrics_res).replace('"', '').strip()
                        time.sleep(5)
                        
                        # 3. Video
                        v_url = get_url(replicate.run("minimax/video-01", input={"prompt": "Cinematic movement", "first_frame_image": img_url}))
                        
                        status.update(label="✅ PRODUKTION KLAR!", state="complete")
                        with c2:
                            st.video(v_url)
                            st.markdown(f"<div style='background:rgba(20,20,20,0.8); padding:15px; border-left:5px solid #bf00ff;'>{lyrics}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Ett fel uppstod: {e}")

    with tab5:
        st.markdown("<h2 style='text-align:center; color:#bf00ff;'>🌐 COMMUNITY HUB</h2>", unsafe_allow_html=True)
        st.info("Koppla Supabase i framtiden för att se allas musik här!")

st.markdown("<br><center><small>MAXIMUSIKAI // 2024</small></center>", unsafe_allow_html=True)

