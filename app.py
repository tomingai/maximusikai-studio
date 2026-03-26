import streamlit as st
import replicate
import os
import time

# --- 1. CORE SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI FULL CONSOLE", page_icon="🎚️", layout="wide", initial_sidebar_state="collapsed")

# Start-bakgrund
STUDIO_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "app_bg" not in st.session_state: st.session_state.app_bg = STUDIO_BG
if "user_units" not in st.session_state: st.session_state.user_units = 10

# --- 2. THE CLEAN GLASS ENGINE (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com');

    /* Dölj sidomenyn helt via CSS */
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}

    /* Bakgrunden täcker allt */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url("{st.session_state.app_bg}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-position: center !important;
    }}

    /* TOTAL TRANSPARENS PÅ INPUTS */
    textarea, input, div[data-baseweb="select"], .stSelectbox div {{
        background-color: rgba(255,255,255,0.02) !important;
        backdrop-filter: blur(20px) !important;
        color: #00f2ff !important;
        border: 1px solid rgba(0, 242, 255, 0.4) !important;
        font-family: 'Share Tech Mono', monospace !important;
        border-radius: 0px !important;
    }}

    /* TRANSPARENTA KNAPPAR */
    .stButton>button {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: #fff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(10px);
        font-family: 'Share Tech Mono';
        text-transform: uppercase;
        width: 100%;
        height: 50px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        border: 1px solid #00f2ff !important;
        background: rgba(0, 242, 255, 0.1) !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
    }}

    /* TYPOGRAFI */
    h1, h2, h3, p, label {{
        color: white !important;
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase;
        text-shadow: 2px 2px 5px #000;
    }}
    
    .console-header {{
        font-size: 4rem; font-weight: 900; text-align: center;
        letter-spacing: 15px; margin: 40px 0;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.8);
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. MAIN INTERFACE ---
st.markdown('<div class="console-header">MAXIMUSIKAI</div>', unsafe_allow_html=True)

# Status Rad
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    artist_id = st.text_input("ID_CALLSIGN:", "ANONYM").upper()
with c2:
    st.markdown(f"<h3 style='margin-top:35px;'>UNITS: {st.session_state.user_units}</h3>", unsafe_allow_html=True)
with c3:
    if st.button("🔄 RESET_CONSOLE", use_container_width=True):
        st.session_state.app_bg = STUDIO_BG
        st.rerun()

st.divider()

# Sektion: Input Engine
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    prompt = st.text_area("VISION_PARAMETERS", placeholder="ENTER NEURAL PROMPT...")
with col_in2:
    aspect = st.selectbox("RATIO", ["1:1", "16:9", "9:16"])
    if st.button("🔥 EXECUTE_SYNTHESIS", use_container_width=True):
        if st.session_state.user_units > 0:
            with st.status("SYNTHESIZING..."):
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect})
                img_url = str(img[0] if isinstance(img, list) else img)
                st.session_state.gallery.append({"user": artist_id, "url": img_url, "name": prompt})
                st.session_state.user_units -= 1
                st.rerun()

st.divider()

# Sektion: Data Vault (Grid)
if st.session_state.gallery:
    st.markdown("### 📚 NEURAL_DATA_VAULT")
    grid = st.columns(3)
    for i, item in enumerate(reversed(st.session_state.gallery)):
        with grid[i % 3]:
            st.image(item["url"])
            c_a, c_b = st.columns(2)
            if c_a.button("SET_BG", key=f"bg_{i}"):
                st.session_state.app_bg = item["url"]
                st.rerun()
            if c_b.button("ANIMATE", key=f"vid_{i}"):
                with st.spinner("Luma_Engine..."):
                    vid = replicate.run("luma-ai/luma-dream-machine", input={"image_url": item["url"]})
                    st.video(str(vid))


