import replicate, os, json, time, re, io, requests
from datetime import datetime
import streamlit as st

# VERSIONSHANTERING (Regel NR 1)
VERSION = "1.2.4" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def sanitize_url(output):
    if not output: return None
    target = output[0] if isinstance(output, list) else output
    return str(target).strip()

# INITIALISERING
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "video_library": [], "audio_library": [], "accent": "#00f2ff", 
        "last_img": None, "last_vid": None, "last_audio": None,
        "wallpaper": "https://images.unsplash.com", "bg_opacity": 0.80
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; background-position: center; }}
    .glass {{ background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stImage, .stVideo {{ max-width: 80% !important; margin: auto !important; border-radius: 15px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; background: {accent}11 !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

# NAV
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

# MODUL: SYNTH
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Testa Chrome Note prompten här...")
    if st.button("🚀 GENERERA BILD"):
        try:
            with st.status("Syntetiserar...", expanded=True) as status:
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": user_p, "aspect_ratio": "16:9"})
                url = sanitize_url(res)
                resp = requests.get(url)
                st.session_state.last_img = resp.content
                st.session_state.library.append({"id": time.time(), "data": resp.content, "url": url, "prompt": user_p})
                st.rerun()
        except Exception as e:
            st.error(f"SYNTH ERROR (Regel NR 6): {str(e)}")
    
    if st.session_state.last_img:
        _, mid, _ = st.columns([0.1, 0.8, 0.1]); mid.image(st.session_state.last_img)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: AUDIO
elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    audio_p = st.text_area("BESKRIV DIN LÅT:")
    if st.button("🎸 GENERERA MUSIK"):
        try:
            with st.status("Komponerar...", expanded=True) as status:
                res = replicate.run("sumit-poddar/suno-v3.5:96773229b4344400e9603099958742512f5a0446f25f19036c0192e21b777a87", input={"prompt": audio_p})
                audio_url = sanitize_url(res)
                resp = requests.get(audio_url)
                st.session_state.last_audio = resp.content
                st.session_state.audio_library.append({"id": time.time(), "data": resp.content, "prompt": audio_p})
                st.rerun()
        except Exception as e:
            st.error(f"AUDIO ERROR (Regel NR 6): {str(e)}")
    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: MOVIE (Fallback till Stable Video Diffusion)
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img:
        _, mid_pre, _ = st.columns([0.3, 0.4, 0.3]); mid_pre.image(st.session_state.last_img, caption="Referens")
        if st.button("🎬 ANIMERA (SVD)"):
            try:
                with st.status("Animerar via SVD...", expanded=True) as status:
                    # Regel NR 4: Skicka som BytesIO för SVD
                    img_io = io.BytesIO(st.session_state.last_img)
                    res = replicate.run(
                        "stability-ai/svd:3f7790f5403028243f6ed291775796f600473ef7116975591d1e433f443b740e",
                        input={"input_image": img_io, "video_length": "14_frames_with_svd"}
                    )
                    vid_url = sanitize_url(res)
                    resp = requests.get(vid_url)
                    st.session_state.last_vid = resp.content
                    st.session_state.video_library.append({"id": time.time(), "data": resp.content, "prompt": "SVD Animation"})
                    st.rerun()
            except Exception as e:
                st.error(f"MOVIE ERROR (Regel NR 6): {str(e)}")
    else:
        st.info("Skapa en bild först.")
    if st.session_state.last_vid:
        _, mid_vid, _ = st.columns([0.1, 0.8, 0.1]); mid_vid.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: ARKIV
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t_img, t_aud, t_vid = st.tabs(["🖼️ BILDER", "🎵 LJUD", "🎬 FILMER"])
    with t_img:
        grid = st.columns(4)
        for i, item in enumerate(list(reversed(st.session_state.library))):
            with grid[i % 4]:
                st.image(item['data'])
                if st.button("BKG", key=f"bg_{item['id']}"): 
                    st.session_state.wallpaper = item['url']; st.rerun()
    with t_aud:
        for a in reversed(st.session_state.audio_library):
            st.audio(a['data'])
    with t_vid:
        for v in reversed(st.session_state.video_library):
            st.video(v['data'])
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
