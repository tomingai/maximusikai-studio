import streamlit as st
import replicate
import os
import time
import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI SPEED PRO", page_icon="⚡", layout="wide")

# Initiera listor för att undvika tomma flikar
if "gallery" not in st.session_state: st.session_state.gallery = []
if "community_feed" not in st.session_state: st.session_state.community_feed = []

# --- 2. DEN STORA DESIGN-MOTORN (TVINGA FRAM SYNLIGHET) ---
st.markdown("""
    <style>
    /* Bakgrund */
    .stApp, [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important;
        color: white !important;
    }
    
    /* FIXA SYNLIGHET I SIDOMENYN */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label p {
        color: #bf00ff !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        font-size: 14px !important;
    }

    /* FIXA FLIKARNA (TABS) - KRITVITA */
    div[data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 10px !important;
        border-radius: 15px !important;
    }
    button[data-baseweb="tab"] div p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 22px !important;
        text-transform: uppercase;
    }
    button[aria-selected="true"] div p {
        color: #bf00ff !important;
        text-shadow: 0 0 15px #bf00ff;
    }

    /* TITEL-CONTAINER */
    .neon-container {
        background: rgba(10, 10, 10, 0.85);
        padding: 30px; border-radius: 25px; 
        border: 2px solid rgba(191, 0, 255, 0.6);
        box-shadow: 0px 0px 40px rgba(191, 0, 255, 0.2);
        text-align: center; margin-bottom: 30px;
    }
    .neon-title { 
        font-family: 'Arial Black', sans-serif; font-size: 60px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 30px #bf00ff; margin: 0; 
    }
    
    /* LABELS OCH TEXT */
    label p, .stMarkdown p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# TITEL (Alltid synlig)
st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

# --- 3. SIDOMENY (TVINGA FRAM) ---
with st.sidebar:
    st.markdown("### 👤 ARTIST")
    artist_name = st.text_input("DITT NAMN:", "ANONYM ARTIST")
    st.divider()
    st.markdown("### 🎨 STIL")
    mood = st.radio("VÄLJ MOOD:", ["Cyberpunk", "Retro VHS", "Lo-fi Dreams"])

# --- 4. HUVUDAPPEN (KOLLA API) ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 ARKIV", "🌐 COMMUNITY"])

    # --- FLIK 1: TOTAL MAGI ---
    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA IDAG?", f"En scen i {mood}-stil")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("🏗️ MAXIMUSIKAI BYGGER...") as status:
                    try:
                        # BILD
                        status.write("🎨 Skapar bild...")
                        img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                        img_url = img[0] if isinstance(img, list) else img
                        
                        # PAUS
                        time.sleep(6)
                        
                        # VIDEO
                        status.write("📽️ Animerar...")
                        video_url = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic movement", "image_url": img_url})
                        
                        # SPARA
                        st.session_state.gallery.append({"name": m_ide[:20], "video": video_url, "time": datetime.datetime.now().strftime("%H:%M")})
                        
                        status.update(label="✅ KLART!", state="complete")
                        with c2: st.video(video_url)
                    except Exception as e: st.error(f"Ett fel uppstod: {e}")

    # --- FLIK 2: REGISSÖREN ---
    with tab2:
        up_file = st.file_uploader("LADDA UPP BILD:", type=["jpg", "png", "jpeg"])
        if up_file and st.button("⚡ ANIMERA DIN BILD"):
            with st.spinner("Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Slow cinematic zoom", "image_url": up_file})
                st.video(res)

    # --- FLIK 3: BARA MUSIK ---
    with tab3:
        mu_ide = st.text_input("BESKRIV MUSIKEN:", "Cyberpunk techno beat")
        if st.button("🎵 SKAPA LJUD"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_ide, "duration": 8})
                st.audio(mu_res)

    # --- FLIK 4: ARKIV ---
    with tab4:
        for item in reversed(st.session_state.gallery):
            with st.expander(f"📁 {item['name']} ({item['time']})"):
                st.video(item['video'])

    # --- FLIK 5: COMMUNITY ---
    with tab5:
        st.markdown("### 🌐 COMMUNITY FEED")
        if st.button("DELA SENASTE"):
            if st.session_state.gallery: st.session_state.community_feed.append(st.session_state.gallery[-1])
        for post in reversed(st.session_state.community_feed):
            st.divider()
            st.video(post['video'])

else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Streamlit Secrets!")
    st.info("Gå till Manage app -> Settings -> Secrets och lägg till din nyckel.")

st.markdown("<br><center><small>MAXIMUSIKAI SPEED PRO // 2024</small></center>", unsafe_allow_html=True)








