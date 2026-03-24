import streamlit as st
import replicate
import os
import time

# --- 1. SETUP & DESIGN (STABIL PRO-LOOK) ---
st.set_page_config(page_title="MAXIMUSIKAI PRO", layout="wide")

st.markdown("""
    <style>
    /* Hela appen och sidomenyn */
    .stApp, [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important;
        color: white !important;
    }
    
    /* FIX: TEXT OVANFÖR RUTOR OCH I SIDOMENY */
    .stWidget label p, label, [data-testid="stSidebar"] .stMarkdown p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.5) !important;
        font-size: 16px !important;
    }
    
    /* INPUT-FÄLT */
    input, textarea {
        background-color: rgba(191, 0, 255, 0.05) !important;
        border: 1px solid #bf00ff !important;
        color: #bf00ff !important;
        font-weight: bold !important;
    }

    /* FLIKARNA (TABS) - KRITVITA */
    div[data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 10px !important;
        border-radius: 15px !important;
    }
    button[data-baseweb="tab"] div p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 24px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.8);
        text-transform: uppercase;
    }
    button[aria-selected="true"] div p {
        color: #bf00ff !important;
        text-shadow: 0 0 20px #bf00ff;
    }

    /* TITEL-CONTAINER */
    .neon-container {
        background: rgba(10, 10, 10, 0.85);
        padding: 30px; border-radius: 25px; 
        border: 2px solid rgba(191, 0, 255, 0.6);
        box-shadow: 0px 0px 60px rgba(191, 0, 255, 0.3);
        text-align: center; margin-bottom: 30px;
        backdrop-filter: blur(15px);
    }
    .neon-title { 
        font-family: 'Arial Black', sans-serif; font-size: 60px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 40px #bf00ff; margin: 0; 
    }
    
    /* KNAPPAR */
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

# API KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    
    # SIDOMENY
    with st.sidebar:
        st.markdown("### 👤 ARTISTPROFIL")
        artist = st.text_input("ARTISTNAMN:", "ANONYM")
        st.divider()
        st.markdown("### 🎨 MOOD-PRESETS")
        mood = st.radio("VÄLJ STIL:", ["Cyberpunk", "Retro VHS", "Lo-fi Dreams"])

    tab1, tab2, tab3 = st.tabs(["🪄 TOTAL MAGI", "📚 BIBLIOTEK", "🌐 COMMUNITY"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA IDAG?", f"En scen i {mood}-stil")
            btn = st.button("🚀 STARTA PRODUKTION")

        if btn:
            with st.status("🏗️ MAXIMUSIKAI BYGGER...") as status:
                try:
                    # 1. Bild
                    status.write("🎨 Skapar bild...")
                    img_output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                    img_url = img_output[0] if isinstance(img_output, list) else img_output
                    
                    # Paus för rate limit
                    time.sleep(10)
                    
                    # 2. Video
                    status.write("📽️ Animerar scenen...")
                    video_url = replicate.run("minimax/video-01", input={"prompt": "Cinematic movement", "first_frame_image": img_url})
                    
                    status.update(label="✅ KLART!", state="complete")
                    with c2:
                        st.video(video_url)
                        st.success(f"Skapad av {artist}")
                except Exception as e:
                    st.error(f"Fel: {e}")
else:
    st.error("Gå till Settings -> Secrets och lägg till din REPLICATE_API_TOKEN!")

st.markdown("<br><center><small>MAXIMUSIKAI // 2024</small></center>", unsafe_allow_html=True)





