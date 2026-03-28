import streamlit as st
import replicate
import os
import json
import traceback
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "10.8.0"
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
    with open(DB_FILE, "w") as f: json.dump(state_data, f)

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
    except Exception as e:
        st.error(f"Neural Error: {str(e)[:50]}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    saved = load_system_state()
    st.session_state.update({
        "page": "SYNTH",
        "library": saved.get("library", []) if saved else [],
        "accent": saved.get("accent", "#00f2ff") if saved else "#00f2ff",
        "wallpaper": saved.get("wallpaper", "https://images.unsplash.com") if saved else "https://images.unsplash.com",
        "last_img": None,
        "enhance": False
    })

# --- 4. UI ENGINE (Hyper-Synth Look) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 15, 0.85); backdrop-filter: blur(45px); border: 1px solid {accent}33; border-radius: 25px; padding: 30px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: white !important; background: {accent}11 !important; border-radius: 15px; height: 3.5rem; font-weight: bold; transition: 0.4s; }}
    .stButton>button:hover {{ background: {accent}33 !important; box-shadow: 0 0 25px {accent}55; transform: translateY(-2px); }}
    .locked-btn button {{ opacity: 0.15 !important; cursor: not-allowed !important; filter: grayscale(1); }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION (LOCKED MODE v2) ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
nav_cols = st.columns(7)
# SYNTH och ARKIV är nu de enda öppna modulerna
nav_config = [
    ("🏠", "DESKTOP", True), ("🪄", "SYNTH", False), ("🎧", "AUDIO", True), 
    ("🎬", "MOVIE", True), ("📚", "ARKIV", False), ("🖼", "ENGINE", True), ("⚙️", "SYSTEM", True)
]

for i, (icon, target, is_locked) in enumerate(nav_config):
    if is_locked:
        with nav_cols[i]:
            st.markdown('<div class="locked-btn">', unsafe_allow_html=True)
            st.button(icon, key=f"lock_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if nav_cols[i].button(icon, key=f"active_{target}"):
            st.session_state.page = target
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:5px;'>🪄 HYPER-SYNTH STATION</h2>", unsafe_allow_html=True)
    
    # Förbättrade funktioner: Inställningar
    c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
    with c1:
        user_p = st.text_input("VISION PROMPT (SV/EN):", placeholder="En cyberpunk-samuraj i regnet...")
    with c2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2"], index=1)
    with c3:
        st.session_state.enhance = st.toggle("AI ENHANCE", value=st.session_state.enhance, help="Använder Llama-3 för att bygga ut din prompt till 8K kvalitet.")

    if st.button("🚀 STARTA NEURAL SYNTES", use_container_width=True):
        if user_p:
            with st.status("Kopplar upp mot neurala nätverk...") as status:
                # Steg 1: Enhance / Translate
                final_p = user_p
                enhance_instr = "Expand this into a highly detailed 8K image prompt: " if st.session_state.enhance else "Translate this to English for image generation: "
                
                trans_res = safe_replicate_run("LLM", {
                    "prompt": f"{enhance_instr} {user_p}",
                    "max_new_tokens": 150
                })
                if trans_res: final_p = "".join(list(trans_res))
                
                # Steg 2: FLUX Generation
                status.update(label=f"Genererar {aspect} vision...")
                res = safe_replicate_run("FLUX", {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x") if aspect != "1:1" else "1:1"})
                
                if res:
                    url = get_url(res)
                    st.session_state.last_img = url
                    st.session_state.library.append({
                        "type": "IMG", "url": url, "prompt": user_p, "aspect": aspect, 
                        "ts": datetime.now().strftime("%H:%M")
                    })
                    save_system_state()
                    status.update(label="Syntes klar!", state="complete")
                    st.rerun()
        else:
            st.error("Skriv in en vision först.")

    # Display & Snabbval
    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SET AS SYSTEM WALLPAPER"):
            st.session_state.wallpaper = st.session_state.last_img
            save_system_state()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 SYSTEM ARCHIVE")
    if not st.session_state.library:
        st.info("Arkivet är tomt. Skapa något i SYNTH först.")
    else:
        # Visa galleri i rutnät
        cols = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with cols[i % 3]:
                st.image(item['url'], use_column_width=True)
                st.caption(f"Prompt: {item['prompt'][:30]}...")
                if st.button(f"Sätt som bakgrund", key=f"ark_wall_{i}"):
                    st.session_state.wallpaper = item['url']
                    save_system_state()
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Footer info
st.markdown(f"<p style='text-align:center; opacity:0.3;'>MAXIMUSIK AI OS v{VERSION} | MODULAR LOCK ACTIVE</p>", unsafe_allow_html=True)





































































