import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.8-STABLE"
st.set_page_config(page_title=f"MAXIMUSIK AI OS {VERSION}", layout="wide", initial_sidebar_state="collapsed")

# Säkerställ API-Token
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
elif "REPLICATE_API_TOKEN" in os.environ:
    pass # Redan satt i miljö
else:
    st.error("API-TOKEN SAKNAS I SECRETS")

# --- 2. SÄKRA MOTORER ---
def safe_replicate_run(model, input_data):
    try:
        # Använd Replicate direkt med felhantering
        return replicate.run(model, input=input_data)
    except Exception as e:
        st.error(f"NEURAL ERROR: {str(e)}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com"
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.95), rgba(0,0,0,0.98)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 20, 0.92); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: white !important; background: {accent}11 !important; border-radius: 12px; height: 3.5rem; font-weight: bold; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, is_locked) in enumerate(nav):
    if not is_locked:
        if nc[i].button(icon, key=f"nav_{target}"):
            st.session_state.page = target; st.rerun()
    else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VISION PROMPT:", placeholder="Bananer som förvandlas till ett lejon...")
    
    if st.button("🚀 EXEKVERA"):
        if user_p:
            with st.status("Neural motor startar...") as status:
                # Steg 1: LLM expansion
                status.update(label="Ansluter till Llama-3...")
                prompt_res = safe_replicate_run("meta/meta-llama-3-8b-instruct", {"prompt": f"Expand this to a cinematic 8k prompt: {user_p}"})
                final_p = "".join(list(prompt_res)) if prompt_res else user_p
                
                # Steg 2: FLUX rendering
                status.update(label="Flux genererar pixlar...")
                flux_res = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": final_p})
                
                if flux_res:
                    url = str(flux_res[0]) if isinstance(flux_res, list) else str(flux_res)
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p})
                    status.update(label="Klar!", state="complete")
                    st.rerun()
        else: st.error("Skriv något i prompt-rutan.")
        
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 ANVÄND BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if not st.session_state.last_img and st.session_state.library:
        st.session_state.last_img = st.session_state.library[-1]['url']
        
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=400)
        if st.button("🔍 ANALYSERA"):
            res = safe_replicate_run("lucataco/moondream2", {"image": st.session_state.last_img, "prompt": "Describe this image."})
            st.info(res)
    else: st.info("Skapa en bild först.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 ARKIV")
    if not st.session_state.library: st.info("Tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'])
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)










































































