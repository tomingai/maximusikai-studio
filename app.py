import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.6.0-PRECISION"
DB_FILE = "maximusik_history.json"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. DATA SHIELD (Spara/Ladda allt) ---
def save_data():
    try:
        data = {
            "library": st.session_state.get("library", []),
            "wallpaper": st.session_state.get("wallpaper", ""),
            "brightness": st.session_state.get("brightness", 5),
            "last_img": st.session_state.get("last_img", None),
            "style": st.session_state.get("style", "Photorealistic"),
            "enhance_lvl": st.session_state.get("enhance_lvl", 0.8)
        }
        with open(DB_FILE, "w") as f: json.dump(data, f)
    except: pass

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return None
    return None

# --- 3. MOTORER & CLEANER ---
def nuclear_clean(text):
    if not text: return ""
    clean = str(text).replace('"', '').replace("'", "").replace('\n', ' ')
    prefixes = ["Here is", "Prompt:", "Expanded:", "Sure", "The prompt is"]
    for p in prefixes:
        if p in clean: clean = clean.split(p)[-1]
    return clean.strip()

# --- 4. INITIALISERING ---
if "page" not in st.session_state:
    saved = load_data()
    st.session_state.update({
        "page": "SYNTH",
        "library": saved.get("library", []) if saved else [],
        "last_img": saved.get("last_img", None) if saved else None,
        "wallpaper": saved.get("wallpaper", "https://images.unsplash.com") if saved else "https://images.unsplash.com",
        "brightness": saved.get("brightness", 5) if saved else 5,
        "style": saved.get("style", "Photorealistic") if saved else "Photorealistic",
        "enhance_lvl": saved.get("enhance_lvl", 0.8) if saved else 0.8,
        "process_log": []
    })

# --- 5. UI ENGINE (HD Gloss) ---
accent = "#00f2ff"
bright_val = (11 - st.session_state.brightness) / 10
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, {bright_val}); z-index: -1; transition: 0.3s;
    }}
    [data-testid="stAppViewContainer"] {{ background: url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; }}
    h1, h2, h3, label, p {{ color: #FFFFFF !important; text-shadow: 0px 0px 15px rgba(0,0,0,1), 2px 2px 5px rgba(0,0,0,1) !important; font-weight: 800 !important; }}
    .glass {{ background: rgba(0, 8, 20, 0.92); backdrop-filter: blur(55px); border: 1.5px solid {accent}55; border-radius: 20px; padding: 25px; }}
    .neural-console {{ background: rgba(0,0,0,0.7); border: 1px solid {accent}33; padding: 12px; border-radius: 10px; font-family: monospace; color: {accent}; font-size: 0.8rem; }}
    .stButton>button {{ border: 2px solid {accent}aa !important; background: {accent}22 !important; color: white !important; font-weight: 900 !important; height: 3.5rem; }}
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
            if nc[i].button(icon, key=f"n_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
with c_bright:
    new_bright = st.slider("🔅 LUMINA", 1, 10, st.session_state.brightness)
    if new_bright != st.session_state.brightness:
        st.session_state.brightness = new_bright
        save_data(); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. MODUL: SYNTH PRECISION ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 PRECISION SYNTH STATION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VISION PROMPT:", placeholder="Banan-lejon...")
    
    # DETALJ-TRIMMARE
    t1, t2, t3 = st.columns(3)
    st.session_state.style = t1.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"], index=0)
    st.session_state.enhance_lvl = t2.slider("AI DEPTH (Kreativitet)", 0.0, 1.0, st.session_state.enhance_lvl)
    aspect = t3.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXEKVERA NEURAL PIPELINE", use_container_width=True):
        if user_p:
            console_area = st.empty()
            with st.status("Neural Connection Established...") as status:
                st.session_state.process_log = [f"› [{datetime.now().strftime('%H:%M:%S')}] ANALYZING INPUT..."]
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                # Step 1: Llama Expansion (Nu med Stil & Depth)
                status.update(label="Llama-3 expanderar visionen...")
                prompt_instr = f"Act as a professional cinematographer. Expand to a {st.session_state.style} 8k prompt. Focus on sharp textures and cinematic lighting. Depth level {st.session_state.enhance_lvl}: {user_p}"
                raw_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": prompt_instr})
                clean_p = nuclear_clean("".join(list(raw_llm)))
                
                st.session_state.process_log.append(f"› [{datetime.now().strftime('%H:%M:%S')}] PROMPT OPTIMIZED (Style: {st.session_state.style}).")
                console_area.markdown(f'<div class="neural-console">{"<br>".join(st.session_state.process_log)}</div>', unsafe_allow_html=True)
                
                # Step 2: Flux Render
                status.update(label="FLUX.1 genererar pixlar...")
                flux_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": clean_p, "aspect_ratio": aspect.replace(":", "x")})
                
                if flux_res:
                    url = str(flux_res) if not isinstance(flux_res, list) else str(flux_res[0])
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

# --- ARKIV-MODUL ---
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





















































































































































