import streamlit as st
import replicate
import os
import requests
import time
import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, vfx
import moviepy.video.fx.all as mp_fx

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO", page_icon="🎵", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "community_feed" not in st.session_state: st.session_state.community_feed = []
if "artist_name" not in st.session_state: st.session_state.artist_name = "Anonym Artist"

# --- 2. DEN ULTIMATA DESIGNEN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(125deg, #050505, #0a0a0a, #0b001a, #050505); background-size: 400% 400%; animation: gradientBG 15s ease infinite; color: #fff; }
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stWidget label p, label, .stMarkdown p { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 2px !important; text-shadow: 0 0 10px rgba(255,255,255,0.5) !important; font-size: 14px !important; }
    div[data-baseweb="tab-list"] { background-color: rgba(255, 255, 255, 0.05) !important; padding: 10px !important; border-radius: 15px !important; gap: 20px !important; }
    button[data-baseweb="tab"] div p { color: #FFFFFF !important; font-weight: 900 !important; font-size: 22px !important; text-shadow: 0 0 15px rgba(255,255,255,1) !important; text-transform: uppercase !important; }
    button[aria-selected="true"] div p { color: #bf00ff !important; text-shadow: 0 0 25px #bf00ff !important; }
    .neon-container { background: rgba(10, 10, 10, 0.85); padding: 30px; border-radius: 25px; border: 2px solid rgba(191, 0, 255, 0.6); box-shadow: 0px 0px 60px rgba(191, 0, 255, 0.3); text-align: center; margin-bottom: 30px; backdrop-filter: blur(15px); }
    .neon-title { font-family: 'Arial Black', sans-serif; font-size: 60px; font-weight: 900; color: #fff; text-shadow: 0 0 15px #bf00ff, 0 0 40px #bf00ff; margin: 0; }
    .stButton>button { background: rgba(191, 0, 255, 0.1); color: #bf00ff; border: 2px solid #bf00ff; width: 100%; font-weight: bold; border-radius: 12px; height: 3.5em; text-transform: uppercase; }
    .stButton>button:hover { background: #bf00ff; color: #000; box-shadow: 0px 0px 40px #bf00ff; }
    .lyrics-card { background: rgba(20, 20, 20, 0.8); padding: 20px; border-left: 5px solid #bf00ff; border-radius: 10px; margin-top: 10px; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p><p style="color:#bf00ff; letter-spacing: 5px;">STUDIO PRO EDITION</p></div>', unsafe_allow_html=True)

# HJÄLPFUNKTIONER
def get_url(output):
    if isinstance(output, list): return str(output[0])
    if hasattr(output, 'url'): return str(output.url)
    return str(output)

# --- 3. SIDOMENY (ARTISTPROFIL) ---
with st.sidebar:
    st.header("👤 ARTISTPROFIL")
    st.session_state.artist_name = st.text_input("DITT ARTISTNAMN:", st.session_state.artist_name)
    st.divider()
    st.header("🎨 STIL-PRESETS")
    preset = st.radio("VÄLJ MOOD:", ["Cyberpunk", "Lo-fi Dreams", "Retro VHS", "Dark Techno", "Svensk Sommar"])
    st.info("Varje mood justerar automatiskt din prompt för bäst resultat.")

# API-KOLL
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    api_ready = True
else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
    api_ready = False

if api_ready:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪄 TOTAL MAGI", "🎬 REGISSÖREN", "🎧 BARA MUSIK", "📚 BIBLIOTEK", "🌐 COMMUNITY"])

    # --- FLIK 1: TOTAL MAGI (UPPGRADERAD) ---
    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            proj_name = st.text_input("PROJEKTETS NAMN:", f"PROJ-{len(st.session_state.gallery)+1}")
            m_ide = st.text_area("VAD SKALL VI SKAPA?", f"En scen i {preset}-stil")
            vfx_choice = st.selectbox("VÄLJ VISUELLT FILTER:", ["None", "Black & White", "High Contrast", "Mirror"])
            
            if st.button("🚀 STARTA FULL PRODUKTION"):
                with st.status("🏗️ MAXIMUSIKAI BYGGER...") as status:
                    try:
                        # 1. Bild
                        status.write("🎨 Genererar bild...")
                        img_raw = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {preset} style", "aspect_ratio": "16:9"})
                        img_url = get_url(img_raw)
                        time.sleep(12) 

                        # 2. Text
                        status.write("✍️ Skriver text...")
                        lyrics_res = replicate.run("meta/llama-2-70b-chat", input={"prompt": f"Write 4 rhyming lines in {preset} vibe about {m_ide}. ONLY lyrics."})
                        lyrics = "".join(lyrics_res).replace('"', '').strip()
                        time.sleep(12)

                        # 3. Video & Musik
                        status.write("📽️ Animerar video...")
                        v_url = get_url(replicate.run("minimax/video-01", input={"prompt": "Cinematic movement", "first_frame_image": img_url}))
                        time.sleep(12)
                        
                        status.write("🎵 Komponerar musik...")
                        m_url = get_url(replicate.run("facebookresearch/musicgen", input={"prompt": f"{preset} melodic music", "duration": 8}))

                        # 4. VFX MIXNING
                        status.write("🧪 Slutför mixning i studion...")
                        v_data = requests.get(v_url).content
                        a_data = requests.get(m_url).content
                        
                        with open("temp_v.mp4", "wb") as f: f.write(v_data)
                        with open("temp_a.mp3", "wb") as f: f.write(a_data)
                        
                        clip = VideoFileClip("temp_v.mp4")
                        
                        # Applicera filter
                        if vfx_choice == "Black & White": clip = clip.fx(mp_fx.blackwhite)
                        elif vfx_choice == "High Contrast": clip = clip.fx(mp_fx.lum_contrast, contrast=0.5)
                        elif vfx_choice == "Mirror": clip = clip.fx(mp_fx.mirror_x)
                        
                        audio = AudioFileClip("temp_a.mp3").set_duration(clip.duration)
                        final_filename = f"out_{int(time.time())}.mp4"
                        clip.set_audio(audio).write_videofile(final_filename, codec="libx264", audio_codec="aac", logger=None)

                        entry = {"name": proj_name, "artist": st.session_state.artist_name, "video": final_filename, "lyrics": lyrics, "audio_data": a_data, "time": datetime.datetime.now().strftime("%H:%M")}
                        st.session_state.gallery.append(entry)
                        
                        status.update(label="✅ PRODUKTION KLAR!", state="complete")
                        with c2:
                            st.video(final_filename)
                            st.markdown(f"<div class='lyrics-card'><b>{st.session_state.artist_name} - {proj_name}</b><br><br>{lyrics}</div>", unsafe_allow_html=True)
                            
                            # DOWNLOAD BUTTONS
                            dl_col1, dl_col2 = st.columns(2)
                            with dl_col1:
                                with open(final_filename, "rb") as f:
                                    st.download_button("💾 VIDEO (MP4)", f, f"{proj_name}.mp4", "video/mp4")
                            with dl_col2:
                                st.download_button("🎵 MUSIK (MP3)", a_data, f"{proj_name}.mp3", "audio/mp3")

                    except Exception as e:
                        st.error(f"Fel: {e}")

    # --- FLIK 4: BIBLIOTEK ---
    with tab4:
        st.subheader("DITT LOKALA ARKIV")
        if not st.session_state.gallery:
            st.info("Arkivet är tomt.")
        else:
            for item in reversed(st.session_state.gallery):
                with st.expander(f"📁 {item['name']} av {item['artist']}"):
                    st.video(item['video'])
                    st.write(item['lyrics'])
                    with open(item['video'], "rb") as f:
                        st.download_button(f"Ladda ner {item['name']}", f, f"{item['name']}.mp4", key=f"dl_{item['video']}")

    # --- FLIK 5: COMMUNITY ---
    with tab5:
        st.markdown("<h2 style='text-align:center; color:#bf00ff;'>🌐 COMMUNITY FEED</h2>", unsafe_allow_html=True)
        if st.button("DELA SENASTE PROJEKTET") and st.session_state.gallery:
            st.session_state.community_feed.append(st.session_state.gallery[-1])
            st.success(f"Ditt verk som '{st.session_state.artist_name}' är nu publikt!")
        
        for post in reversed(st.session_state.community_feed):
            st.divider()
            st.markdown(f"### {post['name']}")
            st.caption(f"Artist: {post['artist']} | Skapad: {post['time']}")
            st.video(post['video'])
            st.write(post['lyrics'])

st.markdown("<br><center><small>MAXIMUSIKAI PRO // 2024</small></center>", unsafe_allow_html=True)




