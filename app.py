import streamlit as st
import replicate
import os
import time

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="MAXIMUSIKAI PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "units" not in st.session_state: st.session_state.units = 50

# --- 2. THE HIGH-CONTRAST NEBULA ENGINE ---
def apply_readable_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* ANIMERAD BAKGRUND */
        .stApp {
            background: linear-gradient(125deg, #000428, #004e92, #000428, #050505);
            background-size: 400% 400%;
            animation: nebulaFlow 20s ease infinite;
        }
        @keyframes nebulaFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

        /* TEXTSKYDD: MÖRKA GLASPANELER */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(0, 0, 0, 0.75) !important; /* Mörkare för bättre textkontrast */
            backdrop-filter: blur(15px) !important;
            border: 2px solid #00f2ff !important; /* Tydlig neonram */
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }

        /* SUPER-LÄSBAR TEXT */
        h1, h2, h3, p, label, .stMarkdown {
            color: #ffffff !important;
            font-family: 'Orbitron', sans-serif !important;
            text-shadow: 2px 2px 4px #000000, -1px -1px 0 #000 !important; /* Dubbel skugga för max läsbarhet */
            letter-spacing: 1px;
        }

        /* INPUT-FÄLT: SVARTA MED NEON-TEXT */
        textarea, input {
            background-color: #000000 !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 18px !important;
            opacity: 1 !important;
        }

        /* KNAPPAR */
        .stButton>button {
            background: #00f2ff !important;
            color: #000000 !important;
            font-weight: 900 !important;
            font-family: 'Orbitron' !important;
            height: 55px !important;
            border: none !important;
            width: 100%;
        }
        
        .logo-text {
            font-family: 'Orbitron'; font-size: 2.5rem; text-align: center;
            color: #fff; text-shadow: 0 0 15px #00f2ff; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. STUDIO UI ---
apply_readable_design()
st.markdown('<div class="logo-text">MAXIMUSIKAI</div>', unsafe_allow_html=True)

# Statusrad
c1, c2 = st.columns(2)
with c1: st.write("📡 SYSTEM: ONLINE")
with c2: st.markdown(f"<p style='text-align:right;'>⚡ UNITS: {st.session_state.units}</p>", unsafe_allow_html=True)

# --- 4. COMMAND CENTER ---
st.markdown("### 🪄 NEURAL SYNTHESIS")
prompt = st.text_area("VAD SKALL VI SKAPA?", placeholder="Skriv din vision...", height=120)

# Mobil-anpassad knapprad
if st.button("🔥 STARTA GENERERING", use_container_width=True):
    if prompt and st.session_state.units > 0:
        with st.status("Länkar till AI-kärnan...") as status:
            try:
                # Automatiskt kvalitets-tillägg
                pro_prompt = f"{prompt}, hyper-realistic, cinematic lighting, 8k, detailed"
                
                os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
                res = replicate.run("black-forest-labs/flux-schnell", 
                                   input={"prompt": pro_prompt, "aspect_ratio": "9:16"})
                
                img_url = str(res) if isinstance(res, list) else str(res)
                st.session_state.gallery.append(img_url)
                st.session_state.units -= 1
                
                st.image(img_url, use_container_width=True)
                status.update(label="KLART!", state="complete")
                st.rerun()
            except Exception as e:
                st.error(f"FEL: {e}")

# --- 5. ARKIV ---
if st.session_state.gallery:
    st.divider()
    st.markdown("### 📚 DITT ARKIV")
    cols = st.columns(2)
    for idx, img in enumerate(reversed(st.session_state.gallery)):
        with cols[idx % 2]:
            st.image(img, use_container_width=True)
            st.caption(f"ASSET #{idx}")

st.caption("v4.5 PRO | 2026.03.26")


