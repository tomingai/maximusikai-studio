import streamlit as st
import replicate
import os
import json
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "10.9.1"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. SÄKRAD REPLICATE-MOTOR (Regel 21: Auto-Fix) ---
def safe_replicate_run(model, input_data):
    try:
        # Försök 1: Fullständig trimning
        return replicate.run(model, input=input_data)
    except Exception as e:
        # Försök 2: Strippa parametrar vid fel (t.ex. seed/format-konflikt)
        clean_input = {"prompt": input_data.get("prompt", "")}
        try:
            return replicate.run(model, input=clean_input)
        except:
            return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Cinematic", "enhance_lvl": 0.7
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 15, 0.9); backdrop-filter: blur(45px); border: 1px solid {accent}44; border-radius: 25px; padding: 25px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; color: white !important; background: {accent}22 !important; border-radius: 12px; height: 3.5rem; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. SYNTH: MODIFIERAD FÖR STABILITET ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STABILIZER v{VERSION}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.7, 0.3])
    user_p = c1.text_input("VISION:", placeholder="Beskriv din vision...")
    st.session_state.style = c2.selectbox("STIL:", ["Cinematic", "Cyberpunk", "Photorealistic", "Digital Art"])

    t1, t2 = st.columns(2)
    st.session_state.enhance_lvl = t1.slider("AI KREATIVITET", 0.0, 1.0, 0.7)
    aspect = t2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"])

    if st.button("🚀 EXEKVERA"):
        if user_p:
            with st.status("Neural process...") as status:
                # Prompt Expansion
                final_p = user_p
                if st.session_state.enhance_lvl > 0.1:
                    status.update(label="Llama-3 trimmar prompt...")
                    instr = f"Professional {st.session_state.style} prompt: {user_p}"
                    res_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": instr})
                    final_p = "".join(list(res_llm))
                
                # Flux Run (Säkrad)
                status.update(label="Flux genererar...")
                flux_res = safe_replicate_run(
                    "black-forest-labs/flux-schnell", 
                    {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x")}
                )
                
                if flux_res:
                    url = str(flux_res[0]) if isinstance(flux_res, list) else str(flux_res)
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p})
                    st.rerun()
        else: st.error("Skriv en prompt.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img)
        if st.button("🖼 ANVÄND BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)







































































