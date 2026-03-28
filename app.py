import replicate, os, json, time, re, io, requests, sys
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# VERSIONSHANTERING
VERSION = "1.3.9" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def sanitize_url(output):
    """Extraherar en ren URL-sträng från Replicates olika svarsformat."""
    if not output: return None
    try:
        # Om det är en lista, ta första elementet
        if isinstance(output, list): output = output[0]
        # Om det är en generator/iterator, konvertera till lista och ta första
        if hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
            output = list(output)[0]
        return str(output).strip()
    except: return None

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
    if nc[0].button("🎨 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if nc[1].button("🌐 WEB-GEN"): st.session_state.page = "APP-GEN"; st.rerun()
    if nc[2].button("🎬 MOVIE"): st.session_state.page = "MOVIE"; st.rerun()
    if nc[3].button("📚 ARKIV"): st.session_state.page = "ARKIV"; st.rerun()
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# MODUL: SYNTH
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("BILD-SYNTHESIZER")
    st.session_state.synth_p = st.text_input("VAD SKALL VI SKAPA?", value=st.session_state.synth_p)
    if st.button("🚀 GENERERA"):
        with st.status("Syntetiserar..."):
            # Flux Schnell anrop
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": st.session_state.synth_p, "aspect_ratio": "16:9"})
            url = sanitize_url(res)
            
            if url and url.startswith("http"):
                try:
                    img_data = requests.get(url).content
                    st.session_state.last_img = img_data
                    st.session_state.last_img_url = url
                    st.session_state.library.append({"id": time.time(), "data": img_data, "url": url})
                    st.rerun()
                except Exception as e: st.error(f"Nedladdningsfel: {e}")
            else:
                st.error("Kunde inte generera en giltig bild-URL. Försök igen.")

    if st.session_state.last_img: 
        st.image(st.session_state.last_img, width=400)
        if st.button("✂️ GÖR LOGO"):
            with st.status("Extraherar..."):
                output = replicate.run("lucatidbury/remove-bg:af3ab35653788916c803875082bc780d60c6d7a46587425114704044ee78996e", input={"image": st.session_state.last_img_url})
                st.session_state.last_logo_url = sanitize_url(output)
                st.success("Logotyp redo!")
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: WEB-GEN
elif st.session_state.page == "APP-GEN":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("WEB ARCHITECT")
    st.session_state.web_p = st.text_area("Beskriv hemsidan:", value=st.session_state.web_p)
    
    row1 = st.columns(4)
    row2 = st.columns(4)
    
    if row1[0].button("🛠 BYGG"):
        st.session_state.last_html = ai_call(f"Full HTML/CSS for: {st.session_state.web_p}", "Output ONLY raw HTML/CSS. Use [TITLE], [CONTENT].")
        st.rerun()
    if row1[1].button("✍️ TEXT"):
        txt = ai_call(f"JSON: TITLE, CONTENT for {st.session_state.web_p}", "Output ONLY raw JSON.")
        try:
            d = json.loads(txt)
            st.session_state.last_html = st.session_state.last_html.replace("[TITLE]", d['TITLE']).replace("[CONTENT]", d['CONTENT'])
            st.rerun()
        except: st.error("JSON Error")
    if row1[2].button("🖼️ BKG"):
        if st.session_state.last_img_url:
            st.session_state.last_html = st.session_state.last_html.replace("</head>", f"<style>body {{ background: url('{st.session_state.last_img_url}') center/cover fixed !important; }}</style></head>")
            st.rerun()
    if row1[3].button("🔖 LOGO"):
        if st.session_state.last_logo_url:
            st.session_state.last_html = st.session_state.last_html.replace("<body>", f"<body><img src='{st.session_state.last_logo_url}' style='width:60px; position:fixed; top:20px; left:20px; z-index:999;'>")
            st.rerun()

    if row2[0].button("🎵 LJUD"):
        with st.status("Komponerar..."):
            out = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db539ea97151b69f31745739ef35147814457bb2212b20f0", input={"prompt": st.session_state.web_p[:50], "duration": 8})
            st.session_state.last_audio_url = sanitize_url(out)
            st.session_state.last_html = st.session_state.last_html.replace("<body>", f"<body><audio autoplay loop><source src='{st.session_state.last_audio_url}' type='audio/mpeg'></audio>")
            st.rerun()
    
    if st.session_state.last_html:
        st.divider()
        components.html(st.session_state.last_html, height=500, scrolling=True)
        st.download_button("🚀 EXPORTERA index.html", st.session_state.last_html, "index.html")
    st.markdown('</div>', unsafe_allow_html=True)

# MODULER: MOVIE & ARKIV
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img:
        if st.button("🎬 ANIMERA"):
            with st.status("Animerar..."):
                output = replicate.run("stability-ai/svd:3f7790f5403028243f6ed291775796f600473ef7116975591d1e433f443b740e", input={"input_image": io.BytesIO(st.session_state.last_img)})
                vid_url = sanitize_url(output)
                st.session_state.last_vid = requests.get(vid_url).content
                st.rerun()
    if st.session_state.last_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    for i in reversed(st.session_state.library): st.image(i['data'], width=200)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
