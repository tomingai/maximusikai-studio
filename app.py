import streamlit as st
import replicate
import os
import time
import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI SPEED PRO", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state:
    st.session_state.gallery = []

# --- 2. AGGRESSIV NEON-DESIGN (LILA & VIT) ---
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
    
    /* FIX: EXTRA TYDLIGA LABELS OCH TEXT */
    .stWidget label p, label, .stMarkdown p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.5) !important;
        font-size: 16px !important;
    }

    /* FIX: KRITVITA OCH STORA FLIKAR */
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

    /* NEON-TITEL */
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

st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p><p style="color:#bf00ff; letter-spacing: 5px; font-weight:bold;">⚡ SPEED PRO EDITION</p></div>', unsafe_allow_html=True)

# HJÄLPFUNKTION
def get_url(output):
    if isinstance(output, list): return str(output[0])
    if hasattr(output, 'url'): return str(output.url)
    return str(output)

# API-KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    api_ready = True
else:
    st.error("Gå till Settings -> Secrets och lägg till din REPLICATE_API_TOKEN!")
    api_ready = False

# --- 3. HUVUDAPPEN ---
if api_ready:
    tab1, tab2, tab3 = st.tabs(["⚡ SNABB PRODUKTION", "📚 BIBLIOTEK", "🌐 COMMUNITY"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            proj_name = st.text_input("PROJEKTNAMN:", f"SPEED-{len(st.session_state.gallery)+1}")
            m_ide = st.text_area("VAD SKALL VI SKAPA?", "En futuristisk stad i neon")
            if st.button("🚀 STARTA SNABB PRODUKTION"):
                with st.status("⚡ MAXI-SPEED MOTORN ARBETAR...") as status:
                    try:
                        # 1. BILD (Flux Schnell - Blixtsnabb)
                        status.write("🎨 Skapar bild blixtsnabbt...")
                        img_output = replicate.run(
                            "black-forest-labs/flux-schnell", 
                            input={"prompt": m_ide, "aspect_ratio": "16:9"}
                        )
                        img_url = get_url(img_output)
                        st.image(img_url, caption="Genererad Scen")
                        
                        # Paus för rate limit (kortare paus tack vare snabbare modell)
                        time.sleep(6)
                        
                        # 2. VIDEO (Luma Dream Machine - Snabbare än Minimax)
                        status.write("📽️ Animerar med Speed-modul...")
                        video_output = replicate.run(
                            "luma-ai/luma-dream-machine", 
                            input={"prompt": "Cinematic slow zoom movement", "image_url": img_url}
                        )
                        video_url = get_url(video_output)
                        
                        # Spara i Session (Bibliotek)
                        st.session_state.gallery.append({
                            "name": proj_name,
                            "video": video_url,
                            "time": datetime.datetime.now().strftime("%H:%M")
                        })
                        
                        status.update(label="✅ MÄSTERVERKET ÄR KLART!", state="complete")
                        with c2:
                            st.video(video_url)
                            st.success(f"Projektet '{proj_name}' är sparat i biblioteket!")
                    except Exception as e:
                        st.error(f"Fel vid snabbkörning: {e}")

    with tab2:
        st.subheader("Dina skapelser")
        for item in reversed(st.session_state.gallery):
            with st.expander(f"📁 {item['name']} ({item['time']})"):
                st.video(item['video'])

st.markdown("<br><center><small>MAXIMUSIKAI SPEED PRO // 2024</small></center>", unsafe_allow_html=True)






