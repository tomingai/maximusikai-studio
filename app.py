import streamlit as st
import replicate
import os
import json
import time
import requests

# =========================
# 0. DATABAS & ANVÄNDARE
# =========================
DB_FILE = "users.json"

def init_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_user(artist_id):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {"units": 20, "bg": None, "gallery": []}
        save_db(db)
    return db[artist_id]

def update_user(artist_id, key, value):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {"units": 20, "bg": None, "gallery": []}
    db[artist_id][key] = value
    save_db(db)

def add_to_gallery(artist, name, img_url, audio_url):
    db = load_db()
    if artist not in db:
        db[artist] = {"units": 20, "bg": None, "gallery": []}
    entry = {
        "id": time.time(),
        "artist": artist,
        "name": name[:30] if name else "UNTITLED",
        "url": img_url,
        "audio": audio_url
    }
    db[artist]["gallery"].append(entry)
    save_db(db)

def get_user_gallery(artist):
    db = load_db()
    return db.get(artist, {}).get("gallery", [])

def get_global_feed():
    db = load_db()
    feed = []
    for artist in db:
        feed.extend(db[artist].get("gallery", []))
    return feed

# =========================
# 1. SPRÅK & TEXTER
# =========================
LANG = {
    "Svenska": {
        "title": "MAXIMUSIKAI SUPER STUDIO",
        "status": "STATUS",
        "units": "Units",
        "magic_tab": "🪄 MAGI",
        "director_tab": "🎬 REGI",
        "music_tab": "🎧 MUSIK",
        "archive_tab": "📚 ARKIV",
        "feed_tab": "🌐 FEED",
        "admin_tab": "⚙️ ADMIN",
        "prompt_label": "Vad ska vi skapa?",
        "generate_btn": "GENERERA",
        "no_gallery": "Inga verk ännu.",
        "create_first": "Skapa något i MAGI först.",
        "beat_label": "Beskriv beatet:",
        "create_sound": "SKAPA LJUD",
        "video_instr": "Instruktion:",
        "create_video": "SKAPA VIDEO",
        "open_studio": "GODKÄNN & ÖPPNA STUDION",
        "studio_title": "STUDIO",
        "artist_id": "ARTIST ID:",
        "lang_label": "Språk:",
        "theme_label": "Tema:",
        "admin_only": "Endast för admin.",
        "admin_panel": "ADMIN PANEL",
    }
}

def get_texts(lang):
    return LANG.get(lang, LANG["Svenska"])

# =========================
# 2. DESIGN
# =========================
def apply_design():
    theme = st.session_state.get("theme", "Neon")
    bg = st.session_state.get("app_bg", None)

    # Globala stilar
    css = """
    <style>
    .stApp { color: white; }
    .stMarkdown, label, p { color: white !important; }
    </style>
    """

    if theme == "Neon":
        css += "<style>h1, h2, h3 { text-shadow: 0 0 10px #0ff, 0 0 20px #0ff; }</style>"
    elif theme == "Cyberpunk":
        css += "<style>h1, h2, h3 { text-shadow: 0 0 15px #ff00ff; }</style>"

    if bg:
        css += f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), url("{bg}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
    else:
        css += "<style>.stApp { background-color: #050505; }</style>"

    st.markdown(css, unsafe_allow_html=True)

# =========================
# 3. AI-MOTOR
# =========================
def generate_image(prompt):
    try:
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
        return str(res[0]) if isinstance(res, list) else str(res)
    except Exception as e:
        st.error(f"Fel: {e}")
        return None

def generate_music(prompt, duration=10):
    try:
        res = replicate.run(
            "facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47",
            input={"prompt": prompt, "duration": duration}
        )
        return str(res)
    except Exception as e:
        st.error(f"Fel: {e}")
        return None

# =========================
# 4. STREAMLIT APP RUN
# =========================
st.set_page_config(page_title="MAXIMUSIKAI 2026", page_icon="⚡", layout="wide")
init_user_db()

# State init
if "artist" not in st.session_state: st.session_state.artist = "ANONYM"
if "agreed" not in st.session_state: st.session_state.agreed = False
if "theme" not in st.session_state: st.session_state.theme = "Neon"
if "app_bg" not in st.session_state: st.session_state.app_bg = None

L = get_texts("Svenska")

# Sidebar
with st.sidebar:
    st.title(L["studio_title"])
    artist_input = st.text_input(L["artist_id"], st.session_state.artist).strip().upper()
    if artist_input: st.session_state.artist = artist_input
    
    user = load_user(st.session_state.artist)
    if user.get("bg") and not st.session_state.app_bg:
        st.session_state.app_bg = user["bg"]
    
    st.metric(L["units"], f"⚡ {user['units']}")
    st.session_state.theme = st.selectbox(L["theme_label"], ["Neon", "Dark", "Cyberpunk"])
    st.divider()

apply_design()

if not st.session_state.agreed:
    st.markdown(f"<h1 style='text-align:center;'>{L['title']}</h1>", unsafe_allow_html=True)
    if st.button(L["open_studio"], use_container_width=True):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# API Token
token = st.secrets.get("REPLICATE_API_TOKEN")
if token: os.environ["REPLICATE_API_TOKEN"] = token

tabs = st.tabs([L["magic_tab"], L["director_tab"], L["music_tab"], L["archive_tab"], L["feed_tab"], L["admin_tab"]])

# --- MAGI ---
with tabs[0]:
    prompt = st.text_area(L["prompt_label"], placeholder="En futuristisk stad i neon...")
    if st.button(L["generate_btn"], use_container_width=True):
        user = load_user(st.session_state.artist)
        if user['units'] > 0 or st.session_state.artist == "TOMAS2026":
            with st.spinner("Skapar magi..."):
                img = generate_image(prompt)
                if img:
                    if st.session_state.artist != "TOMAS2026":
                        update_user(st.session_state.artist, "units", user['units'] - 1)
                    add_to_gallery(st.session_state.artist, prompt, img, None)
                    st.session_state.app_bg = img
                    update_user(st.session_state.artist, "bg", img)
                    st.rerun()
        else:
            st.error("Slut på Units!")

# --- REGI ---
with tabs[1]:
    st.subheader(L["director_tab"])
    st.info("Funktion för att animera dina bilder kommer snart.")

# --- MUSIK ---
with tabs[2]:
    m_prompt = st.text_input(L["beat_label"])
    if st.button(L["create_sound"]):
        with st.spinner("Genererar ljud..."):
            audio = generate_music(m_prompt)
            if audio:
                st.audio(audio)
                add_to_gallery(st.session_state.artist, f"Beat: {m_prompt}", st.session_state.app_bg, audio)

# --- ARKIV ---
with tabs[3]:
    my_items = get_user_gallery(st.session_state.artist)
    if not my_items: st.write(L["no_gallery"])
    for item in reversed(my_items):
        with st.expander(f"🎨 {item['name']}"):
            st.image(item['url'])
            if item.get("audio"): st.audio(item['audio'])
            if st.button("Använd som bakgrund", key=f"bg_{item['id']}"):
                st.session_state.app_bg = item['url']
                update_user(st.session_state.artist, "bg", item['url'])
                st.rerun()

# --- FEED ---
with tabs[4]:
    feed = get_global_feed()
    for item in reversed(feed[-10:]):
        st.markdown(f"**Artist:** {item['artist']}")
        st.image(item['url'], width=500)
        st.divider()

# --- ADMIN ---
with tabs[5]:
    if st.session_state.artist == "TOMAS2026":
        st.subheader(L["admin_panel"])
        db = load_db()
        target = st.selectbox("Välj användare", list(db.keys()))
        amount = st.number_input("Units", 0, 1000, 20)
        if st.button("Uppdatera Units"):
            update_user(target, "units", amount)
            st.success("Uppdaterat!")
    else:
        st.warning(L["admin_only"])
["admin_only"])

  
