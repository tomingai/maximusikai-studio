import streamlit as st
import replicate
import os
import datetime
import time
import json

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# OFFICIEL SKAPARE
MY_NAME = "Tomas Ingvarsson" 

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "creator": f"DESIGNED BY {MY_NAME.upper()}",
        "agreement_title": "📜 ANVÄNDARAVTAL & VILLKOR",
        "agreement_body": f"Denna studio är utvecklad av {MY_NAME}. Genom att använda den godkänner du: **1. Ansvar:** Du ansvarar för dina prompts. **2. AI:** Media skapas via Replicate. **3. Credits:** Varje körning drar en unit.",
        "agreement_check": "Jag godkänner villkoren och vill börja skapa.",
        "open_studio": "ÖPPNA STUDION ✨",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "VAD SKALL VI SKAPA? (Skriv på svenska!)", "start_btn": "STARTA GENERERING",
        "status": "STATUS", "units": "UNITS", "mood": "STÄMNING", "set_bg": "🖼 SÄTT SOM BAKGRUND",
        "atm_space": "RYMDEN 🌌", "atm_forest": "SKOGEN 🌲", "atm_city": "STADEN 🌆", "atm_bake": "BAKNING 🥐"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "creator": f"DESIGNED BY {MY_NAME.upper()}",
        "agreement_title": "📜 TERMS & CONDITIONS",
        "agreement_body": f"This studio is developed by {MY_NAME}. By using it you agree: **1. Responsibility:** You are responsible for your prompts. **2. AI:** Media is generated via Replicate. **3. Credits:** Each run costs one unit.",
        "agreement_check": "I agree to the terms and want to start creating.",
        "open_studio": "OPEN STUDIO ✨",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "WHAT SHALL WE CREATE?", "start_btn": "START GENERATING",
        "status": "STATUS", "units": "UNITS", "mood": "MOOD", "set_bg": "🖼 SET AS BACKGROUND",
        "atm_space": "SPACE 🌌", "atm_forest": "FOREST 🌲", "atm_city": "CITY 🌆", "atm_bake": "BAKING 🥐"
    }
}
L = texts[st.session_state.lang]

# --- 3. HJÄLP-FUNKTIONER ---
def translate_prompt(text):
    try:
        output = replicate.run("meta/llama-2-70b-chat", 
            input={"prompt": f"Translate to a short English image prompt: {text}", "system_prompt": "Return ONLY translation.", "max_new_tokens": 50})
        return "".join(output).strip()
    except: return text

# --- 4. DYNAMISK DESIGN ---
bg_data = st.session_state.app_bg
if bg_data:
    bg_url = bg_data if isinstance(bg_data, str) else str(bg_data if isinstance(bg_data, list) else bg_data)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("{bg_url}");
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; text-shadow: 1px 1px 4px black !important; font-weight: bold !important; 
        }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255,255,255,0.15); border-radius: 10px; padding: 5px; }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 5. SIDOMENY ---
with st.sidebar:
    st.markdown(f'<p style="color:#bf00ff; font-weight:900; letter-spacing:1px; margin-bottom:0;">{L["creator"]}</p>', unsafe_allow_html=True)
    st.caption("v4.9.5 Production Edition")
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    # Säkra variabler för f-string display
    cur_u = st.session_state.user_db[artist_id]
    u_txt = L["units"]
    s_txt = L["status"]
    if is_admin: st.info(f"{s_txt}: 💎 ADMIN")
    else: st.info(f"{s_txt}: ⚡ {cur_u} {u_txt}")
    
    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2)
    if c1.button(L["atm_space"]):
        st.session_state.app_bg = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, 4k"}); st.rerun()
    if c2.button(L["atm_forest"]):
        st.session_state.app_bg = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Magic forest mist, 4k"}); st.rerun()
    if c1.button(L["atm_city"]):
        st.session_state.app_bg = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "City night neon, 4k"}); st.rerun()
    if c2.button(L["atm_bake"]):
        st.session_state.app_bg = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Rustic bakery buns, 4k"}); st.rerun()

# --- 6. HUVUDAPP & FLIKAR ---
st.markdown(f'<h1 style="text-align:center; color:white; margin-bottom:0;">{L["title"]}</h1>', unsafe_allow_html=True)

if not st.session_state.agreed:
    st.markdown(f"### {L['agreement_title']}")
    st.info(L["agreement_body"])
    if st.checkbox(L["agreement_check"]):
        if st.button(L["open_studio"]): st.session_state.agreed = True; st.rerun()
    st.markdown(f'<p style="text-align:center; color:gray; font-size:10px; margin-top:50px;">© 2026 {MY_NAME} | All Rights Reserved</p>', unsafe_allow_html=True)
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tab_list = [L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"]]
    if is_admin: tab_list.append(L["tab6"])
    tabs = st.tabs(tab_list)

    with tabs[0]: # MAGI
        prompt = st.text_area(L["prompt_label"], key="p_magi")
        if st.button(L["start_btn"]):
            if st.session_state.user_db[artist_id] > 0 or is_admin:
                with st.status("AI..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    eng_p = translate_prompt(prompt)
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{eng_p}, cinematic"})
                    mu_url = None
                    try: mu = replicate.run("facebookresearch/musicgen:7a76a825", input={"prompt": "music", "duration": 5}); mu_url = str(mu)
                    except: pass
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:15], "url": img, "audio": mu_url})
                    st.rerun()

    with tabs[1]: # REGI
        up = st.file_uploader("Image:", type=["jpg", "png"], key="reg_up")
        if up and st.button("KÖR LUMA"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": up})
            st.video(str(res))

    with tabs[2]: # MUSIK
        mu_p = st.text_input("Describe beat:", key="p_mu")
        if st.button("CREATE"):
            res = replicate.run("facebookresearch/musicgen:7a76a825", input={"prompt": mu_p, "duration": 10})
            st.audio(str(res))

    with tabs[3]: # ARKIV
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my: st.info("Ditt arkiv är tomt.")
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                u = p["url"] if isinstance(p["url"], str) else p["url"]
                st.image(u)
                if st.button(L["set_bg"], key=f"set_{p['id']}"): st.session_state.app_bg = u; st.rerun()
                if p.get("audio"): st.audio(p["audio"])

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            u = p["url"] if isinstance(p["url"], str) else p["url"]
            st.image(u, caption=f"Artist: {p['artist']}")

    if is_admin:
        with tabs[5]: # ADMIN
            st.json(st.session_state.user_db)
            if st.button("RENSA ALLT"): st.session_state.gallery = []; st.rerun()
else:
    st.error("MISSING API TOKEN")


























