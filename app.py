import replicate, os, json, time, re, io, requests, sys
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# VERSIONSHANTERING
VERSION = "1.4.5" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def handle_replicate_output(output):
    if not output: return None, None
    try:
        if hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
            output = list(output)
        if isinstance(output, str) and output.startswith("http"):
            resp = requests.get(output)
            return resp.content, output
        if isinstance(output, bytes):
            return output, None
        if hasattr(output, 'read'):
            return output.read(), None
    except: pass
    return None, None

def ai_call(prompt, system_prompt="You are a helpful assistant."):
    try:
        output = replicate.run("meta/meta-llama-3-70b-instruct", 
            input={"prompt": prompt, "system_prompt": system_prompt})
        return "".join(output).strip()
    except Exception as e: return f"Error: {e}"

# INITIALISERING
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "video_library": [], "accent": "#00f2ff", 
        "last_img": None, "last_img_url": None, "last_logo_url": None, "last_vid": None, 
        "last_audio_url": None, "last_html": "", "wallpaper": "https://images.unsplash.com", 
        "bg_opacity": 0.80, "synth_p": "", "web_p": ""
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; background-position: center; }}
    .glass {{ background: rgba(0, 10, 30, 0.85); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; background: {accent}11 !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; height: 3.5rem; }}
    </style>
""", unsafe_allow_html=True)

# NAV
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.8, 0.2])
with c_nav:
    nc = st.columns(4)
    if nc.button("🎨 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if nc.button("🌐 WEB-GEN"): st.session_state.page = "APP-GEN"; st.rerun()
    if nc.button("🎬 MOVIE"): st.session_state.page = "MOVIE"; st.rerun()
    if nc.button("📚 ARKIV"): st.session_state.page = "ARKIV"; st.rerun()
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# MODUL: SYNTH
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("BILD-SYNTHESIZER")
    st.session_state.synth_p = st.text_input("PROMPT:", value=st.session_state.synth_p)
    if st.button("🚀 GENERERA BILD"):
        with st.spinner("Beräknar pixlar...", show_time=True):
            try:
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": st.session_state.synth_p})
                img_data, img_url = handle_replicate_output(res)
                if img_data:
                    st.session_state.last_img, st.session_state.last_img_url = img_data, img_url
                    st.session_state.library.append({"id": time.time(), "data": img_data, "url": img_url})
                    st.rerun()
            except Exception as e: st.error(f"Flux Error: {e}")
    if st.session_state.last_img: 
        st.image(io.BytesIO(st.session_state.last_img), width=600)
        if st.session_state.last_img_url and st.button("✂️ EXTRAHERA LOGOTYP"):
            with st.spinner("Frilägger objekt...", show_time=True):
                output = replicate.run("lucatidbury/remove-bg:af3ab35653788916c803875082bc780d60c6d7a46587425114704044ee78996e", input={"image": st.session_state.last_img_url})
                st.session_state.last_logo_url = str(output).strip()
                st.success("Logo redo!")
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: WEB-GEN
elif st.session_state.page == "APP-GEN":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("WEB ARCHITECT")
    st.session_state.web_p = st.text_area("Beskrivning:", value=st.session_state.web_p)
    r1 = st.columns(5)
    if r1.button("🛠 BYGG"):
        with st.spinner("Kodar...", show_time=True):
            st.session_state.last_html = ai_call(f"Full HTML/CSS for: {st.session_state.web_p}", "Output ONLY raw HTML/CSS. Use [TITLE], [CONTENT].")
            st.rerun()
    if r1.button("✍️ TEXT"):
        with st.spinner("Skriver...", show_time=True):
            txt = ai_call(f"JSON: TITLE, CONTENT for {st.session_state.web_p}", "Output ONLY raw JSON.")
            try:
                d = json.loads(txt)
                st.session_state.last_html = st.session_state.last_html.replace("[TITLE]", d['TITLE']).replace("[CONTENT]", d['CONTENT'])
                st.rerun()
            except: st.error("Text Error")
    if r1.button("🖼️ BKG"):
        if st.session_state.last_img_url:
            st.session_state.last_html = st.session_state.last_html.replace("</head>", f"<style>body {{ background: url('{st.session_state.last_img_url}') center/cover fixed !important; }}</style></head>")
            st.rerun()
    if r1.button("🔖 LOGO"):
        if st.session_state.last_logo_url:
            st.session_state.last_html = st.session_state.last_html.replace("<body>", f"<body><img src='{st.session_state.last_logo_url}' style='width:80px; position:fixed; top:20px; left:20px; z-index:999;'>")
            st.rerun()
    if r1.button("🎵 LJUD"):
        with st.spinner("Komponerar...", show_time=True):
            try:
                # FIX: Använder slug istället för hash för ökad stabilitet
                out = replicate.run("facebookresearch/musicgen", 
                    input={"prompt": st.session_state.web_p[:100], "duration": 8, "model_version": "stereo-large"})
                st.session_state.last_audio_url = str(out).strip()
                st.session_state.last_html = st.session_state.last_html.replace("<body>", f"<body><audio autoplay loop><source src='{st.session_state.last_audio_url}' type='audio/mpeg'></audio>")
                st.rerun()
            except Exception as e: st.error(f"MusicGen Error: {e}")

    if st.session_state.last_html:
        components.html(st.session_state.last_html, height=500, scrolling=True)
        st.download_button("🚀 EXPORT", st.session_state.last_html, "index.html")
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: MOVIE & ARKIV
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img:
        if st.button("🎬 ANIMERA"):
            with st.spinner("SVD Render...", show_time=True):
                img_in = st.session_state.last_img_url if st.session_state.last_img_url else io.BytesIO(st.session_state.last_img)
                output = replicate.run("stability-ai/svd", input={"input_image": img_in})
                st.session_state.last_vid = requests.get(str(output).strip()).content
                st.rerun()
    if st.session_state.last_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    grid = st.columns(4)
    for i, item in enumerate(reversed(st.session_state.library)): grid[i % 4].image(io.BytesIO(item['data']))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
