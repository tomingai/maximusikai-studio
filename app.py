import streamlit as st
import replicate
import os
import time

# --- 1. CORE SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI CONSOLE", page_icon="🎚️", layout="wide")

# Den ultimata studio-bakgrunden
STUDIO_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {"ANONYM": 10}
if "app_bg" not in st.session_state: st.session_state.app_bg = STUDIO_BG

# --- 2. STUDIO GLASS ENGINE (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com');

    /* Bakgrunden är allt */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.5)), url("{st.session_state.app_bg}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-position: center !important;
    }}

    /* Sidomeny i glas */
    [data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }}

    /* TOTAL TRANSPARENS PÅ INPUTS */
    textarea, input, div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.03) !important;
        backdrop-filter: blur(15px) !important;
        color: #00f2ff !important;
        border: 1px solid rgba(0, 242, 255, 0.3) !important;
        font-family: 'Share Tech Mono', monospace !important;
        border-radius: 0px !important;
    }}

    /* STUDIO BUTTONS */
    .stButton>button {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: #fff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(10px);
        font-family: 'Share Tech Mono';
        text-transform: uppercase;
        letter-spacing: 2px;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        border: 1px solid #00f2ff !important;
        background: rgba(0, 242, 255, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
    }}

    /* TYPOGRAFI */
    h1, h2, h3, p, label {{
        color: white !important;
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase;
    }}
    
    .console-header {{
        font-size: 4rem; font-weight: 900; text-align: center;
        letter-spacing: 12px; margin-bottom: 40px;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.6);
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (MISSION CONTROL) ---
with st.sidebar:
    st.markdown("## 🛰️ CONSOLE")
    u_id = st.text_input("USER_ID:", "ANONYM").upper()
    if u_id not in st.session_state.user_db: st.session_state.user_db[u_id] = 10
    
    st.markdown(f"### UNITS: {st.session_state.user_db[u_id]}")
    st.divider()
    
    if st.button("🔄 RE-SYNC SYSTEM"):
        st.session_state.app_bg = STUDIO_BG
        st.rerun()

# --- 4. MAIN CONSOLE ---
st.markdown('<div class="console-header">MAXIMUSIKAI</div>', unsafe_allow_html=True)

# Sektion: Input
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_area("COMMAND_INPUT", placeholder="ENTER VISION PARAMETERS...")
with col2:
    aspect = st.selectbox("RATIO", ["1:1", "16:9", "9:16"])
    if st.button("🔥 EXECUTE SYNTHESIS"):
        if st.session_state.user_db[u_id] > 0:
            with st.status("PROCESSING..."):
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect})
                img_url = str(img[0] if isinstance(img, list) else img)
                st.session_state.gallery.append({"user": u_id, "url": img_url})
                st.session_state.user_db[u_id] -= 1
                st.rerun()

st.divider()

# Sektion: Output Grid
if st.session_state.gallery:
    st.markdown("### 📚 DATA VAULT")
    user_data = [p for p in st.session_state.gallery if p["user"] == u_id]
    grid = st.columns(3)
    for i, item in enumerate(reversed(user_data)):
        with grid[i % 3]:
            st.image(item["url"])
            if st.button("USE AS BG", key=f"bg_{i}"):
                st.session_state.app_bg = item["url"]
                st.rerun()

