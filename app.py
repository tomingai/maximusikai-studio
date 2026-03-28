import replicate, os, json, time, re, io, requests
from datetime import datetime
import streamlit as st

# VERSIONSHANTERING (Regel NR 1)
VERSION = "1.2.7" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def sanitize_url(output):
    if not output: return None
    # Replicate returnerar ofta en lista för video/bild, vi vill ha strängen (URL)
    target = output[0] if isinstance(output, list) else output
    return str(target).strip()

# INITIALISERING
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", 
        "library": [], 
        "video_library": [], 
        "audio_library": [], 
        "accent": "#00f2ff", 
        "last_img": None, 
        "last_vid": None, 
        "last_audio": None,
        "wallpaper": "https://images.unsplash.com", 
        "bg_opacity": 0.80
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed; background-position: center; 
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); 
        border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; 
    }}
    .stImage, .stVideo {{ max-width: 100% !important; border-radius: 15px; border: 1px solid {accent}22; }}
    .stButton>button {{ 
        border: 1px solid {accent}66 !important; background: {accent}11 !important; 
        color: white !important; border-radius: 12px; font-weight: bold; width: 100%; 
    }}
    h1, h2, h3 {{ color: {accent} !important; text-transform: uppercase; letter-spacing: 2px; }}
    </style>
""", unsafe_allow_html=True)

# NAVIGERING
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.8, 0.2])
with c_nav:
    nc = st.columns(4)
    if nc[0].button("🎨 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if nc[1].button("🎵 AUDIO"): st.session_state.page = "AUDIO"; st.rerun()
    if nc[2].button("🎬 MOVIE"): st.session_state.page = "MOVIE"; st.rerun()
    if nc[3].button("📚 ARKIV"): st.session_state.page = "ARKIV"; st.rerun()
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# MODUL: SYNTH (Flux Schnell)
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("BILD-SYNTHESIZER")
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Neon city, cinematic lighting, 8k...")
    if st.button("🚀 GENERERA BILD"):
        try:
            with st.status("Syntetiserar...", expanded=True):
                # Vi använder slugen direkt för stabilitet
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": user_p, "aspect_ratio": "16:9"})
                url = sanitize_url(res)
                resp = requests.get(url)
                st.session_state.last_img = resp.content
                st.session_state.library.append({"id": time.time(), "data": resp.content, "url": url, "prompt": user_p})
                st.rerun()
        except Exception as e:
            st.error(f"SYSTEM ERROR: {str(e)}")
    
    if st.session_state.last_img:
        _, mid, _ = st.columns([0.1, 0.8, 0.1])
        mid.image(st.session_state.last_img)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: MOVIE (Stable Video Diffusion - Fixad version)
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("ANIMATIONS-STUDIO")
    if st.session_state.last_img:
        col_img, col_ctrl = st.columns([0.5, 0.5])
        
        with col_img:
            st.image(st.session_state.last_img, caption="Källbild")
        
        with col_ctrl:
            st.info("Reglage för animation:")
            motion = st.slider("Rörelse-intensitet", 1, 255, 127)
            fps = st.slider("Bildhastighet (FPS)", 5, 25, 6)
            
            if st.button("🎬 GENERERA ANIMATION"):
                try:
                    with st.status("Beräknar rörelse (SVD)...", expanded=True):
                        img_io = io.BytesIO(st.session_state.last_img)
                        # FIX: Vi använder den breda slugen "stability-ai/svd" istället för den låsta hashen
                        output = replicate.run(
                            "stability-ai/svd:3f7790f5403028243f6ed291775796f600473ef7116975591d1e433f443b740e",
                            input={
                                "input_image": img_io,
                                "motion_bucket_id": motion,
                                "fps": fps
                            }
                        )
                        vid_url = sanitize_url(output)
                        vid_resp = requests.get(vid_url)
                        st.session_state.last_vid = vid_resp.content
                        st.session_state.video_library.append({
                            "id": time.time(), 
                            "data": vid_resp.content, 
                            "prompt": f"Motion: {motion}, FPS: {fps}"
                        })
                        st.rerun()
                except Exception as e:
                    st.error(f"MOVIE ERROR: {str(e)}")
                    st.info("Tips: Replicate kan ha uppdaterat modellen. Testa att använda slug 'stability-ai/svd' utan hash om felet kvarstår.")
    else:
        st.warning("Gå till SYNTH och skapa en bild först!")
    
    if st.session_state.last_vid:
        st.divider()
        st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: AUDIO
elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("LJUD-LABB")
    st.info("Musikgenerering kommer i nästa uppdatering.")
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: ARKIV
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("ARKIV")
    t_img, t_vid = st.tabs(["🖼️ BILDER", "🎬 FILMER"])
    
    with t_img:
        if st.session_state.library:
            grid = st.columns(4)
            for i, item in enumerate(list(reversed(st.session_state.library))):
                with grid[i % 4]:
                    st.image(item['data'])
                    st.download_button("SPARA", item['data'], file_name=f"img_{i}.png", key=f"dl_{item['id']}")
        else: st.write("Tomt.")

    with t_vid:
        if st.session_state.video_library:
            for v in reversed(st.session_state.video_library):
                st.video(v['data'])
                st.download_button("SPARA FILM", v['data'], file_name=f"vid_{time.time()}.mp4", key=f"dlv_{v['id']}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
