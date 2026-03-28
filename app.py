import streamlit as st
import replicate
import os
import json
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.0.1"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. URL-SANITIZER & MOTOR (Regel 21 & 12) ---
def sanitize_url(output):
    """Extraherar en ren URL-sträng från Replicates utdata"""
    if isinstance(output, list) and len(output) > 0:
        return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        return sanitize_url(res)
    except Exception as e:
        # Fallback vid fel
        try:
            res = replicate.run(model, input={"prompt": input_data.get("prompt", "")})
            return sanitize_url(res)
        except:
            return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "hd_mode": True
    })

# --- 4. UI ENGINE (HD Gloss) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.96)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 15, 0.95); backdrop-filter: blur(50px); border: 1px solid {accent}55; border-radius: 30px; padding: 30px; }}
    .stButton>button {{ border: 1px solid {accent}77 !important; color: white !important; background: {accent}22 !important; border-radius: 15px; height: 4rem; font-weight: 900; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. SYNTH: HD PRECISION FIX ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:{accent}; text-align:center; font-size:1.2rem; letter-spacing:10px;'>ULTRA-HD SYNTH ENGINE v{VERSION}</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.7, 0.3])
    user_p = c1.text_input("VISION (HD-READY):", placeholder="Beskriv ditt mästerverk...")
    st.session_state.style = c2.selectbox("VISUELL STIL:", ["Photorealistic", "Cinematic 8K", "Macro Photography"])

    t1, t2 = st.columns(2)
    st.session_state.hd_mode = t1.toggle("ACTIVATE ULTRA-HD", value=st.session_state.hd_mode)
    aspect = t2.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "21:9"])

    if st.button("🚀 EXEKVERA NEURAL HD-SYNTES", use_container_width=True):
        if user_p:
            with st.status("Neural HD-rendering...") as status:
                # Steg 1: HD-Expansion
                final_p = user_p
                if st.session_state.hd_mode:
                    status.update(label="Llama-3 injicerar HD-parametrar...")
                    hd_instr = f"Professional {st.session_state.style} prompt. 8k, highly detailed, sharp focus: {user_p}"
                    res_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": hd_instr})
                    final_p = "".join(list(res_llm))
                
                # Steg 2: FLUX HD Run med Sanitizer
                status.update(label="FLUX renderar pixlar...")
                url = safe_replicate_run(
                    "black-forest-labs/flux-schnell", 
                    {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x")}
                )
                
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
        else: st.error("Skriv in en vision.")

    if st.session_state.last_img:
        st.divider()
        # Säker visning av URL
        st.image(str(st.session_state.last_img), caption=f"HD-RESULTAT | {st.session_state.style}")
        if st.button("🖼 ANVÄND SOM BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)








































































