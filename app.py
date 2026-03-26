import streamlit as st
import replicate
import os
import time

# --- 1. CORE ENGINE ---
st.set_page_config(page_title="MAXIMUSIKAI 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []

# --- 2. THE BLACK STUDIO DESIGN (PRO) ---
def apply_premium_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* BAKGRUND: Deep Ink med filmiskt brus */
        .stApp {
            background-color: #050505 !important;
            background-image: radial-gradient(circle at 50% -20%, #1a1a2e, #050505) !important;
        }
        
        /* FILM-NOISE (Gör att det inte ser billigt/platt ut) */
        .stApp::after {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            opacity: 0.04; pointer-events: none; z-index: 999;
            background-image: url("https://upload.wikimedia.org");
        }

        /* PREMIUM PANELER: Glassmorphism med inre glöd */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(20, 20, 25, 0.7) !important;
            backdrop-filter: blur(40px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.05);
        }

        /* TEXT: Minimalistisk & Tydlig */
        h1, h2, h3, p, label {
            color: #ffffff !important;
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: -0.02em;
        }

        /* INPUTS: Stealth Look */
        textarea, input {
            background-color: rgba(0, 0, 0, 0.4) !important;
            color: #e0e0e0 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            padding: 15px !important;
        }
        textarea:focus { border-color: #00f2ff !important; }

        /* KNAPPAR: Liquid Silver / Neon */
        .stButton>button {
            background: #ffffff !important;
            color: #000000 !important;
            border-radius: 12px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            height: 55px !important;
            border: none !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255,255,255,0.15);
        }

        .logo-text {
            font-family: 'Space Grotesk'; font-size: 3rem; font-weight: 900;
            text-align: center; color: #fff; letter-spacing: -2px; margin-bottom: 30px;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. STUDIO UI ---
apply_premium_design()
st.markdown('<div class="logo-text">MAXIMUSIKAI.</div>', unsafe_allow_html=True)

# --- 4. COMMAND INTERFACE ---
col_main, col_side = st.columns([2, 1])

with col_main:
    prompt = st.text_area("DESCRIBE YOUR VISION", placeholder="Start typing...", height=150)
    if st.button("EXECUTE SYNTHESIS", use_container_width=True):
        if prompt:
            with st.status("Neural link active...") as status:
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                res = replicate.run("black-forest-labs/flux-schnell", 
                                   input={"prompt": f"Professional cinematic, {prompt}, masterpiece, 8k", "aspect_ratio": "9:16"})
                st.session_state.gallery.append(res)
                st.rerun()

with col_side:
    st.markdown("### SYSTEM STATUS")
    st.write("CORE: OPTIMAL")
    st.write("SYNC: 100%")
    st.divider()
    st.markdown("### FORMAT")
    st.selectbox("ASPECT RATIO", ["9:16 PORTRAIT", "1:1 SQUARE", "16:9 WIDE"])

# --- 5. VAULT (GALLERY) ---
if st.session_state.gallery:
    st.markdown("---")
    st.markdown("### STUDIO VAULT")
    cols = st.columns(3)
    for idx, img in enumerate(reversed(st.session_state.gallery)):
        with cols[idx % 3]:
            st.image(img, use_container_width=True)


