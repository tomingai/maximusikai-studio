import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.5"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. MOTOR & SANITIZER (Regel 21 & 12) ---
def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        if "moondream" in model or "llama" in model: return res
        return sanitize_url(res)
    except Exception as e:
        st.error(f"Neural Error: {str(e)[:50]}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", 
        "library": [], 
        "accent": "#00f2ff", 
        "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", 
        "process_log": [],
        "analysis": ""
    })

# --- 4. UI ENGINE (Neural Gloss & Animations) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    @keyframes pulse-green {{ 
        0% {{ border-color: {accent}44; }} 
        50% {{ border-color: #00ff88; box-shadow: 0 0 20px #00ff8844; }} 
        100% {{ border-color: {accent}44; }} 
    }}
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.94), rgba(0,0,0,0.98)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ background: rgba(0, 5, 20, 0.9); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; }}
    .success-box {{ 
        border: 2px solid #00ff88; 
        animation: pulse-green 2s infinite; 
        border-radius: 15px; padding: 15px; 
        text-align: center; color: #00ff88; 
        font-family: monospace; font-weight: bold; margin: 10px 0;
    }}
    .neural-console {{ 
        background: rgba(0,0,0,0.6); border: 1px solid {accent}22; 
        padding: 15px; border-radius: 10px; 
        font-family: 'Courier New', monospace; color: {accent}; 
        font-size: 0.8rem; line-height: 1.4;
    }}
    .stButton>button {{ 
        border: 1px solid {accent}55 !important; color: white !important; 
        background: {accent}11 !important; border-radius: 12px; 
        height: 3.5rem; font-weight: bold; width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, locked) in enumerate(nav):
    if not locked:
        if nc[i].button(icon, key=f"nav_{target}"): 
            st.session_state.page = target
            st.rerun()
    else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# --- SYNTH: CHRONOS INTERFACE ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:4px;'>🪄 NEURAL PIPELINE v{VERSION}</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VISION PROMPT (SV/EN):", placeholder="The Quantum Alchemist...")
    
    col1, col2 = st.columns([0.7, 0.3])
    st.session_state.style = col1.selectbox("STYLE PRESET:", ["Photorealistic", "Cinematic", "Cyberpunk", "Macro", "Digital Art"])
    aspect = col2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXEKVERA NEURAL KEDJA"):
        if user_p:
            # Tidsaxel & Konsol Init
            progress_bar = st.progress(0)
            console = st.empty()
            log = [f"› [{datetime.now().strftime('%H:%M:%S')}] KERNEL INITIALIZED. READY FOR SYNTHESIS."]
            
            # STEG 1: LLM ANALYS (0-30%)
            progress_bar.progress(10, text="ANALYSING LANGUAGE...")
            log.append("› ATTEMPTING SEMANTIC EXPANSION VIA LLAMA-3...")
            console.markdown(f'<div class="neural-console">{"<br>".join(log)}</div>', unsafe_allow_html=True)
            
            expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={
                "prompt": f"Act as a professional cinematographer. Expand this to a {st.session_state.style} 8k image prompt: {user_p}",
                "max_new_tokens": 200
            })))
            
            # STEG 2: FLUX DIFFUSION (30-90%)
            progress_bar.progress(40, text="STARTING LATENT DIFFUSION...")
            log.append(f"› PROMPT EXPANDED ({len(expanded)} chars)")
            log.append("› COMMENCING FLUX.1 [SCHNELL] NEURAL ENGINE...")
            console.markdown(f'<div class="neural-console">{"<br>".join(log)}</div>', unsafe_allow_html=True)
            
            url = safe_replicate_run("black-forest-labs/flux-schnell", {
                "prompt": expanded, 
                "aspect_ratio": aspect.replace(":", "x")
            })
            
            # STEG 3: FINALIZING (100%)
            if url:
                progress_bar.progress(100, text="SYNTHESIS COMPLETE")
                log.append("› PIXEL DATA RECEIVED. WRITING TO ARCHIVE...")
                console.markdown(f'<div class="neural-console">{"<br>".join(log)}</div>', unsafe_allow_html=True)
                
                st.session_state.last_img = url
                st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                
                st.markdown('<div class="success-box">✅ NEURAL SYNTES SLUTFÖRD - BILD REDO</div>', unsafe_allow_html=True)
                time.sleep(1.5)
                st.rerun()
        else: st.error("Ingen vision angiven.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 ANVÄND SOM BAKGRUND"): 
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ENGINE: ANALYS ---
elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ENGINE [ANALYS]</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=450)
        if st.button("🔍 KÖR NEURAL INSPEKTION"):
            res = safe_replicate_run("lucataco/moondream2", {"image": st.session_state.last_img, "prompt": "Identify quality and materials."})
            st.session_state.analysis = res
        if st.session_state.analysis: st.info(st.session_state.analysis)
    else: st.warning("Skapa en bild i SYNTH först.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ARKIV MODUL ---
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 SYSTEM ARCHIVE")
    if not st.session_state.library: st.info("Archive empty.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("SET WALLPAPER", key=f"w_{i}"):
                    st.session_state.wallpaper = item['url']
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)








































































