import streamlit as st
import replicate
import os
import json
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "10.8.2"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SYSTEMFUNKTIONER (Regel 8, 12, 21) ---
def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        return str(res.url) if hasattr(res, 'url') else str(res)
    except: return str(res)

def save_system_state():
    state_data = {
        "library": st.session_state.get("library", []),
        "accent": st.session_state.get("accent", "#00f2ff"),
        "wallpaper": st.session_state.get("wallpaper", ""),
        "lang": st.session_state.get("lang", "SV")
    }
    try:
        with open(DB_FILE, "w") as f: json.dump(state_data, f)
    except: pass

def load_system_state():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return None
    return None

def safe_replicate_run(model_alias, input_data):
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "LLM": "meta/meta-llama-3-8b-instruct"
    }
    target = models.get(model_alias, model_alias)
    try:
        return replicate.run(target, input=input_data)
    except: return None

# --- 3. INITIALISERING (Säkerställer alla states) ---
if "page" not in st.session_state:
    saved = load_system_state()
    st.session_state.update({
        "page": "SYNTH",
        "library": saved.get("library", []) if saved else [],
        "accent": saved.get("accent", "#00f2ff") if saved else "#00f2ff",
        "wallpaper": saved.get("wallpaper", "https://images.unsplash.com") if saved else "https://images.unsplash.com",
        "last_img": None,
        "enhance": True, # Standarvärde ON för testet
        "lang": "SV"
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 8, 20, 0.85); backdrop-filter: blur(45px); border: 1px solid {accent}33; border-radius: 25px; padding: 30px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: white !important; background: {accent}11 !important; border-radius: 15px; height: 3.5rem; font-weight: bold; transition: 0.4s; width: 100%; }}
    .stButton>button:hover {{ background: {accent}33 !important; box-shadow: 0 0 25px {accent}55; }}
    .locked-btn button {{ opacity: 0.15 !important; cursor: not-allowed !important; filter: grayscale(1); }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
nav_cols = st.columns(7)
nav_config = [("🏠", "DESKTOP", True), ("🪄", "SYNTH", False), ("🎧", "AUDIO", True), ("🎬", "MOVIE", True), ("📚", "ARKIV", False), ("🖼", "ENGINE", True), ("⚙️", "SYSTEM", True)]
for i, (icon, target, is_locked) in enumerate(nav_config):
    if is_locked:
        nav_cols[i].markdown('<div class="locked-btn">', unsafe_allow_html=True)
        nav_cols[i].button(icon, key=f"lock_{i}")
        nav_cols[i].markdown('</div>', unsafe_allow_html=True)
    else:
        if nav_cols[i].button(icon, key=f"active_{target}"):
            st.session_state.page = target
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:3px;'>🪄 HYPER-SYNTH STATION</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
    user_p = c1.text_input("DIN VISION (SVENSKA GÅR BRA):", placeholder="T.ex. En robot som dricker kaffe i regnet...")
    aspect = c2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)
    st.session_state.enhance = c3.toggle("AI ENHANCE", value=st.session_state.enhance)

    if st.button("🚀 KÖR NEURAL SYNTES", use_container_width=True):
        if user_p:
            with st.status("Neural motor startar...") as status:
                # Steg 1: AI Enhance / Translation via Llama-3
                final_p = user_p
                status.update(label="Ansluter till Llama-3 för prompt-expansion...")
                prompt_instr = f"Expand this into a professional, highly detailed cinematic 8k image prompt in English. Be creative with lighting and textures: {user_p}"
                
                trans_data = safe_replicate_run("LLM", {"prompt": prompt_instr, "max_new_tokens": 200})
                if trans_data:
                    final_p = "".join(list(trans_data))
                
                # Steg 2: FLUX Generation
                status.update(label=f"Genererar vision: {final_p[:40]}...")
                res = safe_replicate_run("FLUX", {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x")})
                
                if res:
                    url = get_url(res)
                    st.session_state.last_img = url
                    st.session_state.library.append({
                        "type": "IMG", "url": url, "prompt": user_p, "enhanced_prompt": final_p, 
                        "ts": datetime.now().strftime("%H:%M")
                    })
                    save_system_state()
                    status.update(label="Syntes klar!", state="complete")
                    st.rerun()
        else:
            st.error("Vision saknas. Skriv något först.")
    
    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, caption="Senaste neurala resultatet")
        if st.button("🖼 SÄTT SOM BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img
            save_system_state(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 DITT ARKIV")
    if not st.session_state.library:
        st.info("Inga bilder sparade än.")
    else:
        cols = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with cols[i % 3]:
                st.image(item['url'], use_column_width=True)
                st.caption(f"Prompt: {item['prompt']}")
                if st.button(f"Använd bakgrund", key=f"wall_{i}"):
                    st.session_state.wallpaper = item['url']
                    save_system_state(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"<p style='text-align:center; opacity:0.2;'>MAXIMUSIK AI OS v{VERSION} | ENHANCE BRIDGE ACTIVE</p>", unsafe_allow_html=True)






































































