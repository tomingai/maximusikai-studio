import streamlit as st
import replicate
import os
import requests
import time
import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "community_feed" not in st.session_state: st.session_state.community_feed = []

# --- 2. DEN STORA DESIGN-MOTORN (2026 STUDIO EDITION) ---
st.markdown("""
    <style>
    .stApp, [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important;
        color: white !important;
    }
    
    /* SIDOMENY - NEON LILA */
    [data-testid="stSidebar"] .stMarkdown h3, [data-testid="stSidebar"] label p {
        color: #bf00ff !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        font-size: 16px !important;
        text-shadow: 0 0 10px rgba(191, 0, 255, 0.5);
    }
    
    [data-testid="stSidebar"] input {
        color: #bf00ff !important;
        background-color: rgba(191, 0, 255, 0.05) !important;
        border: 1px solid #bf00ff !important;
    }

    /* FLIKARNA - KRITVITA & STORA */
    div[data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 10px !important;
        border-radius: 15px !important;
    }
    button[data-baseweb="tab"] div p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 24px !important;
        text-transform: uppercase;
    }
    button[aria-selected="true"] div p {
        color: #bf00ff !important;
        text-shadow: 0 0 15px #bf00ff;
    }

    /* TITEL & CONTAINERS */
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

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown("### 👤 ARTIST")
    artist_name = st.text_input("DITT NAMN:", "ANONYM ARTIST")
    st.divider()
    st.markdown("### 🎨 STIL")
    mood = st.radio("VÄLJ MOOD:", ["Cyberpunk", "Retro VHS", "Lo-fi Dreams", "Dark Techno"])

# --- 4. HUVUDAPPEN ---
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
                        status.write("🎨 Skapar bild...")
                        img_output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                        img_url = img_output if isinstance(img_output, str) else img_output
                        time.sleep(6)
                        
                        status.write("🎵 Komponerar musik...")
                        mu_output = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood} melodic music", "duration": 8})
                        mu_url = str(mu_output)
                        time.sleep(6)

                        status.write("📽️ Animerar video...")
                        video_output = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic movement", "image_url": img_url})
                        video_url = str(video_output)
                        
                        # Spara i arkivet
                        st.session_state.gallery.append({
                            "id": time.time(),
                            "name": m_ide[:20], 
                            "video": video_url, 
                            "audio": mu_url,
                            "time": datetime.datetime.now().strftime("%H:%M")
                        })
                        status.update(label="✅ KLART!", state="complete")
                        with c2: 
                            st.video(video_url)
                            st.audio(mu_url)
                    except Exception as e: st.error(f"Fel: {e}")

    # --- FLIK 4: ARKIV (UPPGRADERAD MED MP3) ---
    with tab4:
        st.subheader("📁 DINA SPARADE MÄSTERVERK")
        if not st.session_state.gallery:
            st.info("Arkivet är tomt. Skapa något i fliken TOTAL MAGI!")
        else:
            for i, item in enumerate(reversed(st.session_state.gallery)):
                with st.expander(f"PROJEKT: {item['name']} ({item['time']})"):
                    st.video(item['video'])
                    st.audio(item['audio'])
                    
                    col_dl1, col_dl2, col_del = st.columns(3)
                    with col_dl1:
                        v_resp = requests.get(item['video']).content
                        st.download_button("💾 VIDEO (MP4)", v_resp, file_name=f"video_{item['id']}.mp4", key=f"vdl_{item['id']}")
                    with col_dl2:
                        a_resp = requests.get(item['audio']).content
                        st.download_button("🎵 LJUD (MP3)", a_resp, file_name=f"audio_{item['id']}.mp3", key=f"adl_{item['id']}")
                    with col_del:
                        if st.button("🗑️ RADERA", key=f"del_{item['id']}"):
                            st.session_state.gallery = [x for x in st.session_state.gallery if x['id'] != item['id']]
                            st.rerun()

    # --- FLIK 5: COMMUNITY ---
    with tab5:
        st.markdown("### 🌐 COMMUNITY FEED")
        if st.button("DELA SENASTE SKAPELSEN"):
            if st.session_state.gallery: st.session_state.community_feed.append(st.session_state.gallery[-1])
            st.success("Publicerad!")
        for post in reversed(st.session_state.community_feed):
            st.divider()
            st.video(post['video'])
            st.audio(post['audio'])
            st.caption(f"Skapad av {artist_name}")

else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")

st.markdown("<br><center><small>MAXIMUSIKAI SPEED PRO // 2026</small></center>", unsafe_allow_html=True)










