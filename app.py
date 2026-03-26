import streamlit as st
import replicate
import os
import time

# --- 1. PRO CONFIG ---
st.set_page_config(page_title="MAXIMUSIKAI PREMIER", layout="wide", initial_sidebar_state="collapsed")

# --- 2. THE PREMIER ENGINE (STEROID-CSS) ---
def apply_premier_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* DARK FOUNDATION */
        .stApp {
            background-color: #030303 !important;
            color: #999 !important;
            font-family: 'Inter', sans-serif;
        }

        /* HIDE STREAMLIT JUNK */
        header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] { visibility: hidden; height: 0; }
        [data-testid="stAppViewBlockContainer"] { padding: 0 !important; }

        /* PREMIER WORKSPACE LAYOUT */
        .main-container { display: flex; height: 100vh; }
        
        .sidebar-nav {
            width: 70px; background: #000; border-right: 1px solid #111;
            display: flex; flex-direction: column; align-items: center; padding: 20px 0;
        }

        /* MODULAR PANELS (THE INSTRUMENT LOOK) */
        div[data-testid="stVerticalBlock"] > div {
            background: #080808 !important;
            border: 1px solid #141414 !important;
            border-radius: 2px; padding: 30px; margin-bottom: 20px;
        }
        
        /* PRO INPUTS */
        textarea, input {
            background-color: #000 !important;
            color: #00f2ff !important;
            border: 1px solid #181818 !important;
            border-radius: 0px !important;
            font-family: 'JetBrains Mono' !important;
            font-size: 13px !important;
            padding: 15px !important;
        }
        textarea:focus { border-color: #00f2ff !important; box-shadow: 0 0 10px rgba(0,242,255,0.1); }

        /* BUTTONS (INDUSTRIAL MINIMALISM) */
        .stButton>button {
            background: #fff !important;
            color: #000 !important;
            border-radius: 0px !important;
            font-weight: 800 !important;
            font-family: 'Inter' !important;
            text-transform: uppercase;
            letter-spacing: 3px;
            font-size: 10px !important;
            height: 45px !important;
            border: none !important;
            transition: 0.2s ease;
        }
        .stButton>button:hover {
            background: #00f2ff !important;
            box-shadow: 0 0 20px rgba(0,242,255,0.4);
        }

        /* TYPOGRAPHY */
        .studio-title {
            font-family: 'Inter'; font-weight: 800; font-size: 1.2rem;
            color: #fff; letter-spacing: -1px; margin-bottom: 2px;
        }
        .studio-sub {
            font-family: 'JetBrains Mono'; font-size: 9px; color: #444;
            letter-spacing: 2px; text-transform: uppercase; margin-bottom: 30px;
        }
        
        /* VU METER ANIMATION */
        .vu-container { display: flex; gap: 3px; height: 20px; margin-top: 10px; }
        .vu-bar { width: 3px; background: #222; }
        .vu-bar.active { background: #00f2ff; animation: pulse 0.5s infinite alternate; }
        @keyframes pulse { from { opacity: 0.2; } to { opacity: 1; } }
        </style>
    """, unsafe_allow_html=True)

# --- 3. STUDIO INTERFACE ---
apply_premier_ui()

# Custom HUD
with st.container():
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<div class='studio-title'>MAXIMUSIKAI // PREMIER STUDIO</div>", unsafe_allow_html=True)
        st.markdown("<div class='studio-sub'>NEURAL CORE ENGINE v4.2</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='text-align:right; font-family:JetBrains Mono; font-size:10px; color:#00f2ff;'>SYNC: OPTIMAL<br>UNITS: 99.9</div>", unsafe_allow_html=True)

# Main Workspace
col_ctrl, col_view = st.columns([1, 1.8], gap="large")

with col_ctrl:
    st.markdown("<label>SOURCE_PROMPT</label>", unsafe_allow_html=True)
    prompt = st.text_area("", placeholder="Enter neural parameters...", height=250, label_visibility="collapsed")
    
    st.markdown("<label>ASPECT_RATIO</label>", unsafe_allow_html=True)
    ratio = st.selectbox("", ["1:1", "16:9", "9:16"], label_visibility="collapsed")
    
    st.markdown("<label>SYNTH_QUALITY</label>", unsafe_allow_html=True)
    quality = st.select_slider("", options=["DRAFT", "PRO", "ULTRA"], label_visibility="collapsed")
    
    if st.button("EXECUTE SYNTHESIS"):
        if prompt:
            with st.status("ENGINE_SYNC..."):
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                # Förstärkt prompt för Pro-look
                p = f"{prompt}, high-end cinematic, architectural photography, hyper-detailed"
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p, "aspect_ratio": ratio})
                st.session_state.pro_res = res
                st.rerun()

with col_view:
    st.markdown("<label>LIVE_PREVIEW</label>", unsafe_allow_html=True)
    if "pro_res" in st.session_state:
        st.image(st.session_state.pro_res, use_container_width=True)
        # VU-meter simulation
        st.markdown('<div class="vu-container">' + ''.join(['<div class="vu-bar active"></div>']*20) + '</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="height:550px; background:#000; border:1px solid #111; display:flex; align-items:center; justify-content:center; color:#222; font-family:'JetBrains Mono'; font-size:11px; letter-spacing:3px;">
                AWAITING_SIGNAL_SOURCE
            </div>
        """, unsafe_allow_html=True)

# Secondary Row (Library)
st.markdown("<br><label>ASSET_VAULT</label>", unsafe_allow_html=True)
st.markdown("<div style='color:#222; font-size:10px; letter-spacing:1px;'>NO_LOCAL_ASSETS_FOUND</div>", unsafe_allow_html=True)


