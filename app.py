import replicate, os, json, time, re, io, requests
from datetime import datetime
import streamlit as st

# VERSIONSHANTERING (Regel NR 1)
VERSION = "1.2.1" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def sanitize_url(output):
    if not output: return None
    # Hanterar både strängar och listor från Replicate
    url = str(output[0] if isinstance(output, list) else output).replace("['", "").replace("']", "").replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
    return url if url.startswith("http") else None

# INITIALISERING
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "video_library": [], "accent": "#00f2ff", 
        "last_img": None, "last_vid": None, "wallpaper": "https://images.unsplash.com", "bg_opacity": 0.80
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

# TOP NAVIGATION
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.8, 0.2])
with c_nav:
    nc = st.columns(6)
    if nc[0].button("🎨 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if nc[1].button("🎬 MOVIE"): st.session_state.page = "MOVIE"; st.rerun()
    if nc[2].button("📚 ARKIV"): st.session_state.page = "ARKIV"; st.rerun()
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# MODUL: SYNTH (Flux)
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?")
    if st.button("🚀 GENERERA BILD"):
        bar, timer_text = st.progress(0), st.empty()
        start = time.time()
        # Flux Schnell för snabbhet
        prediction = replicate.predictions.create(version="black-forest-labs/flux-schnell", input={"prompt": user_p, "aspect_ratio": "16:9"})
        while prediction.status not in ["succeeded", "failed", "canceled"]:
            elapsed = int(time.time() - start)
            bar.progress(min(elapsed * 15, 99))
            timer_text.markdown(f"**Syntetiserar:** {prediction.status}... ({elapsed}s)")
            time.sleep(1); prediction.reload()
        
        if prediction.status == "succeeded":
            url = sanitize_url(prediction.output)
            resp = requests.get(url)
            st.session_state.last_img = resp.content
            st.session_state.library.append({"id": time.time(), "data": resp.content, "url": url, "prompt": user_p})
            st.rerun()
    
    if st.session_state.last_img:
        _, mid, _ = st.columns([0.1, 0.8, 0.1]); mid.image(st.session_state.last_img)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: MOVIE (Fixat med Luma Ray-2 för att undvika 404)
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img:
        _, mid_pre, _ = st.columns([0.3, 0.4, 0.3])
        mid_pre.image(st.session_state.last_img, caption="Referensbild")
        
        vid_p = st.text_input("RÖRELSEBESKRIVNING (Valfritt):", placeholder="Kameran åker långsamt framåt...")
        
        if st.button("🎬 ANIMERA MED LUMA"):
            bar, timer_text = st.progress(0), st.empty()
            start = time.time()
            
            # Regel NR 4: Skicka bilden som URL för att Luma ska acceptera den korrekt
            # Vi använder den sparade URL:en från biblioteket för den senaste bilden
            img_url = st.session_state.library[-1]['url'] if st.session_state.library else None
            
            if img_url:
                prediction = replicate.predictions.create(
                    version="luma/ray-2", 
                    input={"prompt": vid_p if vid_p else "Cinematic motion", "start_image_url": img_url}
                )
                
                # Regel NR 5: Polling för tunga processer
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    elapsed = int(time.time() - start)
                    bar.progress(min(elapsed * 2, 99))
                    timer_text.markdown(f"**Animerar (Luma Ray-2):** {prediction.status}... ({elapsed}s)")
                    time.sleep(5); prediction.reload()
                
                if prediction.status == "succeeded":
                    st.session_state.last_vid = sanitize_url(prediction.output)
                    st.session_state.video_library.append({"id": time.time(), "url": st.session_state.last_vid, "prompt": vid_p})
                    st.rerun()
                else:
                    st.error(f"Fel vid animering: {prediction.error}")
            else:
                st.warning("Ingen bild hittades att animera. Skapa en bild i SYNTH först.")
    else:
        st.info("Gå till SYNTH och skapa en bild först för att kunna animera.")
        
    if st.session_state.last_vid:
        _, mid_vid, _ = st.columns([0.1, 0.8, 0.1]); mid_vid.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# MODUL: ARKIV
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t_img, t_vid = st.tabs(["🖼️ BILDER", "🎬 FILMER"])
    with t_img:
        grid = st.columns(4)
        for i, item in enumerate(list(reversed(st.session_state.library))):
            with grid[i % 4]:
                st.image(item['data'])
                if st.button("Bakgrund", key=f"bg_{item['id']}"): 
                    st.session_state.wallpaper = item['url']
                    st.rerun()
    with t_vid:
        for v in reversed(st.session_state.video_library):
            with st.container():
                st.video(v['url'])
                st.caption(f"Prompt: {v['prompt']}")
                st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
