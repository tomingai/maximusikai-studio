import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.2.5"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

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
        st.error(f"Neural Bridge Error: {str(e)[:50]}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "hd_mode": True, "enhance_lvl": 0.8,
        "process_log": [], "analysis": ""
    })

# --- 4. UI ENGINE (Neural Gloss) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.94), rgba(0,0,0,0.98)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ background: rgba(0, 5, 20, 0.9); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: white !important; background: {accent}11 !important; border-radius: 12px; height: 3.5rem; font-weight: bold; }}
    .neural-console {{ 
        background: rgba(0,0,0,0.5); border: 1px solid {accent}22; padding: 15px; border-radius: 10px;
        font-family: 'Courier New', monospace; color: {accent}; font-size: 0.85rem; line-height: 1.4;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, locked) in enumerate(nav):
    if not locked:
        if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
    else: nc[i].markdown(f'<p style="text-align:center; opacity:0.15; font-size:1.5rem; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# --- SYNTH: PROCESS VISUALIZER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:4px;'>🪄 NEURAL VISUALIZER STATION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VISION PROMPT (SV/EN):", placeholder="The Quantum Alchemist...")
    
    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
    st.session_state.style = col1.selectbox("STYLE:", ["Photorealistic", "Cinematic", "Cyberpunk", "Macro"])
    st.session_state.enhance_lvl = col2.slider("AI ENHANCE DEPTH", 0.0, 1.0, 0.8)
    aspect = col3.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXECUTE NEURAL PIPELINE", use_container_width=True):
        if user_p:
            console_area = st.empty()
            with st.status("Neural Pipeline Processing...") as status:
                # 1. LLM Expansion
                st.session_state.process_log = [f"› [{datetime.now().strftime('%H:%M:%S')}] ANALYZING INPUT: '{user_p}'"]
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                status.update(label="Llama-3 expanderar visionen...")
                prompt_instr = f"Act as a professional cinematographer. Expand this to a {st.session_state.style} 8k prompt. Creativity level {st.session_state.enhance_lvl}: {user_p}"
                expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": prompt_instr, "max_new_tokens": 200})))
                
                st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] PROMPT EXPANDED ({len(expanded)} chars)")
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                # 2. FLUX Rendering
                status.update(label="FLUX.1 [schnell] renderar pixlar...")
                st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] STARTING LATENT DIFFUSION (FLUX ENGINE)")
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": expanded, "aspect_ratio": aspect.replace(":", "x")})
                
                if url:
                    st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] RENDERING COMPLETE. SANITIZING DATA...")
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "expanded": expanded, "ts": datetime.now().strftime("%H:%M")})
                    console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                    status.update(label="Pipeline slutförd!", state="complete")
                    st.rerun()
        else: st.error("Please enter a vision.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, caption=f"v{VERSION} Render Result")
        if st.button("🖼 SET AS WALLPAPER"): 
            st.session_state.wallpaper = st.session_state.last_img; st.rerun()
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
                    st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ENGINE MODUL ---
elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ENGINE [ANALYS]</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=450)
        if st.button("🔍 KÖR NEURAL INSPEKTION"):
            res = safe_replicate_run("lucataco/moondream2", {"image": st.session_state.last_img, "prompt": "Identify quality and materials."})
            st.session_state.analysis = res
        if st.session_state.analysis: st.info(st.session_state.analysis)
    else: st.warning("No image to analyze.")
    st.markdown('</div>', unsafe_allow_html=True)







































































