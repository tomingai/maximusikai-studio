import streamlit as st
import replicate
import os
import time

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

MY_NAME = "Tomas Ingvarsson" 

# Initialisera Session State
for key, val in {
    "gallery": [], "user_db": {"TOMAS2026": 9999}, "app_bg": None, 
    "agreed": False, "lang": "Svenska"
}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. SPRÅK & DESIGN ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO", "creator": f"DESIGNED BY {MY_NAME.upper()}",
        "agreement_title": "📜 ANVÄNDARAVTAL", "open_studio": "ÖPPNA STUDION ✨",
        "tab1": "🪄 MAGI", "tab2": "🎬 REGI", "tab3": "🎧 MUSIK", "tab4": "📚 ARKIV", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "VAD SKALL VI SKAPA?", "start_btn": "STARTA GENERERING", "set_bg": "🖼 SÄTT SOM BAKGRUND"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO", "creator": f"DESIGNED BY {MY_NAME.upper()}",
        "agreement_title": "📜 TERMS", "open_studio": "OPEN STUDIO ✨",
        "tab1": "🪄 MAGIC", "tab2": "🎬 DIRECTOR", "tab3": "🎧 MUSIC", "tab4": "📚 ARCHIVE", "tab5": "🌐 FEED", "tab6": "⚙️ ADMIN",
        "prompt_label": "WHAT SHALL WE CREATE?", "start_btn": "START GENERATING", "set_bg": "🖼 SET AS BACKGROUND"
    }
}
L = texts[st.session_state.lang]

# Dynamisk Bakgrund (CSS)
bg_url = st.session_state.app_bg
if bg_url:
    st.markdown(f"""<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ color: white !important; text-shadow: 2px 2px 4px #000; font-weight: bold; }}</style>""", unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #050505; }</style>", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown(f"### {L['creator']}")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    
    is_admin = (artist_id == "TOMAS2026")
    units = st.session_state.user_db[artist_id]
    st.info(f"STATUS: {'💎 ADMIN' if is_admin else f'⚡ {units} UNITS'}")

# --- 4. HUVUDLOGIK ---
if not st.session_state.agreed:
    st.title(L["agreement_title"])
    if st.checkbox("Jag godkänner att Tomas är ett geni och att jag ansvarar för mina prompts."):
        if st.button(L["open_studio"]): st.session_state.agreed = True; st.rerun()
    st.stop()

# API-Check
if not st.secrets.get("REPLICATE_API_TOKEN"):
    st.error("Saknar REPLICATE_API_TOKEN i Secrets!")
    st.stop()

# FLIKAR
tabs = st.tabs([L[f"tab{i+1}"] for i in range(6 if is_admin else 5)])

with tabs[0]: # MAGI (Bild + Musik)
    prompt = st.text_area(L["prompt_label"])
    if st.button(L["start_btn"]):
        if units > 0 or is_admin:
            with st.spinner("AI bearbetar din vision..."):
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:20], "url": img[0]})
                if not is_admin: st.session_state.user_db[artist_id] -= 1
                st.rerun()

with tabs[1]: # REGI (Video)
    st.subheader("Video-generering")
    vid_p = st.text_input("Beskriv scenen:")
    if st.button("Skapa Video"):
        res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": vid_p})
        st.video(res)

with tabs[2]: # MUSIK
    mu_p = st.text_input("Beskriv ljudbilden (t.ex. 'Lo-fi hip hop')")
    if st.button("Generera Musik"):
        res = replicate.run("facebookresearch/musicgen:7a76a825", input={"prompt": mu_p})
        st.audio(res)

with tabs[3]: # ARKIV
    my_items = [i for i in st.session_state.gallery if i["artist"] == artist_id]
    for item in reversed(my_items):
        with st.expander(f"📁 {item['name']}"):
            st.image(item["url"])
            if st.button(L["set_bg"], key=f"bg_{item['id']}"):
                st.session_state.app_bg = item["url"]; st.rerun()

with tabs[4]: # FEED (Global)
    st.subheader("Globalt flöde")
    for item in reversed(st.session_state.gallery[-10:]):
        st.write(f"**Artist:** {item['artist']}")
        st.image(item["url"], width=400)

if is_admin:
    with tabs[5]:
        st.subheader("Admin Kontrollpanel")
        st.write("Registrerade användare:", st.session_state.user_db)
        if st.button("Rensa Galleri"): 
            st.session_state.gallery = []; st.rerun()



























