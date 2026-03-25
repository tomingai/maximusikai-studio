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
if "bg_focus" not in st.session_state: st.session_state.bg_focus = "center"
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "start_btn": "STARTA GENERERING", "prompt_label": "VAD SKALL VI SKAPA?",
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SÄTT SOM BAKGRUND",
        "upload_label": "LADDA UPP EGEN BILD", "upload_btn": "SPARA I ARKIVET",
        "crop_label": "VÄLJ BILD-FOKUS (CROP):"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "start_btn": "START GENERATING", "prompt_label": "WHAT SHALL WE CREATE?",
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SET AS BACKGROUND",
        "upload_label": "UPLOAD OWN IMAGE", "upload_btn": "SAVE TO ARCHIVE",
        "crop_label": "SELECT IMAGE FOCUS (CROP):"
    }
}
L = texts[st.session_state.lang]

# --- 3. DYNAMISK DESIGN (MED CROP/FOKUS) ---
with st.sidebar:
    st.session_state.lang = st.radio("Language / Språk:", ["Svenska", "English"], horizontal=True)
    st.divider()
    bg_color = st.color_picker("BAKGRUNDSFÄRG", "#050505")
    neon_color = st.color_picker("NEON-FÄRG", "#bf00ff")
    
    # Crop/Fokus-väljare för bakgrunden
    st.session_state.bg_focus = st.selectbox(L["crop_label"], ["top", "center", "bottom"], index=1)
    
    if st.button("ÅTERSTÄLL DESIGN"):
        st.session_state.app_bg_url = None
        st.rerun()

# CSS Logik (Hanterar f-strings säkert med dubbla citattecken)
bg_css = ""
if st.session_state.app_bg_url:
    # Om bakgrunden är en uppladdad fil (Bytes) eller URL (Sträng)
    img_src = st.session_state.app_bg_url
    if not isinstance(img_src, str):
        import base64
        data = base64.b64encode(img_src.getvalue()).decode()
        img_src = f"data:image/png;base64,{data}"
    
    bg_css = f"""
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{img_src}");
        background-size: cover;
        background-position: {st.session_state.bg_focus};
        background-attachment: fixed;
    }}
    """
else:
    bg_css = f".stApp {{ background-color: {bg_color} !important; }}"

st.markdown(f"<style>{bg_css} .neon-container {{ border: 2px solid {neon_color}; box-shadow: 0 0 20px {neon_color}33; }}</style>", unsafe_allow_html=True)

# --- 4. SIDOMENY & ANVÄNDARE ---
with st.sidebar:
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: 
        st.session_state.user_db[artist_id] = {"credits": 10, "is_pro": False}
    
    user_info = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    # Säkra f-strings för status
    u_credits = user_info.get("credits", 0)
    status_label = L["status"]
    unit_label = L["units"]
    
    if is_admin:
        st.info(f"{status_label}: 💎 ADMIN")
    else:
        st.info(f"{status_label}: ⚡ {u_credits} {unit_label}")

# --- 5. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container" style="text-align:center; padding:20px; border-radius:20px; background:rgba(0,0,0,0.5); backdrop-filter:blur(10px); margin-bottom:20px;"><h1 style="color:white; font-family:Arial Black; font-size:50px; margin:0;">{L["title"]}</h1></div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"], L["tab6"] if is_admin else " "])

    with tabs[0]: # MAGI
        m_ide = st.text_area(L["prompt_label"], value=st.session_state.remix_prompt)
        if st.button(L["start_btn"]):
            if user_info["credits"] > 0 or is_admin:
                with st.status("AI..."):
                    if not is_admin: user_info["credits"] -= 1
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": m_ide})
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": m_ide[:15], "video": str(img[0] if isinstance(img, list) else img), "audio": None})
                    st.rerun()

    with tabs[3]: # ARKIV (UPPLADDNING + CROP)
        st.subheader(L["upload_label"])
        with st.form("upload_form"):
            up_img = st.file_uploader("Bild:", type=["jpg", "png", "jpeg"])
            up_name = st.text_input("Namn:", "Uppladdning")
            if st.form_submit_button(L["upload_btn"]):
                if up_img:
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": up_name, "video": up_img, "audio": None, "manual": True})
                    st.rerun()

        st.divider()
        for item in reversed([p for p in st.session_state.gallery if p["artist"] == artist_id]):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if st.button(L["set_bg"], key=f"bg_{item['id']}"):
                    st.session_state.app_bg_url = item['video']
                    st.rerun()

    if is_admin and len(tabs) > 5:
        with tabs[5]:
            st.write(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("API-nyckel saknas!")




















