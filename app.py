import replicate, os, json, time, re, io, requests
from datetime import datetime
import streamlit as st

# VERSIONSHANTERING
VERSION = "1.2.8" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def sanitize_url(output):
    if not output: return None
    target = output if isinstance(output, list) else output
    return str(target).strip()

# INITIALISERING
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "video_library": [], "code_library": [], "accent": "#00f2ff", 
        "last_img": None, "last_vid": None, "last_code": "",
        "wallpaper": "https://images.unsplash.com", "bg_opacity": 0.80
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; background-position: center; }}
    .glass {{ background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; background: {accent}11 !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; }}
    h1, h2, h3 {{ color: {accent} !important; text-transform: uppercase; letter-spacing: 2px; }}
    </style>
""", unsafe_allow_html=True)

# NAV
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.8, 0.2])
with c_nav:
    nc = st.columns(4)
    if nc[0].button("🎨 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if nc[1].button("🛠 APP-GEN"): st.session_state.page = "APP-GEN"; st.rerun()
    if nc[2].button("🎬 MOVIE"): st.session_state.page = "MOVIE"; st.rerun()
    if nc[3].button("📚 ARKIV"): st.session_state.page = "ARKIV"; st.rerun()
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# MODUL: SYNTH
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("BILD-SYNTHESIZER")
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Neon city, cinematic lighting...")
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

# MODUL: APP-GEN (Här skapas kod!)
elif st.session_state.page == "APP-GEN":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("AI APP ARCHITECT")
    app_prompt = st.text_area("Beskriv appen/scriptet du vill att jag ska koda:", placeholder="Skriv ett Python-script som räknar ut BMI...")
    
    if st.button("🛠 GENERERA KOD"):
        try:
            with st.status("AI skriver kod..."):
                # Vi anropar Llama-3 för ren kodgenerering
                full_prompt = f"Write only the python code for: {app_prompt}. No explanations, just code."
                output = replicate.run(
                    "meta/meta-llama-3-70b-instruct",
                    input={"prompt": full_prompt, "system_prompt": "You are a world class Python developer. Output only raw code."}
                )
                code_text = "".join(output)
                st.session_state.last_code = code_text
                st.session_state.code_library.append({"id": time.time(), "code": code_text, "name": app_prompt[:20]})
                st.rerun()
        except Exception as e: st.error(f"APP-GEN ERROR: {e}")
    
    if st.session_state.last_code:
        st.code(st.session_state.last_code, language='python')
        st.download_button("LADDA NER .PY", st.session_state.last_code, "generated_app.py")
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: MOVIE
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("ANIMATIONS-STUDIO")
    if st.session_state.last_img:
        motion = st.slider("Rörelse", 1, 255, 127)
        if st.button("🎬 ANIMERA"):
            try:
                with st.status("Animerar..."):
                    img_io = io.BytesIO(st.session_state.last_img)
                    output = replicate.run(
                        "stability-ai/svd:3f7790f5403028243f6ed291775796f600473ef7116975591d1e433f443b740e",
                        input={"input_image": img_io, "motion_bucket_id": motion}
                    )
                    vid_url = sanitize_url(output)
                    vid_resp = requests.get(vid_url)
                    st.session_state.last_vid = vid_resp.content
                    st.session_state.video_library.append({"id": time.time(), "data": vid_resp.content})
                    st.rerun()
            except Exception as e: st.error(f"MOVIE ERROR: {e}")
    else: st.warning("Skapa bild i SYNTH först.")
    if st.session_state.last_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: ARKIV
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t_img, t_vid, t_code = st.tabs(["🖼️ BILDER", "🎬 FILMER", "💻 KOD"])
    with t_img:
        for item in reversed(st.session_state.library): st.image(item['data'])
    with t_vid:
        for v in reversed(st.session_state.video_library): st.video(v['data'])
    with t_code:
        for c in reversed(st.session_state.code_library):
            st.text(f"App: {c['name']}...")
            st.code(c['code'], language='python')
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
