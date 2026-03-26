import streamlit as st
import replicate
import os
import random

# --- 1. HJÄLPFUNKTIONER ---
def get_url(res):
    """Säkerställer att vi får en sträng-URL från Replicates output"""
    if isinstance(res, list) and len(res) > 0:
        return str(res[0])
    return str(res)

def enhance_prompt(user_input):
    styles = ["8k cinematic", "hyper-detailed", "neon lighting", "volumetric fog", "masterpiece", "synthwave aesthetic"]
    if not user_input:
        subjects = ["Cyberpunk city", "Deep space nebula", "Interstellar portal", "Android DJ", "Alien crystal world"]
        user_input = random.choice(subjects)
    return f"{user_input}, {', '.join(random.sample(styles, 3))}"

# --- 2. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "library": [],
    "res_img": None,
    "res_audio": None,
    "input_text": "",
    "accent_color": "#00f2ff"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 3. CSS ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        .window-box {{
            background: rgba(0, 5, 12, 0.95);
            backdrop-filter: blur(40px);
            border: 1px solid {accent}44;
            border-radius: 40px; padding: 40px; color: white;
            box-shadow: 0 50px 100px rgba(0,0,0,0.8);
        }}
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid {accent}33 !important;
            color: white !important; border-radius: 20px !important; height: 100px !important;
            font-size: 1.1rem !important; transition: 0.4s !important;
        }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 30px {accent}44 !important; transform: scale(1.05); }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown("<h1 style='text-align:center; color:white; letter-spacing:15px; padding-top:10vh; text-shadow: 0 0 20px #00f2ff;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.page = target; st.rerun()

# --- 5. WINDOWS ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.title(f"// {st.session_state.page}")
        if h2.button("✕", key="close_btn"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- SYNTH (Bilder) ---
        if st.session_state.page == "SYNTH":
            col1, col2 = st.columns([0.7, 0.3])
            with col2:
                if st.button("🎲 SLUMPA"): 
                    st.session_state.input_text = enhance_prompt(""); st.rerun()
            u_input = col1.text_area("VAD SKALL VI SKAPA?", value=st.session_state.input_text)
            
            if st.button("EXECUTE NEURAL SYNTH", use_container_width=True):
                enhanced = enhance_prompt(u_input)
                with st.spinner("Neural Sync..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": enhanced})
                    url = get_url(res) # HÄR FIXAR VI FELET
                    st.session_state.res_img = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": enhanced})
                    st.rerun()
            if st.session_state.res_img: 
                st.image(st.session_state.res_img)

        # --- AUDIO (Musik) ---
        elif st.session_state.page == "AUDIO":
            ap = st.text_input("BESKRIV BEATET:", value=st.session_state.input_text)
            if st.button("COMPOSE MUSIC", use_container_width=True):
                final_p = ap if ap else "Epic dark synthwave beat"
                with st.spinner("Komponerar..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": final_p, "duration": 10})
                    st.session_state.res_audio = res
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": final_p})
                    st.rerun()
            if st.session_state.res_audio: st.audio(st.session_state.res_audio)

        # --- LIBRARY (Arkiv) ---
        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.info("Arkivet är tomt.")
            else:
                for idx, item in enumerate(reversed(st.session_state.library)):
                    with st.expander(f"{item['type'].upper()}: {item['prompt'][:50]}..."):
                        if item['type'] == "image":
                            st.image(item['url'], use_container_width=True)
                            if st.button("SÄTT SOM BAKGRUND", key=f"bg_{idx}"):
                                st.session_state.wallpaper = item['url']; st.rerun()
                        else: st.audio(item['url'])

        # --- ENGINE (Miljö/Bakgrund) ---
        elif st.session_state.page == "ENGINE":
            ep = st.text_input("MILJÖ-PROMPT:", value=st.session_state.input_text)
            if st.button("UPDATE REALITY"):
                enhanced = enhance_prompt(ep)
                with st.spinner("Rewriting Reality..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": enhanced, "aspect_ratio": "16:9"})
                    url = get_url(res) # FIX HÄR OCKSÅ
                    st.session_state.wallpaper = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": enhanced})
                    st.rerun()

        # --- SYSTEM (Inställningar) ---
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("UI ACCENT FÄRG:", st.session_state.accent_color)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


























