import streamlit as st
import replicate
import os

# --- 1. SETUP ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DEN ULTIMATA DESIGN-MOTORN (HTML + CSS) ---
# Här skriver vi "riktig" frontend-kod för att slippa Streamlits begränsningar
def inject_custom_os():
    accent = "#00f2ff"
    bg_url = "https://images.unsplash.com"
    
    st.markdown(f"""
        <style>
        /* Hela bakgrunden */
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url("{bg_url}") !important;
            background-size: cover !important;
            background-position: center !important;
        }}

        /* Gömmer Streamlits menyer */
        [data-testid="stHeader"], .main {{ background: transparent !important; }}

        /* Glas-kort för knapparna */
        .os-container {{
            display: flex;
            justify-content: center;
            gap: 30px;
            padding-top: 15vh;
            flex-wrap: wrap;
        }}

        .nav-card {{
            width: 200px;
            height: 250px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: 0.5s all cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-decoration: none;
        }}

        .nav-card:hover {{
            transform: scale(1.1) translateY(-20px);
            background: rgba(255, 255, 255, 0.1);
            border-color: {accent};
            box-shadow: 0 30px 60px rgba(0,0,0,0.5), 0 0 20px {accent}44;
        }}

        .nav-icon {{
            font-size: 50px;
            margin-bottom: 20px;
            filter: drop-shadow(0 0 10px {accent});
        }}

        .nav-text {{
            color: white;
            font-family: 'Courier New', monospace;
            letter-spacing: 3px;
            font-weight: bold;
            font-size: 14px;
        }}
        </style>

        <div class="os-container">
            <div class="nav-card">
                <div class="nav-icon">🪄</div>
                <div class="nav-text">SYNTH</div>
            </div>
            <div class="nav-card">
                <div class="nav-icon">🎧</div>
                <div class="nav-text">AUDIO</div>
            </div>
            <div class="nav-card">
                <div class="nav-icon">🎬</div>
                <div class="nav-text">VIDEO</div>
            </div>
            <div class="nav-card">
                <div class="nav-icon">⚙️</div>
                <div class="nav-text">ENGINE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 3. LOGIK ---
if "page" not in st.session_state:
    st.session_state.page = "DESKTOP"

if st.session_state.page == "DESKTOP":
    inject_custom_os()
    
    # Eftersom HTML-knapparna ovan bara är visuella, 
    # använder vi Streamlits knappar osynligt för att byta sida
    st.write("") # Spacer
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("OPEN SYNTH", use_container_width=True): 
            st.session_state.page = "SYNTH"
            st.rerun()
    # ... osv för de andra knapparna

# --- 4. MODUL-FÖNSTER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div style="background: rgba(0,0,0,0.8); padding: 50px; border-radius: 40px; border: 1px solid #00f2ff;">', unsafe_allow_html=True)
    st.title("🪄 SYNTH MODULE")
    if st.button("← BACK TO OS"):
        st.session_state.page = "DESKTOP"
        st.rerun()
    
    prompt = st.text_input("Enter Prompt:")
    if st.button("GENERATE"):
        st.write("AI is generating...")
    st.markdown('</div>', unsafe_allow_html=True)
























