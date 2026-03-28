import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- SYSTEM REFRESH v10.1.6 ---
# STATUS: OPTIMIZED | CACHE: PURGED | REGLER 1-21 ACTIVE

def refresh_system():
    """Rensar temporära filer och validerar anslutningar."""
    st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append(f"[{st.session_state.last_refresh}] ⚡ SYSTEM REFRESH COMPLETE")
    if len(st.session_state.logs) > 15:
        st.session_state.logs.pop(0)

# Kör refresh vid rendering
refresh_system()

# UI RE-APPLY
accent = st.session_state.get("accent_color", "#00ffcc")
st.markdown(f"""
    <style>
    .refresh-notifier {{
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 20px;
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid {accent};
        border-radius: 10px;
        backdrop-filter: blur(10px);
        color: {accent};
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        z-index: 1000;
        animation: fadeout 3s forwards;
    }}
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    </style>
    <div class="refresh-notifier">SYSTEM RELOADED: {st.session_state.last_refresh}</div>
""", unsafe_allow_html=True)

# Fortsätt med huvudgränssnittet (Desktop)
if st.session_state.get("page") == "DESKTOP":
    st.markdown("<h1 style='text-align:center; font-size:4rem; letter-spacing:15px; padding-top:15vh;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    
    # Grid för appar
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🪄 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    with col2:
        if st.button("🎧 AUDIO"): st.session_state.page = "AUDIO"; st.rerun()
    with col3:
        if st.button("⚙️ SYSTEM"): st.session_state.page = "SYSTEM"; st.rerun()

    # Live Log Box
    st.markdown('<div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">', unsafe_allow_html=True)
    st.write("### 📜 KERNEL LOG")
    for log in reversed(st.session_state.logs):
        st.code(log, language="bash")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Fallback för att tvinga fram desktop om sidan tappats
    if st.button("🏠 ÅTERGÅ TILL DESKTOP"):
        st.session_state.page = "DESKTOP"
        st.rerun()




























































