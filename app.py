import replicate, os, json, time, re, io, requests, sys
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# VERSIONSHANTERING
VERSION = "1.4.8" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def handle_any_output(output):
    """Extraherar data eller URL från ALLA typer av Replicate-svar."""
    if not output: return None, None
    
    try:
        # Om det är en lista/generator (Flux standard), ta första objektet
        target = output
        if isinstance(output, list): target = output[0]
        elif hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
            target = next(iter(output))

        # Om det är en URL (sträng)
        if isinstance(target, str) and target.startswith("http"):
            resp = requests.get(target)
            return resp.content, target
            
        # Om det är ett 'File'-objekt eller 'Bytes' (nytt format)
        if hasattr(target, 'read'):
            data = target.read()
            return data, None
        if isinstance(target, bytes):
            return target, None
            
    except Exception as e:
        st.error(f"Datafel: {e}")
    return None, None

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

# MODUL: SYNTH (TOTAL FIX v1.4.8)
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("BILD-SYNTHESIZER")
    st.session_state.synth_p = st.text_input("PROMPT:", value=st.session_state.synth_p)
    if st.button("🚀 GENERERA BILD"):
        with st.spinner("Extraherar bilddata från AI-noden...", show_time=True):
            try:
                # Vi kör Flux Schnell
                output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": st.session_state.synth_p})
                img_data, img_url = handle_any_output(output)
                
                if img_data:
                    st.session_state.last_img = img_data
                    st.session_state.last_img_url = img_url
                    st.session_state.library.append({"id": time.time(), "data": img_data, "url": img_url})
                    st.rerun()
                else:
                    st.error("Kunde inte extrahera bilddatan. Försök igen.")
            except Exception as e: st.error(f"Flux Error: {e}")
            
    if st.session_state.last_img: 
        st.image(io.BytesIO(st.session_state.last_img), width=600)
        if st.session_state.last_img_url and st.button("✂️ EXTRAHERA LOGOTYP"):
            with st.spinner("Frilägger...", show_time=True):
                res = replicate.run("lucatidbury/remove-bg:af3ab35653788916c803875082bc780d60c6d7a46587425114704044ee78996e", input={"image": st.session_state.last_img_url})
                _, logo_url = handle_any_output(res)
                st.session_state.last_logo_url = logo_url
                st.success("Logo klar!")
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: WEB-GEN
elif st.session_state.page == "APP-GEN":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("WEB ARCHITECT")
    st.session_state.web_p = st.text_area("Beskrivning:", value=st.session_state.web_p)
    r = st.columns(5)
    if r[0].button("🛠 BYGG"):
        with st.spinner("Kodar...", show_time=True):
            res = replicate.run("meta/meta-llama-3-70b-instruct", input={"prompt": f"Full HTML/CSS for: {st.session_state.web_p}", "system_prompt": "Output only raw HTML."})
            st.session_state.last_html = "".join(res).strip()
            st.rerun()
    if r[1].button("🖼️ BKG") and st.session_state.last_img_url:
        st.session_state.last_html = st.session_state.last_html.replace("</head>", f"<style>body {{ background: url('{st.session_state.last_img_url}') center/cover fixed !important; }}</style></head>")
        st.rerun()
    
    if st.session_state.last_html:
        st.session_state.last_html = st.text_area("KOD:", value=st.session_state.last_html, height=200)
        components.html(st.session_state.last_html, height=500, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)

# MODULER: MOVIE & ARKIV
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img_url and st.button("🎬 ANIMERA"):
        with st.spinner("Animerar...", show_time=True):
            out = replicate.run("stability-ai/svd:3f7790f5403028243f6ed291775796f600473ef7116975591d1e433f443b740e", input={"input_image": st.session_state.last_img_url})
            video_data, _ = handle_any_output(out)
            st.session_state.last_vid = video_data
            st.rerun()
    if st.session_state.last_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    for i in reversed(st.session_state.library): st.image(io.BytesIO(i['data']), width=200)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
