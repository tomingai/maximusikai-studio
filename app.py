import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION & DATA SHIELD ---
VERSION = "11.5.5-VISUAL-SHIELD"
DB_FILE = "maximusik_history.json"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. PERSISTENCE ENGINE (Regel 8) ---
def save_data():
    try:
        data = {
            "library": st.session_state.get("library", []),
            "wallpaper": st.session_state.get("wallpaper", ""),
            "brightness": st.session_state.get("brightness", 5),
            "accent": st.session_state.get("accent", "#00f2ff"),
            "last_img": st.session_state.get("last_img", None)
        }
        with open(DB_FILE, "w") as f: json.dump(data, f)
    except: pass

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return None
    return None

# --- 3. MOTORER & NUCLEAR CLEANER ---
def nuclear_clean(text):
    if not text: return ""
    clean = str(text).replace('"', '').replace("'", "").replace('\n', ' ')
    prefixes = ["Here is", "Prompt:", "Expanded:", "Sure", "The prompt is"]
    for p in prefixes:
        if p in clean: clean = clean.split(p)[-1]
    return clean.strip()

def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

# --- 4. INITIALISERING ---
if "page" not in st.session_state:
    saved = load_data()
    st.session_state.update({
        "page": "SYNTH",
        "library": saved["library"] if saved else [],
        "accent": saved["accent"] if saved else "#00f2ff",
        "last_img": saved["last_img"] if saved else None,
        "wallpaper": saved["wallpaper"] if saved else "https://images.unsplash.com",
        "brightness": saved["brightness"] if saved else 5,
        "process_log": []
    })

# --- 5. UI ENGINE (HD Gloss & Visualizer Style) ---
accent = st.session_state.accent
bright_val = (11 - st.session_state.brightness) / 10
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, {bright_val}); z-index: -1; transition: 0.3s;
    }}
    [data-testid="stAppViewContainer"] {{ background: url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; }}
    h1, h2, h3, label, p {{ color: #FFFFFF !important; text-shadow: 0px 0px 15px rgba(0,0,0,1), 2px 2px 5px rgba(0,0,0,1) !important; font-weight: 800 !important; }}
    .glass {{ background: rgba(0, 8, 20, 0.92); backdrop-filter: blur(55px); border: 1px solid {accent}55; border-radius: 20px; padding: 25px; }}
    .neural-console {{ 
        background: rgba(0,0,0,0.7); border: 1px solid {accent}33; padding: 12px; border-radius: 10px;
        font-family: 'Courier New', monospace; color: {accent}; font-size: 0.8rem; line-height: 1.4; margin-top: 15px;
    }}
    .stButton>button {{ border: 2px solid {accent}aa !important; background: {accent}22 !important; color: white !important; font-weight: 900 !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. NAVIGATION & LUMINA ---
st.markdown('<div class="glass" style="padding: 15px; margin-bottom: 25px;">', unsafe_allow_html=True)
c_nav, c_bright = st.columns([0.7, 0.3])
with c_nav:
    nc = st.columns(7)
    nav_icons = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav_icons):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
with c_bright:
    new_bright = st.slider("🔅 LUMINA", 1, 10, st.session_state.brightness)
    if new_bright != st.session_state.brightness:
        st.session_state.brightness = new_bright
        save_data(); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 HYPER-SYNTH VISUALIZER</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VISION PROMPT:", placeholder="Banan-lejon...")
    
    if st.button("🚀 EXEKVERA NEURAL PIPELINE", use_container_width=True):
        if user_p:
            console_area = st.empty()
            with st.status("Neural Connection Established...") as status:
                # STEP 1: LOGIC ANALYSIS
                st.session_state.process_log = [f"› [{datetime.now().strftime('%H:%M:%S')}] ANALYZING INPUT: '{user_p}'"]
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                status.update(label="Llama-3 expanderar visionen...")
                raw_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand this to a cinematic 8k prompt: {user_p}. Only output the prompt."})
                clean_p = nuclear_clean("".join(list(raw_llm)))
                
                st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] PROMPT OPTIMIZED VIA LLAMA-3.")
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                # STEP 2: DIFFUSION
                status.update(label="FLUX.1 genererar pixlar...")
                st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] STARTING LATENT DIFFUSION (FLUX ENGINE)")
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                flux_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": clean_p})
                url = sanitize_url(flux_res)
                
                if url:
                    st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] RENDERING COMPLETE. WRITING TO SHIELD ARCHIVE.")
                    console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    save_data()
                    status.update(label="Pipeline Successful!", state="complete")
                    st.rerun()
        else: st.error("Prompt missing.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SÄTT SOM BAKGRUND"): 
            st.session_state.wallpaper = st.session_state.last_img
            save_data(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if not st.session_state.library: st.info("Archive empty.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']
                    save_data(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)





















































































































































