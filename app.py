import streamlit as st
import replicate
import os
import requests
import time
import datetime

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", page_icon="🎬", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "community_feed" not in st.session_state: st.session_state.community_feed = []

st.markdown("""
    <style>
    .stApp { background: linear-gradient(125deg, #050505, #0a0a0a, #0b001a, #050505); background-size: 400% 400%; animation: gradientBG 15s ease infinite; color: #fff; }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stWidget label p, label, .stMarkdown p { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 2px !important; text-shadow: 0 0 10px rgba(255,255,255,0.5) !important; font-size: 16px !important; }
    div[data-baseweb="tab-list"] { background-color: rgba(255, 255, 255, 0.05) !important; padding: 10px !important; border-radius: 15px !important; gap: 20px !important; }
    button[data-baseweb="tab"] div p { color: #FFFFFF !important; font-weight: 900 !important; font-size: 26px !important; text-shadow: 0 0 15px rgba(255,255,255,1) !important; text-transform: uppercase !important; }
    button[aria-selected="true"] div p { color: #bf00ff !important; text-shadow: 0 0 25px #bf00ff !important; }
    .neon-container { background: rgba(10, 10, 10, 0.85); padding: 40px; border-radius: 30px; border: 2px solid rgba(191, 0, 255, 0.6); box-shadow: 0px 0px 60px rgba(191, 0, 255, 0.3); text-align: center; margin-bottom: 40px; backdrop-filter: blur(15px); }
    .neon-title { font-family: 'Arial Black', sans-serif; font-size: 80px; font-weight: 900; color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 40px #bf00ff; margin: 0; }
    .stButton>button { background: rgba(191, 0, 255, 0.1); color: #bf00ff; border: 2px solid #bf00ff; width: 100%; font-weight: bold; border-radius: 12px; height: 3.5em; text-transform: uppercase; }
    .stButton>button:hover { background: #bf00ff; color: #000; box-shadow: 0px 0px 40px #bf00ff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

# API-KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    api_ready = True
else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
    api_ready = False

if api_ready:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 BIBLIOTEK", "🌐 COMMUNITY"])

    # --- FLIK 1: TOTAL MAGI (Samma som förut) ---
    with tab1:
        st.write("Skapa allt från grunden med AI.")
        # ... (Här ligger din befintliga kod för flik 1)

    # --- FLIK 2: REGISSÖREN (UPPGRADERAD!) ---
    with tab2:
        col_r1, col_r2 = st.columns([1, 1.2])
        with col_r1:
            uploaded_file = st.file_uploader("LADDA UPP DIN SCEN (BILD):", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                st.image(uploaded_file, caption="Din uppladdade scen", use_container_width=True)
            
            st.divider()
            motion_type = st.selectbox("VÄLJ KAMERARÖRELSE:", [
                "Cinematic Slow Zoom", 
                "Pan Right to Left", 
                "Drone Flyover", 
                "Fast Action Push", 
                "Slow motion dream"
            ])
            
            r_btn = st.button("⚡ ANIMERA SCENEN")

        with col_r2:
            if r_btn and uploaded_file:
                with st.status("🎬 Regisserar din scen...") as status:
                    try:
                        # Animera bilden med Minimax
                        video_output = replicate.run(
                            "minimax/video-01",
                            input={
                                "prompt": f"{motion_type}, high quality, cinematic lighting",
                                "first_frame_image": uploaded_file
                            }
                        )
                        video_url = str(video_output)
                        
                        status.update(label="✅ Scenen är filmad!", state="complete")
                        st.video(video_url)
                        
                        # Möjlighet att spara till arkiv
                        if st.button("💾 SPARA I ARKIVET"):
                            st.session_state.gallery.append({
                                "name": f"Regi: {motion_type}",
                                "video": video_url,
                                "time": datetime.datetime.now().strftime("%H:%M"),
                                "lyrics": "Endast video (Regissören)"
                            })
                            st.success("Sparad!")
                            
                    except Exception as e:
                        st.error(f"Kameran hängde sig: {e}")
            elif r_btn and not uploaded_file:
                st.warning("Du måste ladda upp en bild först, Regissören!")

    # --- ÖVRIGA FLIKAR (Samma som förut) ---
    with tab4:
        for item in reversed(st.session_state.gallery):
            with st.expander(f"📁 {item['name']}"):
                st.video(item['video'])

st.markdown("<br><center><small>MAXIMUSIKAI // 2024</small></center>", unsafe_allow_html=True)




