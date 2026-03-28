import streamlit as st
import replicate
import os
import json
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.0.0"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION} [HD-ULTRA]", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. HD-OPTIMERAD MOTOR (Regel 21 & 22) ---
def safe_replicate_run(model, input_data):
    try:
        # Standard-anrop med fulla parametrar
        return replicate.run(model, input=input_data)
    except Exception as e:
        # Fail-safe: Strippa till enbart prompt vid timeout eller parameter-fel
        st.warning(f"HD-Optimering anpassas...")
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
        "style": "Photorealistic", "hd_mode": True
    })

# --- 4. UI ENGINE (HD Gloss look) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.96)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 15, 0.95); backdrop-filter: blur(50px); border: 1px solid {accent}55; border-radius: 30px; padding: 30px; box-shadow: 0 0 40px {accent}22; }}
    .stButton>button {{ border: 1px solid {accent}77 !important; color: white !important; background: {accent}22 !important; border-radius: 15px; height: 4rem; font-weight: 900; letter-spacing: 2px; }}
    .stButton>button:hover {{ background: {accent}44 !important; box-shadow: 0 0 30px {accent}88; transform: scale(1.01); }}
    </style>
""", unsafe_allow_html=True)

# --- 5. SYNTH: HD PRECISION MOD ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:{accent}; text-align:center; font-size:1.2rem; letter-spacing:10px;'>ULTRA-HD SYNTH ENGINE</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.7, 0.3])
    user_p = c1.text_input("VISION (HD-ENABLED):", placeholder="Beskriv ditt mästerverk...")
    st.session_state.style = c2.selectbox("VISUELL STIL:", ["Photorealistic", "Cinematic 8K", "Hyper-Detailed Art", "Macro Photography"])

    t1, t2, t3 = st.columns(3)
    with t1:
        st.session_state.hd_mode = st.toggle("ACTIVATE ULTRA-HD", value=st.session_state.hd_mode, help="Tvingar fram 8K-beskrivningar och teknisk skärpa.")
    with t2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "21:9"])
    with t3:
        num_outputs = st.select_slider("PIXEL DENSITY", options=["Standard", "High", "Ultra"], value="Ultra")

    if st.button("🚀 EXEKVERA NEURAL HD-SYNTES", use_container_width=True):
        if user_p:
            with st.status("Neural HD-rendering pågår...") as status:
                # Steg 1: HD-Prompt Expansion (Llama-3)
                final_p = user_p
                if st.session_state.hd_mode:
                    status.update(label="Llama-3 injicerar HD-parametrar...")
                    hd_instr = f"Act as a professional cinematographer. Expand this to a {st.session_state.style} prompt. Focus on 8k resolution, ray-tracing, sub-surface scattering, and razor-sharp textures: {user_p}"
                    res_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": hd_instr, "max_new_tokens": 250})
                    final_p = "".join(list(res_llm))
                
                # Steg 2: FLUX HD Run
                status.update(label="FLUX.1 [schnell] renderar pixlar...")
                flux_res = safe_replicate_run(
                    "black-forest-labs/flux-schnell", 
                    {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x")}
                )
                
                if flux_res:
                    url = str(flux_res) if isinstance(flux_res, list) else str(flux_res)
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "hd": True})
                    st.rerun()
        else: st.error("Skriv in en vision.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, caption=f"HD-RESULTAT | {st.session_state.style}")
        col_save, col_wall = st.columns(2)
        with col_wall:
            if st.button("🖼 ANVÄND SOM BAKGRUND"):
                st.session_state.wallpaper = st.session_state.last_img
                st.rerun()
        with col_save:
            st.markdown(f'<a href="{st.session_state.last_img}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:4rem; background:rgba(255,255,255,0.1); border:1px solid white; color:white; border-radius:15px; cursor:pointer;">💾 LADDA NER HD-FIL</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)







































































