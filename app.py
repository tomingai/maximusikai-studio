import streamlit as st
import replicate
import os
import requests
import time
import datetime
import json
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & PERSISTENCE ENGINE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

DB_FILE = "maximusikai_archive.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

if "gallery" not in st.session_state:
    st.session_state.gallery = load_data()
if "community_feed" not in st.session_state:
    st.session_state.community_feed = []

# --- 2. DESIGN-MOTORN ---
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

st.markdown("""
<div class="neon-container">
    <p class="neon-title">MAXIMUSIKAI</p>
    <p style="color:#bf00ff; letter-spacing: 5px; font-size: 14px; margin-top: -10px; opacity: 0.8;">
        ULTIMATE PRODUCTION STUDIO PRO
    </p>
</div>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown("""
        <div style="background: rgba(191, 0, 255, 0.05); padding: 15px; border-radius: 15px; border: 1px solid rgba(191, 0, 255, 0.2); margin-bottom: 20px;">
            <p style="color:#bf00ff; font-weight:900; margin:0; font-size:12px; letter-spacing:1px;">STUDIO STATUS: <span style="color:#00ff00;">● ONLINE</span></p>
            <p style="color:#555; font-size:10px; margin:0;">ENGINEERED BY TOMAS INGVARSSON</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("👤 ARTIST"):
        artist_name = st.text_input("DITT NAMN:", "ANONYM ARTIST")
    
    st.divider()
    st.markdown("### 🎨 STIL-PRESET")
    mood = st.radio("VÄLJ MOOD:", ["Cyberpunk", "Retro VHS", "Lo-fi Dreams", "Dark Techno"])
    st.divider()
    st.info("MAXIMUSIKAI 2026.1.6 (PARALLEL ENGINE)")

# --- 4. HUVUDAPPEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 ARKIV", "🌐 COMMUNITY"])

    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", f"En scen i {mood}-stil")
            if st.button("🚀 STARTA PRODUKTION"):
                with st.status("🏗️ MULTI-ENGINE: Skapar bild, musik & text samtidigt...") as status:
                    try:
                        with ThreadPoolExecutor() as executor:
                            img_future = executor.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                            mu_future = executor.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music, high quality", "duration": 8})
                            ly_future = executor.submit(replicate.run, "meta/llama-2-70b-chat", input={"prompt": f"Write 2 short rhyming lines about {m_ide}. ONLY lyrics."})

                            img_url = str(img_future.result())
                            mu_url = str(mu_future.result())
                            lyrics = "".join(ly_future.result()).replace('"', '').strip()

                        status.update(label="🎬 Animerar video...")
                        video_output = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": img_url})
                        
                        entry = {"id": time.time(), "name": m_ide[:20], "video": str(video_output), "audio": mu_url, "lyrics": lyrics, "time": datetime.datetime.now().strftime("%H:%M")}
                        st.session_state.gallery.append(entry)
                        save_data(st.session_state.gallery)
                        
                        with c2:
                            st.video(str(video_output))
                            st.markdown(f'<div class="lyrics-overlay">🎵 {lyrics}</div>', unsafe_allow_html=True)
                            st.audio(mu_url)
                        status.update(label="✅ KLART!", state="complete")
                    except Exception as e: st.error(f"Fel: {e}")

    with tab2:
        up_file = st.file_uploader("LADDA UPP BILD:", type=["jpg", "png", "jpeg"])
        if up_file and st.button("⚡ ANIMERA BILD"):
            with st.status("📽️ Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Slow cinematic zoom", "image_url": up_file})
                st.video(str(res))

    with tab3:
        mu_ide = st.text_input("BESKRIV MUSIKEN:", f"{mood} beat")
        intro_text = st.text_input("VAD SKALL RÖSTEN SÄGA?", f"Här kommer en ny hit från {artist_name}")
        if st.button("🎵 GENERERA MED INTRO"):
            with st.status("🎙️ Skapar röst & 🎸 Musik..."):
                with ThreadPoolExecutor() as executor:
                    v_future = executor.submit(replicate.run, "openai/tts-1", input={"text": intro_text, "voice": "alloy"})
                    m_future = executor.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": mu_ide, "duration": 10})
                    
                    st.write("🎙️ **Röst-Intro:**"); st.audio(str(v_future.result()))
                    st.write("🎸 **Ditt Beat:**"); st.audio(str(m_future.result()))

    with tab4:
        if not st.session_state.gallery: st.info("Arkivet är tomt.")
        else:
            # EXPORT KNAPP LÄNGST UPP I ARKIVET
            if st.button("📦 FÖRBERED FULL EXPORT (ZIP)"):
                with st.spinner("Packar arkivet..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        zf.writestr("arkiv_info.json", json.dumps(st.session_state.gallery, indent=4))
                        # Här lägger vi in metadata om alla projekt
                    st.download_button("📥 LADDA NED ZIP", data=zip_buffer.getvalue(), file_name=f"maximusikai_backup_{datetime.datetime.now().strftime('%Y%m%d')}.zip")

            for item in reversed(st.session_state.gallery):
                with st.expander(f"📁 {item['name']} ({item['time']})"):
                    st.video(item['video']); st.audio(item['audio'])
                    c_dl1, c_dl2, c_del = st.columns(3)
                    try:
                        with c_dl1: st.download_button("💾 VIDEO", requests.get(item['video']).content, file_name=f"{item['name']}.mp4", key=f"v_{item['id']}")
                        with c_dl2: st.download_button("🎵 LJUD", requests.get(item['audio']).content, file_name=f"{item['name']}.mp3", key=f"a_{item['id']}")
                    except: st.warning("Länk utgången.")
                    with c_del:
                        if st.button("🗑️ RADERA", key=f"del_{item['id']}"):
                            st.session_state.gallery = [x for x in st.session_state.gallery if x['id'] != item['id']]
                            save_data(st.session_state.gallery)
                            st.rerun()

    with tab5:
        if st.button("DELA SENASTE"):
            if st.session_state.gallery: st.session_state.community_feed.append(st.session_state.gallery[-1]); st.success("Delad!")
        for post in reversed(st.session_state.community_feed):
            st.divider(); st.video(post['video']); st.caption(f"Artist: {artist_name}")

else: st.error("⚠️ REPLICATE_API_TOKEN saknas!")

st.markdown("<br><center><p style='color:#333; font-size:10px;'>MAXIMUSIKAI SPEED PRO // 2026 // T.I.</p></center>", unsafe_allow_html=True)












