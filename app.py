import replicate, os, json, time, re, io, requests, sys
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# VERSIONSHANTERING
VERSION = "1.3.0" 
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
        "page": "SYNTH", "library": [], "video_library": [], "code_library": [], "accent": "#00f2ff", 
        "last_img": None, "last_vid": None, "last_code": "", "last_html": "", "sandbox_out": "",
        "wallpaper": "https://images.unsplash.com", "bg_opacity": 0.80
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; background-position: center; }}
    .glass {{ background: rgba(0, 10, 30, 0.85); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; background: {accent}11 !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; }}
    .console {{ background: #000; color: #0f0; padding: 15px; border-radius: 10px; font-family: 'Courier New', monospace; border: 1px solid #333; min-height: 50px; }}
    .preview-box {{ background: white; border-radius: 10px; border: 4px solid {accent}; overflow: hidden; }}
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
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="En futuristisk stad i neon...")
    if st.button("🚀 GENERERA BILD"):
        try:
            with st.status("Syntetiserar..."):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": user_p, "aspect_ratio": "16:9"})
                url = sanitize_url(res)
                resp = requests.get(url)
                st.session_state.last_img = resp.content
                st.session_state.library.append({"id": time.time(), "data": resp.content, "url": url, "prompt": user_p})
                st.rerun()
        except Exception as e: st.error(f"ERROR: {e}")
    if st.session_state.last_img: st.image(st.session_state.last_img)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: WEB/APP-GEN (HTML & Python)
elif st.session_state.page == "APP-GEN":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("AI WEB & CODE ARCHITECT")
    mode = st.radio("VÄLJ TYP", ["HEMSIDA (HTML/CSS)", "LOGIK (PYTHON)"], horizontal=True)
    app_prompt = st.text_area("Beskriv din skapelse:", placeholder="En landningssida för ett techno-event med animerad bakgrund...")
    
    if st.button("🛠 BYGG"):
        try:
            with st.status("AI Konstruerar..."):
                sys_msg = "You are a senior developer. Output ONLY raw code without markdown backticks."
                prompt_mod = f"Create a full {mode} file for: {app_prompt}. Include modern styling."
                output = replicate.run("meta/meta-llama-3-70b-instruct", 
                    input={"prompt": prompt_mod, "system_prompt": sys_msg})
                code_res = "".join(output).strip()
                
                if mode == "HEMSIDA (HTML/CSS)":
                    st.session_state.last_html = code_res
                else:
                    st.session_state.last_code = code_res
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

    # DISPLAY & PREVIEW
    if mode == "HEMSIDA (HTML/CSS)" and st.session_state.last_html:
        col_code, col_pre = st.columns(2)
        with col_code:
            st.code(st.session_state.last_html, language="html")
        with col_pre:
            st.markdown("### LIVE PREVIEW")
            st.markdown('<div class="preview-box">', unsafe_allow_html=True)
            components.html(st.session_state.last_html, height=500, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.download_button("LADDA NER INDEX.HTML", st.session_state.last_html, "index.html")

    if mode == "LOGIK (PYTHON)" and st.session_state.last_code:
        st.code(st.session_state.last_code, language="python")
        if st.button("▶️ KÖR LOGIK"):
            old_stdout = sys.stdout
            res_io = sys.stdout = io.StringIO()
            try:
                exec(st.session_state.last_code)
                st.session_state.sandbox_out = res_io.getvalue()
            except Exception as e: st.session_state.sandbox_out = f"FEL: {e}"
            finally: sys.stdout = old_stdout
        
        if st.session_state.sandbox_out:
            st.markdown('<div class="console">' + st.session_state.sandbox_out + '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: MOVIE
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img:
        if st.button("🎬 ANIMERA"):
            try:
                with st.status("Animerar..."):
                    img_io = io.BytesIO(st.session_state.last_img)
                    output = replicate.run("stability-ai/svd:3f7790f5403028243f6ed291775796f600473ef7116975591d1e433f443b740e", 
                        input={"input_image": img_io})
                    st.session_state.last_vid = requests.get(sanitize_url(output)).content
                    st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.last_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: ARKIV
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Media", "Kod"])
    with t1:
        for i in reversed(st.session_state.library): st.image(i['data'])
    with t2:
        if st.session_state.last_html: st.text("Senaste HTML:"); st.code(st.session_state.last_html[:500] + "...")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
