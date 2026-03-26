import streamlit as st
import replicate
import os
import time

# --- 1. CONFIG & UI ENGINE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- 2. THE JUKEBOX-INSPIRED SHADER (CSS) ---
def apply_jukebox_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* Bakgrund: Djup kolsvart med subtil textur */
        .stApp {
            background-color: #0b0b0e !important;
            background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0);
            background-size: 40px 40px;
        }

        /* Sidebar: Smal och industriell */
        [data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid #1a1a1a;
            width: 80px !important;
        }

        /* Paneler: Inga hörn, bara mjukt ljus */
        div[data-testid="stVerticalBlock"] > div {
            background: #111114 !important;
            border: 1px solid #1c1c21 !important;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s ease;
        }
        div[data-testid="stVerticalBlock"] > div:hover {
            border-color: #33333b !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.5);
        }

        /* Typography */
        h1, h2, h3, p, label {
            color: #ececed !important;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.01em;
        }

        /* Input: "The Console Look" */
        textarea, input {
            background-color: #08080a !important;
            color: #00f2ff !important;
            border: 1px solid #1c1c21 !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 14px !important;
        }

        /* Knappar: Jukebox-blå (Electric) */
        .stButton>button {
            background: #0052ff !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            height: 48px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0, 82, 255, 0.2);
        }
        .stButton>button:hover {
            background: #1a66ff !important;
            box-shadow: 0 8px 20px rgba(0, 82, 255, 0.4);
            transform: translateY(-1px);
        }

        /* Status-indikatorer */
        .status-dot {
            height: 8px; width: 8px; background-color: #00ff88;
            border-radius: 50%; display: inline-block; margin-right: 8px;
            box-shadow: 0 0 10px #00ff88;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. STUDIO LAYOUT ---
apply_jukebox_design()

# Header Area
col_logo, col_stat = st.columns([4, 1])
with col_logo:
    st.markdown("<h1 style='margin:0;'>MAXIMUSIKAI <span style='color:#0052ff;'>STUDIO</span></h1>", unsafe_allow_html=True)
with col_stat:
    st.markdown("<div style='text-align:right; padding-top:10px;'><span class='status-dot'></span>SYSTEM ONLINE</div>", unsafe_allow_html=True)

st.write("---")

# Main Workspace
col_input, col_preview = st.columns([1, 1.5])

with col_input:
    st.markdown("### 🎛️ CONTROL")
    prompt = st.text_area("NEURAL PROMPT", placeholder="Describe your vision...", height=150)
    
    c1, c2 = st.columns(2)
    with c1:
        ratio = st.selectbox("FORMAT", ["1:1", "16:9", "9:16"])
    with c2:
        quality = st.select_slider("QUALITY", options=["Draft", "Pro", "Ultra"])
        
    if st.button("EXECUTE SYNTHESIS", use_container_width=True):
        if prompt:
            with st.status("Initializing Cores..."):
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                # Prompt Engineering för Pro-resultat
                enhanced = f"{prompt}, professional studio quality, high-fidelity, masterpiece"
                res = replicate.run("black-forest-labs/flux-schnell", 
                                   input={"prompt": enhanced, "aspect_ratio": ratio})
                st.session_state.last_res = res
                st.rerun()

with col_preview:
    st.markdown("### 📺 OUTPUT")
    if "last_res" in st.session_state:
        st.image(st.session_state.last_res, use_container_width=True, caption="RENDER_COMPLETE")
    else:
        st.info("Awaiting input parameters...")

# --- 4. FEED / VAULT ---
st.write("---")
st.markdown("### 📚 RECENT ASSETS")
# Här skulle vi ha ett snyggt grid med tidigare skapelser
st.caption("v4.8 Build 2026.04 | Powered by Neural Engine")


