import streamlit as st
import replicate
import os
from datetime import datetime

# --- 1. SYSTEM-KONFIGURATION ---
VERSION = "10.9.0"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. INITIALISERING (Säkrad med alla trimmare) ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH",
        "library": [],
        "accent": "#00f2ff",
        "wallpaper": "https://images.unsplash.com",
        "last_img": None,
        "enhance_level": 0.7, # Hur mycket AI ska brodera ut texten
        "style_preset": "Cinematic",
        "seed": -1 # -1 betyder slumpmässig
    })

# --- 3. UI ENGINE (Glasmorphism) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 8, 25, 0.9); backdrop-filter: blur(45px); border: 1px solid {accent}44; border-radius: 25px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; color: white !important; background: {accent}22 !important; border-radius: 12px; transition: 0.3s; width: 100%; }}
    .stButton>button:hover {{ background: {accent}44 !important; box-shadow: 0 0 15px {accent}77; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SYNTH: PRECISION CONTROL ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:3px;'>🪄 SYNTH PRECISION ENGINE</h2>", unsafe_allow_html=True)
    
    # RAD 1: Prompt & Stil
    c1, c2 = st.columns([0.7, 0.3])
    user_p = c1.text_input("VISION PROMPT (SV/EN):", placeholder="Beskriv din scen...")
    st.session_state.style_preset = c2.selectbox("STIL:", ["Cinematic", "Photorealistic", "Cyberpunk", "Oil Painting", "Vector Art"])

    # RAD 2: Finjustering (Trimmare)
    st.markdown("---")
    t1, t2, t3 = st.columns(3)
    
    with t1:
        st.session_state.enhance_level = st.slider("AI KREATIVITET (LLM)", 0.0, 1.0, 0.7, help="Högre värde ger mer detaljerade beskrivningar.")
    with t2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2"], index=1)
    with t3:
        st.session_state.seed = st.number_input("SEED (Frö)", value=-1, step=1, help="-1 ger unik bild varje gång. Lås för att behålla karaktär.")

    if st.button("🚀 KÖR PRECISIONS-SYNTES"):
        if user_p:
            with st.status("Neural trimning pågår...") as status:
                # Steg 1: Dynamisk Prompt-Expansion
                final_p = user_p
                if st.session_state.enhance_level > 0.1:
                    status.update(label="Llama-3 optimerar beskrivningen...")
                    instr = f"Act as a professional prompt engineer. Expand this to a {st.session_state.style_preset} 8k prompt. Creativity level {st.session_state.enhance_level}: {user_p}"
                    trans = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": instr, "max_new_tokens": 200})
                    final_p = "".join(list(trans))
                
                # Steg 2: FLUX med Trimmade Parametrar
                status.update(label=f"FLUX genererar {st.session_state.style_preset}...")
                flux_input = {
                    "prompt": final_p,
                    "aspect_ratio": aspect.replace(":", "x")
                }
                if st.session_state.seed != -1:
                    flux_input["seed"] = st.session_state.seed
                
                res = replicate.run("black-forest-labs/flux-schnell", input=flux_input)
                
                if res:
                    url = str(res[0]) if isinstance(res, list) else str(res)
                    st.session_state.last_img = url
                    st.session_state.library.append({"type": "IMG", "url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
        else:
            st.error("Ange en vision.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, caption=f"Resultat: {st.session_state.style_preset}")
        if st.button("🖼 SÄTT SOM BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)






































































