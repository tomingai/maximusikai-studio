import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

# Säkerställ API-nyckel
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
elif not os.environ.get("REPLICATE_API_TOKEN"):
    st.error("⚠️ REPLICATE_API_TOKEN saknas i secrets/miljövariabler.")

# --- 2. MOTOR-FUNKTIONER ---
def clean_prompt(text):
    if not text: return ""
    # Rensar bort skräptext som LLMs ibland lägger till
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        return res
    except Exception as e:
        st.error(f"Neural Error: {e}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", 
        "library": [], 
        "accent": "#00f2ff", 
        "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Cinematic", 
        "process_log": []
    })

# --- 4. UI ENGINE (CSS) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ 
        background: rgba(0, 10, 25, 0.8); 
        backdrop-filter: blur(20px); 
        border: 1px solid {accent}44; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }}
    h1, h2, h3, label, p {{ color: white !important; font-family: 'Inter', sans-serif; }}
    .stButton>button {{ 
        border: 1px solid {accent}88 !important; 
        background: {accent}22 !important; color: white !important; 
        border-radius: 10px; transition: 0.3s;
    }}
    .stButton>button:hover {{ background: {accent}44 !important; transform: scale(1.02); }}
    .neural-console {{ 
        background: rgba(0,0,0,0.9); border: 1px solid {accent}44; 
        padding: 10px; border-radius: 5px; font-family: monospace; 
        color: {accent}; font-size: 0.85rem; height: 120px; overflow-y: auto;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 5px 15px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, locked) in enumerate(nav):
    if not locked:
        if nc[i].button(f"{icon} {target}", key=f"nav_{target}"): 
            st.session_state.page = target
            st.rerun()
    else:
        nc[i].markdown(f'<p style="text-align:center; opacity:0.3; margin-top:10px;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# --- MODUL: SYNTH STATION ---
if st.session_state.page == "SYNTH":
    st.markdown(f"<h2 style='color:{accent};'>🪄 NEURAL SYNTH STATION</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        user_p = st.text_area("VAD SKALL VI SKAPA?", placeholder="Beskriv din vision här...", height=100)
        
        c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
        with c1:
            st.session_state.style = st.selectbox("VISUELL STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Anime", "Oil Painting"])
        with c2:
            aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2"], index=1)
        with c3:
            model_choice = st.selectbox("MOTOR:", ["FLUX Schnell", "FLUX Dev"])

        if st.button("🚀 EXEKVERA NEURAL PIPELINE"):
            if user_p:
                log_placeholder = st.empty()
                logs = ["› INITIALIZING NEURAL ENGINE...", f"› TARGET STYLE: {st.session_state.style}"]
                
                # Steg 1: Prompt Expansion (Llama 3)
                log_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                logs.append("› EXPANDING VISION VIA LLAMA-3...")
                
                raw_expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={
                    "prompt": f"Write a detailed {st.session_state.style} image prompt based on: {user_p}. Max 100 words. Output ONLY the expanded prompt.",
                    "max_new_tokens": 150
                })))
                expanded = clean_prompt(raw_expanded)
                logs.append(f"› PROMPT OPTIMIZED: {expanded[:50]}...")
                log_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)

                # Steg 2: Bildgenerering (Flux)
                logs.append("› RENDERING PIXELS (FLUX)...")
                log_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                
                model_path = "black-forest-labs/flux-schnell" if "Schnell" in model_choice else "black-forest-labs/flux-dev"
                output = safe_replicate_run(model_path, {
                    "prompt": expanded, 
                    "aspect_ratio": aspect.replace(":", "x"),
                    "output_format": "webp"
                })

                if output:
                    img_url = output[0] if isinstance(output, list) else output
                    st.session_state.last_img = img_url
                    st.session_state.library.append({
                        "url": img_url, 
                        "prompt": user_p, 
                        "style": st.session_state.style,
                        "ts": datetime.now().strftime("%H:%M")
                    })
                    logs.append("› PIPELINE COMPLETE. READY.")
                    log_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Vänligen ange en prompt först.")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.last_img:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.image(st.session_state.last_img, caption="NEURAL OUTPUT", use_container_width=True)
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("🖼 SÄTT SOM BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
        if col_btn2.button("💾 SPARA TILL ARKIV"):
            st.toast("Sparad i Arkivet!", icon="📚")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MODUL: ARKIV ---
elif st.session_state.page == "ARKIV":
    st.markdown(f"<h2 style='color:{accent};'>📚 SYSTEM ARCHIVE</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.info("Arkivet är tomt. Skapa något i SYNTH-stationen!")
    else:
        # Visa i ett rutnät
        cols = st.columns(3)
        for idx, item in enumerate(reversed(st.session_state.library)):
            with cols[idx % 3]:
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.image(item['url'], use_container_width=True)
                st.caption(f"🕒 {item['ts']} | {item['style']}")
                if st.button("LADDA", key=f"load_{idx}"):
                    st.session_state.last_img = item['url']
                    st.session_state.page = "SYNTH"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# --- MODUL: VISION ENGINE ---
elif st.session_state.page == "ENGINE":
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ANALYSIS ENGINE</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.image(st.session_state.last_img, use_container_width=True)
        with col2:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            task = st.selectbox("ANALYS-TYP:", ["Beskriv detaljerat", "Identifiera objekt", "Föreslå färgpalett"])
            if st.button("🔍 STARTA ANALYS"):
                with st.spinner("Analyserar pixlar..."):
                    analysis = safe_replicate_run("lucataco/moondream2", {
                        "image": st.session_state.last_img, 
                        "prompt": task
                    })
                    st.markdown(f"**RESULTAT:**<br>{analysis}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Ingen aktiv bild att analysera. Gå till SYNTH.")

# --- FOOTER ---
st.markdown(f"""
    <div style="position: fixed; bottom: 10px; right: 20px; color: {accent}; opacity: 0.5; font-family: monospace; font-size: 0.7rem;">
        OS STATUS: ONLINE | ENCRYPTED | {VERSION}
    </div>
""", unsafe_allow_html=True)























































































































































