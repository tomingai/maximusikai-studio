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
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "start_btn": "STARTA GENERERING", "prompt_label": "VAD SKALL VI SKAPA?",
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SÄTT SOM BAKGRUND",
        "upload_label": "LADDA UPP EGEN BILD TILL ARKIVET", "upload_btn": "SPARA I ARKIVET"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "start_btn": "START GENERATING", "prompt_label": "WHAT SHALL WE CREATE?",
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SET AS BACKGROUND",
        "upload_label": "UPLOAD OWN IMAGE TO ARCHIVE", "upload_btn": "SAVE TO ARCHIVE"
    }
}
L = texts[st.session_state.lang]

# --- 3. DYNAMISK DESIGN ---
with st.sidebar:
    st.session_state.lang = st.radio("Language / Språk:", ["Svenska", "English"], horizontal=True)
    st.divider()
    bg_color = st.color_picker("BAKGRUNDSFÄRG", "#050505")
    neon_color = st.color_picker("NEON-FÄRG", "#bf00ff")
    if st.button("ÅTERSTÄLL DESIGN"):
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
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = {"credits": 10, "is_pro": False}
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    u_credits = user_info.get("credits", 0)
    st.info(f"{L['status']}: {'💎 ADMIN' if is_admin else f'⚡ {u_credits} {L['units']}'}")
    mood_val = st.selectbox("MOOD:", ["Cinematic", "Surreal", "Vibrant", "Minimalist"])

# --- 5. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><p class="neon-title">{L["title"]}</p></div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN VILLKOR & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"], L["tab6"] if is_admin else " "])

    with tabs[0]: # --- MAGI ---
        m_ide = st.text_area(L["prompt_label"], value=st.session_state.remix_prompt)
        if st.button(L["start_btn"]):
            if user_info["credits"] > 0 or is_admin:
                with st.status("AI SKAPAR..."):
                    try:
                        if not is_admin: user_info["credits"] -= 1
                        img_output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood_val} style"})
                        img_url = img_output[0] if isinstance(img_output, list) else str(img_output)
                        
                        mu_url = None
                        try:
                            mu_output = replicate.run("facebookresearch/musicgen", input={"prompt": f"{mood_val} music", "duration": 5})
                            mu_url = str(mu_output)
                        except: pass

                        st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": m_ide[:20], "video": img_url, "audio": mu_url})
                        st.rerun()
                    except Exception as e: st.error(f"Fel: {e}")

    with tabs[1]: # --- REGI (Luma) ---
        up_luma = st.file_uploader("Bild till Video:", type=["jpg", "png"], key="l_up")
        if up_luma and st.button("KÖR LUMA ANIMATION"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up_luma})
            st.video(str(res))

    with tabs[2]: # --- MUSIK ---
        mu_p = st.text_input("Beskriv ljudet:")
        if st.button("SKAPA BEAT"):
            res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 15})
            st.audio(str(res))

    with tabs[3]: # --- ARKIV (MED MANUELL UPPLADDNING) ---
        st.subheader(L["upload_label"])
        with st.form("manual_upload"):
            new_img = st.file_uploader("Välj bild:", type=["jpg", "png", "jpeg"])
            new_name = st.text_input("Namnge bilden:", "Min uppladdning")
            if st.form_submit_button(L["upload_btn"]):
                if new_img:
                    # Spara lokalt i sessionen (Streamlit hanterar fil-objektet)
                    st.session_state.gallery.append({
                        "id": time.time(), 
                        "artist": artist_id, 
                        "name": new_name, 
                        "video": new_img, # Här sparar vi filen direkt
                        "audio": None,
                        "is_manual": True
                    })
                    st.success("Bild sparad i arkivet!")
                    st.rerun()

        st.divider()
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if st.button(L["set_bg"], key=f"bg_{item['id']}"):
                    # Vi använder Streamlits inbyggda sätt att hantera filer för bakgrund
                    st.session_state.app_bg_url = item['video']
                    st.rerun()
                if item['audio']: st.audio(item['audio'])

    with tabs[4]: # --- FEED ---
        for item in reversed(st.session_state.gallery[-10:]):
            st.image(item['video'], caption=f"By: {item['artist']}")
            st.divider()

    if is_admin:
        with tabs[5]:
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API-nyckel saknas i Secrets!")



















