import streamlit as st
import replicate
import os
import datetime
import time
import json

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg_url" not in st.session_state: st.session_state.app_bg_url = None
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "agreement_title": "📜 ANVÄNDARAVTAL & VILLKOR",
        "agreement_info": "Du måste godkänna villkoren för att använda studion.",
        "agreement_body": "**1. Ansvar:** Du ansvarar för dina prompts. **2. AI:** Media skapas via Replicate. **3. Credits:** Varje körning drar en unit.",
        "agreement_check": "Jag godkänner villkoren.",
        "open_studio": "ÖPPNA STUDION ✨",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "VAD SKALL VI SKAPA? (Skriv på svenska!)",
        "start_btn": "STARTA GENERERING",
        "status": "STATUS", "units": "UNITS", "mood": "STÄMNING",
        "set_bg": "🖼 SÄTT SOM BAKGRUND", "reset_bg": "ÅTERSTÄLL DESIGN",
        "translating": "Översätter din vision...", "generating": "AI:n skapar..."
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "agreement_title": "📜 TERMS & CONDITIONS",
        "agreement_info": "You must accept the terms to enter the studio.",
        "agreement_body": "**1. Responsibility:** You are responsible for your prompts. **2. AI:** Media is generated via Replicate. **3. Credits:** Each run costs one unit.",
        "agreement_check": "I agree to the terms and conditions.",
        "open_studio": "OPEN STUDIO ✨",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "WHAT SHALL WE CREATE?",
        "start_btn": "START GENERATING",
        "status": "STATUS", "units": "UNITS", "mood": "MOOD",
        "set_bg": "🖼 SET AS BACKGROUND", "reset_bg": "RESET DESIGN",
        "translating": "Translating vision...", "generating": "AI is creating..."
    }
}
L = texts[st.session_state.lang]

# --- 3. DYNAMISK DESIGN ---
with st.sidebar:
    st.markdown(f"### 🌍 LANGUAGE / SPRÅK")
    st.session_state.lang = st.radio("SELECT:", ["Svenska", "English"], horizontal=True, label_visibility="collapsed")
    st.divider()
    st.markdown("### 🎨 STUDIO DESIGN")
    bg_color = st.color_picker("COLOR / FÄRG", "#050505")
    neon_color = st.color_picker("NEON", "#bf00ff")
    if st.button(L["reset_bg"]):
        st.session_state.app_bg_url = None
        st.rerun()

bg_style = f'background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{st.session_state.app_bg_url}"); background-size: cover; background-attachment: fixed;' if st.session_state.app_bg_url else f'background-color: {bg_color} !important;'

st.markdown(f"""
    <style>
    .stApp {{ {bg_style} color: white !important; }}
    [data-testid="stSidebar"] {{ background-color: rgba(10,10,10,0.8) !important; border-right: 1px solid {neon_color}44; }}
    .neon-container {{ background: rgba(0,0,0,0.5); backdrop-filter: blur(15px); padding: 25px; border-radius: 20px; border: 2px solid {neon_color}; text-align: center; margin-bottom: 25px; }}
    .neon-title {{ font-family: 'Arial Black'; font-size: clamp(30px, 5vw, 60px); font-weight: 900; color: white; text-shadow: 2px 2px 15px {neon_color}; margin: 0; }}
    .stButton>button {{ background: rgba(255,255,255,0.1); color: {neon_color}; border: 2px solid {neon_color}; border-radius: 12px; font-weight: bold; width: 100%; transition: 0.3s; }}
    .stButton>button:hover {{ background: {neon_color}; color: white; box-shadow: 0 0 20px {neon_color}; }}
    label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: bold !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY & ANVÄNDARE ---
with st.sidebar:
    st.divider()
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: 
        st.session_state.user_db[artist_id] = {"credits": 10, "is_pro": False}
    
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    # Säker status-logik
    if is_admin:
        display_status = "💎 ADMIN"
    else:
        u_credits = user_info.get("credits", 0)
        display_status = f"⚡ {u_credits} {L['units']}"
        
    st.info(f"{L['status']}: {display_status}")
    mood_val = st.selectbox(L["mood"], ["Cinematic", "Surreal", "Vibrant", "Minimalist"])

# --- 5. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><p class="neon-title">{L["title"]}</p></div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    st.markdown(f"### {L['agreement_title']}")
    st.info(L["agreement_info"])
    with st.expander("READ / LÄS"): st.write(L["agreement_body"])
    if st.checkbox(L["agreement_check"]):
        if st.button(L["open_studio"]):
            st.session_state.agreed = True
            st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"], L["tab6"] if is_admin else " "])

    with tabs[0]: # MAGI
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area(L["prompt_label"], value=st.session_state.remix_prompt)
            if st.button(L["start_btn"]):
                if user_info["credits"] > 0 or is_admin:
                    with st.status(L["generating"]):
                        try:
                            if not is_admin: user_info["credits"] -= 1
                            
                            # Bild-anrop (Flux)
                            img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood_val} style, high quality"})
                            
                            # Säker musik-generering (med fallback)
                            mu_url = None
                            try:
                                # Använder MusicGen-modellen utan ett raderat version-ID
                                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood_val} music", "duration": 5})
                                mu_url = str(mu_res)
                            except Exception:
                                st.warning("Musiken kunde inte genereras just nu, men bilden sparades!")

                            st.session_state.gallery.append({
                                "id": time.time(), 
                                "artist": artist_id, 
                                "name": m_ide[:20], 
                                "video": str(img[0] if isinstance(img, list) else img), 
                                "audio": mu_url
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ett fel uppstod: {e}")

    with tabs[1]: # REGI (Luma)
        up = st.file_uploader("IMAGE:", type=["jpg", "png"], key="reg_up")
        if up and st.button("KÖR LUMA"):
            with st.spinner("Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up})
                st.video(str(res))

    with tabs[2]: # MUSIK STUDIO
        mu_prompt = st.text_input("DESCRIBE BEAT:", f"{mood_val} vibes")
        if st.button("CREATE AUDIO"):
            with st.spinner("Komponerar..."):
                try:
                    res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_prompt, "duration": 10})
                    st.audio(str(res))
                except Exception as e:
                    st.error(f"Kunde inte skapa musik: {e}")

    with tabs[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for item in reversed(my):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if st.button(L["set_bg"], key=f"bg_{item['id']}"):
                    st.session_state.app_bg_url = item['video']
                    st.rerun()
                if item.get('audio'): st.audio(item['audio'])

    with tabs[4]: # FEED
        for item in reversed(st.session_state.gallery[-10:]):
            st.image(item['video'], caption=f"{item['name']} by {item['artist']}")
            st.divider()

    if is_admin:
        with tabs[5]: # ADMIN
            st.write("### ADMIN DASHBOARD")
            st.write(st.session_state.user_db)
            if st.button("RESET ALL GALLERY"): 
                st.session_state.gallery = []
                st.rerun()
else:
    st.error("API KEY MISSING")



















