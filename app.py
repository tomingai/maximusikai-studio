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

# --- 2. DEN STORA DESIGN-MOTORN ---
st.markdown("""
    <style>
    .stApp, [data-testid="stSidebar"] { background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }
    [data-testid="stSidebar"] .stMarkdown h3, [data-testid="stSidebar"] label p { color: #bf00ff !important; font-weight: 900 !important; text-transform: uppercase; font-size: 16px !important; text-shadow: 0 0 10px rgba(191, 0, 255, 0.5); }
    [data-testid="stSidebar"] input { color: #bf00ff !important; background-color: rgba(191, 0, 255, 0.05) !important; border: 1px solid #bf00ff !important; }
    div[data-baseweb="tab-list"] { background-color: rgba(255, 255, 255, 0.05) !important; padding: 10px !important; border-radius: 15px !important; }
    button[data-baseweb="tab"] div p { color: #FFFFFF !important; font-weight: 900 !important; font-size: 24px !important; text-transform: uppercase; }
    button[aria-selected="true"] div p { color: #bf00ff !important; text-shadow: 0 0 15px #bf00ff; }
    .neon-container { background: rgba(10, 10, 10, 0.85); padding: 30px; border-radius: 25px; border: 2px solid rgba(191, 0, 255, 0.6); box-shadow: 0px 0px 40px rgba(191, 0, 255, 0.2); text-align: center; margin-bottom: 30px; }
    .neon-title { font-family: 'Arial Black', sans-serif; font-size: 60px; font-weight: 900; color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 30px #bf00ff; margin: 0; }
    .lyrics-overlay { background: rgba(0, 0, 0, 0.8); border: 1px solid #bf00ff; padding: 15px; border-radius: 10px; color: #fff; font-family: 'Courier New', monospace; text-align: center; margin-top: 10px; box-shadow: 0 0 15px rgba(191, 0, 255, 0.4); }
    .stButton>button { background: rgba(191, 0, 255, 0.1); color: #bf00ff; border: 2px solid #bf00ff; width: 100%; font-weight: bold; border-radius: 12px; height: 3.5em; text-transform: uppercase; }
    .stButton>button:hover { background: #bf00ff; color: #000; box-shadow: 0px 0px 40px #bf00ff; }
    </style>
""", unsafe_allow_html=True)

# TITEL MED DITT NAMN
st.markdown("""
<div class="neon-container">
    <p class="neon-title">MAXIMUSIKAI</p>
    <p style="color:#bf00ff; letter-spacing: 3px; font-size: 14px; margin-top: -10px;">
        ENGINEERED BY <span style="color:#fff; font-weight:bold;">TOMAS INGVARSSON</span>
    </p>
</div>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown("### 👤 ARTIST")
    artist_name = st.text_input("DITT NAMN:", "ANONYM ARTIST")
    st.divider()
    st.markdown("### 🎨 STIL-PRESET")
    mood = st.radio("VÄLJ MOOD:", ["Cyberpunk", "Retro VHS", "Lo-fi Dreams", "Dark Techno"])

# --- 4. HUVUDAPPEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 ARKIV", "🌐 COMMUNITY"])

    with tab1: # --- TOTAL MAGI ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", f"En scen i {mood}-stil")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("🏗️ BYGGER...") as status:
                    try:
                        img_output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                        img_url = str(img_output)
                        time.sleep(10)
                        lyrics_res = replicate.run("meta/llama-2-70b-chat", input={"prompt": f"Write 2 short rhyming lines about {m_ide}. ONLY lyrics."})
                        lyrics = "".join(lyrics_res).replace('"', '').strip()
                        time.sleep(10)
                        mu_output = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood} music", "duration": 8})
                        video_output = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": img_url})
                        
                        entry = {"id": time.time(), "name": m_ide[:20], "video": str(video_output), "audio": str(mu_output), "lyrics": lyrics, "time": datetime.datetime.now().strftime("%H:%M")}
                        st.session_state.gallery.append(entry)
                        with c2:
                            st.video(str(video_output))
                            st.markdown(f'<div class="lyrics-overlay">🎵 {lyrics}</div>', unsafe_allow_html=True)
                            st.audio(str(mu_output))
                        status.update(label="✅ KLART!", state="complete")
                    except Exception as e: st.error(f"Fel: {e}")

    with tab2: # --- REGISSÖREN ---
        up_file = st.file_uploader("LADDA UPP BILD:", type=["jpg", "png", "jpeg"])
        if up_file and st.button("⚡ ANIMERA BILD"):
            with st.status("📽️ Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Slow cinematic zoom", "image_url": up_file})
                st.video(str(res))

    with tab3: # --- BARA MUSIK + SVENSK RÖST ---
        mu_ide = st.text_input("BESKRIV MUSIKEN:", f"{mood} beat")
        intro_text = st.text_input("VAD SKALL RÖSTEN SÄGA?", f"Här kommer en ny hit från {artist_name}")
        if st.button("🎵 GENERERA MED INTRO"):
            with st.status("🎙️ Skapar röst & 🎸 Musik...") as status:
                voice_res = replicate.run("openai/tts-1", input={"text": intro_text, "voice": "alloy"})
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_ide, "duration": 10})
                st.write("🎙️ **Röst-Intro:**"); st.audio(str(voice_res))
                st.write("🎸 **Ditt Beat:**"); st.audio(str(mu_res))

    with tab4: # --- ARKIV ---
        if not st.session_state.gallery: st.info("Arkivet är tomt.")
        else:
            for item in reversed(st.session_state.gallery):
                with st.expander(f"📁 {item['name']} ({item['time']})"):
                    st.video(item['video']); st.audio(item['audio'])
                    c_dl1, c_dl2, c_del = st.columns(3)
                    with c_dl1: st.download_button("💾 VIDEO", requests.get(item['video']).content, file_name="vid.mp4", key=f"v_{item['id']}")
                    with c_dl2: st.download_button("🎵 LJUD", requests.get(item['audio']).content, file_name="aud.mp3", key=f"a_{item['id']}")
                    with c_del:
                        if st.button("🗑️ RADERA", key=f"del_{item['id']}"):
                            st.session_state.gallery = [x for x in st.session_state.gallery if x['id'] != item['id']]; st.rerun()

    with tab5: # --- COMMUNITY ---
        st.markdown(f"<p style='text-align:center; color:#aaa; font-style:italic;'>Community System Engineered by Tomas Ingvarsson</p>", unsafe_allow_html=True)
        if st.button("DELA SENASTE"):
            if st.session_state.gallery: st.session_state.community_feed.append(st.session_state.gallery[-1]); st.success("Delad!")
        for post in reversed(st.session_state.community_feed):
            st.divider(); st.video(post['video']); st.caption(f"Artist: {artist_name}")

else: st.error("⚠️ REPLICATE_API_TOKEN saknas!")

# FOOTER MED DITT NAMN
st.markdown(f"<br><center><small>MAXIMUSIKAI SPEED PRO // 2026 // CREATED BY <b>TOMAS INGVARSSON</b></small></center>", unsafe_allow_html=True)










