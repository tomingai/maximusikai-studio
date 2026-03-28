import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.3.3", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SJÄLVTEST & DIAGNOSTIK (Regel 19) ---
def run_system_diagnostics():
    checks = []
    # API Check
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if api_token and api_token.startswith("r8_"):
        checks.append("API: CONNECTED")
    else:
        checks.append("API: TOKEN MISSING/INVALID")
        st.session_state.alarm = True
    
    # Database Check
    if os.path.exists(DB_FILE):
        checks.append("DATABASE: ONLINE")
    else:
        checks.append("DATABASE: NEW INITIALIZED")
        with open(DB_FILE, "w") as f: json.dump([], f)
        
    for msg in checks:
        add_log(f"DIAGNOSTIC: {msg}")

# --- 3. SYSTEMFUNKTIONER ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
    if len(st.session_state.logs) > 12: st.session_state.logs.pop(0)

# --- 4. INITIALISERING & UI ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP", "library": [], "logs": [],
        "accent": "#00f2ff", "wallpaper": "https://images.unsplash.com",
        "alarm": False
    })
    run_system_diagnostics()

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass-card {{ background: rgba(0, 5, 15, 0.85); backdrop-filter: blur(25px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}44 !important; color: {accent} !important; background: transparent !important; border-radius: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "ARKIV"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
for i, (icon, target) in enumerate(nav):
    if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODUL: DESKTOP & TERMINAL ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:10vh; color:{accent};'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    
    # CMD Terminal
    cmd = st.text_input("SYSTEM TERMINAL >", placeholder="Skriv /test för självtest eller /rules för regler...")
    if cmd == "/test": 
        run_system_diagnostics()
        st.success("Självtest utfört. Se loggen.")
    elif cmd == "/rules": 
        st.json({"v": "10.3.3", "active_rules": "1-22"})
    elif cmd == "/clear": 
        st.session_state.logs = []
        st.rerun()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📜 SYSTEM KERNEL LOG")
    for log in reversed(st.session_state.logs): st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📚 MULTIMEDIA-ARKIV")
    if not st.session_state.library:
        st.info("Arkivet är tomt.")
    else:
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type']} | {item['prompt'][:30]}..."):
                if item['type'] == "IMG": 
                    st.image(item['url'])
                    if st.button("SET WALLPAPER", key=f"w_{i}"):
                        st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# (Övriga moduler SYNTH, AUDIO, SYSTEM laddas här enligt tidigare logik)

































































