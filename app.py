import streamlit as st
import replicate
import os
import requests
import json
import base64
from datetime import datetime
from io import BytesIO

# --- 1. BOOT LOADER & GLOBAL SETTINGS ---
st.set_page_config(page_title="MAXIMUSIKAI PREMIER", layout="wide", initial_sidebar_state="expanded")

# API Setup
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_PATH = "maximus_vault.json"

# --- 2. DATABASE ARCHITECT (Functions) ---
def load_database():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_to_database(entry):
    db = load_database()
    entry["id"] = f"HEX_{datetime.now().strftime('%y%m%d%H%M%S')}"
    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.append(entry)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)
    st.session_state.vault = db

# --- 3. SESSION STATE INITIALIZATION (Critical Fix) ---
if "vault" not in st.session_state:
    st.session_state.vault = load_database()
if "terminal_logs" not in st.session_state:
    st.session_state.terminal_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] CORE_BOOT_SUCCESS"]
if "last_res" not in st.session_state:
    st.session_state.last_res = None

def log_event(msg):
    st.session_state.terminal_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# --- 4. UI ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    .stApp { background-color: #030303; color: #999; font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background: #080808 !important; border: 1px solid #141414 !important;
        font-family: 'JetBrains Mono'; font-size: 11px; padding: 10px 20px;
    }
    .terminal-box { 
        background: #000; border: 1px solid #111; padding: 15px; 
        font-family: 'JetBrains Mono'; font-size: 10px; color: #00f2ff;
        height: 250px; overflow-y: auto;
    }
    label { font-family: 'JetBrains Mono' !important; color: #333 !important; text-transform: uppercase; font-size: 9px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. MAIN WORKSPACE ---
tab_gen, tab_analyze, tab_vault, tab_logs = st.tabs(["⚡ SYNTHESIS", "🔍 ANALYZER", "📦 VAULT", "📟 LOGS"])

# --- TAB: SYNTHESIS ---
with tab_gen:
    c1, c2 = st.columns([1, 1.8])
    with c1:
        st.markdown("<label>NEURAL_PROMPT</label>", unsafe_allow_html=True)
        prompt = st.text_area("P", height=200, label_visibility="collapsed", placeholder="Define the visual...")
        ratio = st.selectbox("FRAME", ["1:1", "16:9", "9:16"])
        
        if st.button("EXECUTE_SYNTHESIS", use_container_width=True):
            if prompt:
                with st.status("ENGAGING_FLUX_CORE..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": ratio})
                    final_url = res[0] if isinstance(res, list) else res
                    st.session_state.last_res = final_url
                    save_to_database({"type": "GEN", "url": final_url, "prompt": prompt})
                    log_event("SYNTHESIS_SUCCESSFUL")
                st.rerun()

    with c2:
        if st.session_state.last_res:
            st.image(st.session_state.last_res, use_container_width=True)
            st.download_button("💾 DOWNLOAD", requests.get(st.session_state.last_res).content, "export.jpg")
        else:
            st.info("AWAITING_SIGNAL")

# --- TAB: ANALYZER ---
with tab_analyze:
    st.markdown("### `NEURAL_DECONSTRUCTION`")
    up_file = st.file_uploader("UPLOAD_ASSET", type=["jpg", "png"])
    if up_file:
        st.image(up_file, width=300)
        if st.button("ANALYZE_PIXELS"):
            log_event("ANALYSIS_STARTED")
            # Här läggs moondream-logiken in som i förra steget
            st.warning("ENGINE_OFFLINE: Connect Moondream API")

# --- TAB: VAULT ---
with tab_vault:
    st.markdown("### `ARCHIVE_EXPLORER`")
    if not st.session_state.vault:
        st.write("VAULT_EMPTY")
    else:
        v_cols = st.columns(4)
        for i, item in enumerate(reversed(st.session_state.vault)):
            with v_cols[i % 4]:
                st.image(item["url"])
                st.caption(item.get("timestamp", "N/A"))

# --- TAB: LOGS ---
with tab_logs:
    logs = "\n".join(st.session_state.terminal_logs[::-1])
    st.markdown(f'<div class="terminal-box">{logs.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# --- SIDEBAR INFO ---
with st.sidebar:
    st.title("MAXIMUS_OS")
    st.write(f"VAULT_COUNT: {len(st.session_state.vault)}")
    if st.button("WIPE_SYSTEM_DATA"):
        if os.path.exists(DB_PATH): os.remove(DB_PATH)
        st.session_state.clear()
        st.rerun()



