import streamlit as st
import replicate
import os
import time

# --- DESIGN & SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050505; color: white; }
    .neon-title { font-family: 'Arial Black'; font-size: 60px; color: #fff; text-shadow: 0 0 20px #bf00ff; text-align: center; }
    /* Ljus lila text för labels */
    label p { color: #bf00ff !important; font-weight: bold; text-transform: uppercase; }
    /* Vita flikar */
    .stTabs [data-baseweb="tab"] p { color: white !important; font-size: 20px !important; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">MAXIMUSIKAI</h1>', unsafe_allow_html=True)

# API KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    
    tab1, tab2, tab3 = st.tabs(["🪄 TOTAL MAGI", "📚 ARKIV", "🌐 COMMUNITY"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            m_ide = st.text_input("VAD SKALL VI SKAPA?", "En neonstad")
            start_btn = st.button("🚀 STARTA PRODUKTION")

        if start_btn:
            with st.status("🏗️ MAXI-MOTORN ARBETAR...") as status:
                try:
                    # STEG 1: BILD
                    status.write("🎨 Skapar bild...")
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": m_ide})
                    img_url = img[0] if isinstance(img, list) else img
                    st.image(img_url)
                    
                    # STEG 2: VIDEO (Denna tar tid, vi visar URL direkt för att undvika "snurr")
                    status.write("📽️ Animerar (detta kan ta 30-60 sek)...")
                    video_output = replicate.run("minimax/video-01", input={"prompt": "Cinematic", "first_frame_image": img_url})
                    
                    with col2:
                        st.video(video_output)
                        st.success("Produktion klar!")
                except Exception as e:
                    st.error(f"Ett fel uppstod: {e}")
else:
    st.error("Lägg till REPLICATE_API_TOKEN i Secrets!")



