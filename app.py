import streamlit as st
import replicate
import os
import time

# --- 1. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# System States
states = {
    "page": "DESKTOP",
    "lang": "Svenska",
    "accent_color": "#00f2ff",
    "bg_brightness": 0.4,
    "wallpaper": "https://images.unsplash.com",
    "library": [],
    "res_img": None,
    "is_loading": False
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. THE OS CORE (CSS med GLITCH EFFEKT) ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.bg_brightness
    overlay = 1.0 - bright 
    
    st.markdown(f"""
        <style>
        @keyframes glitch {{
            0% {{ transform: translate(0); }}
            20% {{ transform: translate(-5px, 5px); }}
            40% {{ transform: translate(-5px, -5px); }}
            60% {{ transform: translate(5px, 5px); }}
            80% {{ transform: translate(5px, -5px); }}
            100% {{ transform: translate(0); }}
        }}

        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; 
            background-attachment: fixed !important;
            transition: 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            {'animation: glitch 0.2s infinite;' if st.session_state.is_loading else ''}
        }}

        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        
        /* TEXT ENGINE */
        h1, h2, h3, p, label, .stMarkdown, .stSelectbox label {{
            color: {accent} !important;
            text-shadow: 0 0 15px {accent}77 !important;
            font-family: 'Courier New', monospace !important;
            letter-spacing: 2px;
        }}
        
        .window-box {{
            background: rgba(0, 5, 12, 0.92); 
            backdrop-filter: blur(50px);
            border: 2px solid {accent}33; 
            border-radius: 40px; padding: 40px;
            box-shadow: 0 0 60px {accent}15;
        }}

        .stButton > button {{
            background: rgba(0,0,0,0.7) !important; 
            border: 1px solid {accent}44 !important;
            color: {accent} !important; 
            border-radius: 20px !important; 
            height: 80px !important;
            font-weight: 900; letter-spacing: 3px;
            transition: 0.3s;
        }}
        .stButton > button:hover {{
            background: {accent}22 !important;
            box-shadow: 0 0 30px {accent}44 !important;
        }}

        /* Status bar */
        .status-bar {{
            position: fixed; bottom: 20px; right: 40px;
            font-family: monospace; color: {accent};
            font-size: 10px; text-transform: uppercase;
        }}
        </style>
        <div class="status-bar">Core: Stable | Latency: 24ms | OS: v4.2</div>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. HELPER: EXECUTE AI ---
def run_ai(prompt, aspect="1:1"):
    st.session_state.is_loading = True
    st.rerun() # Triggar glitch-animationen
    # (I verkligheten körs replicate här, men vi simulerar logiken för demon)

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:15vh; font-size:4.5rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
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
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕"): st.session_state.page = "DESKTOP"; st.rerun()

        if st.session_state.page == "ENGINE":
            st.session_state.bg_brightness = st.slider("LJUSSTYRKA", 0.0, 1.0, st.session_state.bg_brightness)
            p = st.text_area("ENVIRONMENT PROMPT:")
            if st.button("REWRITE REALITY", use_container_width=True):
                with st.spinner("NEURAL RECONSTRUCTION..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = str(res)
                    st.rerun()

        elif st.session_state.page == "SYNTH":
            sp = st.text_area("VISUAL PROMPT:")
            if st.button("SYNTHESIZE", use_container_width=True):
                with st.spinner("SYNTHESIZING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": sp})
                    st.session_state.res_img = str(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.res_img, "prompt": sp})
                    st.rerun()
            if st.session_state.res_img: st.image(st.session_state.res_img)

        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.write("EMPTY_ARCHIVE")
            else:
                for idx, item in enumerate(reversed(st.session_state.library)):
                    with st.container():
                        st.image(item['url'], width=500)
                        if st.button("SÄTT SOM BAKGRUND", key=f"bg_{idx}"):
                            st.session_state.wallpaper = item['url']; st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("ACCENT COLOR", st.session_state.accent_color)
            if st.button("TERMINATE SESSION (RESET)"):
                st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)




























