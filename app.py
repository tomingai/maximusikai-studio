import streamlit as st
import os
import requests
import time
import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", page_icon="🎵", layout="wide")

if "gallery" not in st.session_state:
    st.session_state.gallery = []
if "community_feed" not in st.session_state:
    st.session_state.community_feed = []

# --- 2. DEN ULTIMATA NEON-DESIGNEN ---
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
    
    /* --- FIX: TEXT OVANFÖR RUTOR (LABELS) --- */
    /* Detta gör att texten "VAD SKALL VI SKAPA" syns tydligt */
    .stWidget label p, label, .stMarkdown p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.5) !important;
        font-size: 16px !important;
    }

    /* --- FIX: FLIKARNA (TABS) --- */
    div[data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 10px !important;
        border-radius: 15px !important;
        gap: 20px !important;
    }
    button[data-baseweb="tab"] div p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 26px !important;
        text-shadow: 0 0 15px rgba(255,255,255,1) !important;
        text-transform: uppercase !important;
    }
    button[aria-selected="true"] div p {
        color: #bf00ff !important;
        text-shadow: 0 0 25px #bf00ff !important;
    }

    /* Titeln */
    .neon-container {
        background: rgba(10, 10, 10, 0.85);
        padding: 40px; border-radius: 30px; 
        border: 2px solid rgba(191, 0, 255, 0.6);
        box-shadow: 0px 0px 60px rgba(191, 0, 255, 0.3);
        text-align: center; margin-bottom: 40px;
        backdrop-filter: blur(15px);
    }
    .neon-title { 
        font-family: 'Arial Black', sans-serif; font-size: 80px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 40px #bf00ff; margin: 0; 
    }

    /* Knappar */
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

# --- 3. MOTOR & LOGIK ---
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, vfx
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        import moviepy.video.fx.all as vfx
    except:
        st.error("Laddar motorer...")

def get_url(output):
    if isinstance(output, list): return str(output[0])
    if hasattr(output, 'url'): return str(output.url)
    return str(output)

# API-KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    import replicate
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    api_ready = True
else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
    api_ready = False

# --- 4. FLIKAR ---
if api_ready:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 BIBLIOTEK", "🌐 COMMUNITY"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            proj_name = st.text_input("PROJEKTETS NAMN:", f"MAXI-{len(st.session_state.gallery)+1}")
            m_ide = st.text_area("VAD SKALL VI SKAPA IDAG?", "En cyberpunk-stad i neon-lila regn")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("🏗️ MAXIMUSIKAI BYGGER...") as status:
                    try:
                        # AI-stegen
                        img_raw = replicate.run("black-forest-labs/flux-schnell", input={"prompt": m_ide, "aspect_ratio": "16:9"})
                        img_url = get_url(img_raw)
                        
                        lyrics_res = replicate.run("meta/llama-2-70b-chat", input={"prompt": f"Write 4 short lines about: {m_ide}. ONLY lyrics.", "max_new_tokens": 100})
                        lyrics = "".join(lyrics_res).replace('"', '').strip()
                        
                        v_url = get_url(replicate.run("minimax/video-01", input={"prompt": "Cinematic movement", "first_frame_image": img_url}))
                        
                        entry = {"name": proj_name, "video": v_url, "lyrics": lyrics, "time": datetime.datetime.now().strftime("%H:%M")}
                        st.session_state.gallery.append(entry)
                        
                        status.update(label="✅ PRODUKTION KLAR!", state="complete")
                        with c2:
                            st.video(v_url)
                            st.markdown(f"<div style='padding:15px; border-left:5px solid #bf00ff; background:rgba(0,0,0,0.5);'>{lyrics}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Fel: {e}")

    with tab4:
        st.subheader("DITT ARKIV")
        for item in reversed(st.session_state.gallery):
            with st.expander(f"📁 {item['name']} ({item['time']})"):
                st.video(item['video'])
                st.write(item['lyrics'])

    with tab5:
        st.markdown("<h2 style='text-align:center; color:#bf00ff;'>🌐 COMMUNITY HUB</h2>", unsafe_allow_html=True)
        if st.button("DELA SENASTE PROJEKTET"):
            if st.session_state.gallery:
                st.session_state.community_feed.append(st.session_state.gallery[-1])
                st.success("Publicerat i communityt!")
        for post in reversed(st.session_state.community_feed):
            st.divider()
            st.video(post['video'])

st.markdown("<br><center><small>MAXIMUSIKAI // 2024</small></center>", unsafe_allow_html=True)



