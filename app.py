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
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_user(artist_id):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {
            "units": 20,
            "bg": None,
            "gallery": []
        }
        save_db(db)
    return db[artist_id]

def update_user(artist_id, key, value):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {
            "units": 20,
            "bg": None,
            "gallery": []
        }
    db[artist_id][key] = value
    save_db(db)

def add_to_gallery(artist, name, img_url, audio_url):
    db = load_db()
    if artist not in db:
        db[artist] = {
            "units": 20,
            "bg": None,
            "gallery": []
        }
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
    if artist not in db:
        return []
    return db[artist].get("gallery", [])

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

    base_css = """
    <style>
    .stApp {
        background-color: #050505;
        color: white;
    }
    h1, h2, h3 {
        font-weight: 900;
    }
    </style>
    """

    neon_css = """
    <style>
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    h1, h2, h3 {
        text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
    }
    </style>
    """

    cyber_css = """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1a2a3a, #000000);
        color: #e0e0ff;
    }
    h1, h2, h3 {
        text-shadow: 0 0 15px #ff00ff;
    }
    </style>
    """

    if bg:
        bg_css = f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), url("{bg}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
            color: white;
        }}
        </style>
        """
    else:
        bg_css = ""

    if theme == "Neon":
        css = neon_css
    elif theme == "Cyberpunk":
        css = cyber_css
    else:
        css = base_css

    st.markdown(css + bg_css, unsafe_allow_html=True)

def theme_selector(label):
    st.session_state.theme = st.selectbox(
        label,
        ["Neon", "Dark", "Cyberpunk"],
        index=["Neon", "Dark", "Cyberpunk"].index(st.session_state.get("theme", "Neon"))
    )

# =========================
# 3. AI-MOTOR
# =========================

def generate_image(prompt):
    if not prompt.strip():
        return None
    try:
        res = replicate.run(
            "black-forest-labs/flux-schnell",
            input={"prompt": prompt}
        )
        if isinstance(res, list) and len(res) > 0:
            return str(res[0])
        return str(res)
    except Exception as e:
        st.error(f"Bildgenerering misslyckades: {e}")
        return None

def generate_music(prompt, duration=10):
    if not prompt.strip():
        return None
    try:
        res = replicate.run(
            "facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47",
            input={"prompt": prompt, "duration": duration}
        )
        return str(res)
    except Exception as e:
        st.error(f"Musikgenerering misslyckades: {e}")
        return None

def generate_video(prompt, image_url):
    if not prompt.strip() or not image_url:
        return None
    try:
        res = replicate.run(
            "luma-ai/luma-dream-machine",
            input={"prompt": prompt, "image_url": image_url}
        )
        if isinstance(res, list) and len(res) > 0:
            return str(res[0])
        return str(res)
    except Exception as e:
        st.error(f"Videogenerering misslyckades: {e}")
        return None

# =========================
# 4. STREAMLIT APP
# =========================

st.set_page_config(
    page_title="MAXIMUSIKAI SUPER STUDIO 2026",
    page_icon="⚡",
    layout="wide"
)

init_user_db()

if "artist" not in st.session_state:
    st.session_state.artist = "ANONYM"
if "lang" not in st.session_state:
    st.session_state.lang = "Svenska"
if "agreed" not in st.session_state:
    st.session_state.agreed = False
if "theme" not in st.session_state:
    st.session_state.theme = "Neon"
if "app_bg" not in st.session_state:
    st.session_state.app_bg = None

L = get_texts(st.session_state.lang)

with st.sidebar:
    st.title(L["studio_title"])
    st.session_state.lang = st.radio(L["lang_label"], ["Svenska"], horizontal=True)
    L = get_texts(st.session_state.lang)

    artist = st.text_input(L["artist_id"], st.session_state.artist).strip().upper()
    if artist == "":
        artist = "ANONYM"
    st.session_state.artist = artist

    user = load_user(artist)
    units = user.get("units", 0)

    if user.get("bg") and st.session_state.app_bg is None:
        st.session_state.app_bg = user["bg"]

    st.info(f"{L['status']}: ⚡ {units} {L['units']}")

    st.divider()
    theme_selector(L["theme_label"])

apply_design()

st.markdown(
    f"<h1 style='text-align:center;'>⚡ {L['title']} ⚡</h1>",
    unsafe_allow_html=True
)

if not st.session_state.agreed:
    if st.button(L["open_studio"]):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN", None)
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
else:
    st.warning("REPLICATE_API_TOKEN saknas i st.secrets. Vissa AI-funktioner kommer inte fungera.")

tabs = st.tabs([
    L["magic_tab"],
    L["director_tab"],
    L["music_tab"],
    L["archive_tab"],
    L["feed_tab"],
    L["admin_tab"]
])

# =========================
# TAB 1: MAGI
# =========================

with tabs[0]:
    st.subheader(L["magic_tab"])
    prompt = st.text_area(L["prompt_label"])

    if st.button(L["generate_btn"]):
        if not prompt.strip():
            st.error("Skriv en prompt först.")
        else:
            with st.status("AI arbetar..."):
                user = load_user(artist)
                units = user.get("units", 0)
                is_admin = (artist == "TOMAS2026")

                if units <= 0 and not is_admin:
                    st.error("Du har slut på Units!")
                else:
                    if not is_admin:
                        user["units"] = max(0, units - 1)
                        db = load_db()
                        db[artist] = user
                        save_db(db)

                    img_url = generate_image(prompt)
                    mu_url = generate_music(prompt, duration=10)

                    if img_url:
                        if st.session_state.app_bg is None:
                            st.session_state.app_bg = img_url
                            user["bg"] = img_url
                            db = load_db()
                            db[artist] = user
                            save_db(db)

                        add_to_gallery(artist, prompt, img_url, mu_url)
                        st.success("Verket är skapat och sparat i ARKIV & FEED.")
                        st.image(img_url)
                        if mu_url:
                            st.audio(mu_url)
                        st.rerun()
                    else:
                        st.error("Ingen bild kunde skapas.")

# =========================
# TAB 2: REGI
# =========================

with tabs[1]:
    st.subheader(L["director_tab"])
    gallery = get_user_gallery(artist)

    if not gallery:
        st.info(L["create_first"])
    else:
        names = [g["name"] for g in gallery]
        choice = st.selectbox("Välj bild:", names)
        selected = next(g for g in gallery if g["name"] == choice)

        st.image(selected["url"], width=300)
        vid_prompt = st.text_input(L["video_instr"], "Cinematic motion")

        if st.button(L["create_video"]):
            with st.status("Skapar video..."):
                vid_url = generate_video(vid_prompt, selected["url"])
                if vid_url:
                    st.video(vid_url)
                else:
                    st.error("Ingen video kunde skapas.")

# =========================
# TAB 3: MUSIK
# =========================

with tabs[2]:
    st.subheader(L["music_tab"])
    mu_prompt = st.text_input(L["beat_label"])

    if st.button(L["create_sound"]):
        if not mu_prompt.strip():
            st.error("Skriv en beskrivning först.")
        else:
            with st.spinner("Komponerar..."):
                mu_url = generate_music(mu_prompt, duration=12)
                if mu_url:
                    st.audio(mu_url)
                else:
                    st.error("Ingen musik kunde skapas.")

# =========================
# TAB 4: ARKIV
# =========================

with tabs[3]:
    st.subheader(L["archive_tab"])
    gallery = get_user_gallery(artist)

    if not gallery:
        st.info(L["no_gallery"])
    else:
        for g in reversed(gallery):
            with st.expander(g["name"]):
                st.image(g["url"])
                c1, c2 = st.columns(2)
                if c1.button("Sätt som bakgrund", key=f"bg_{g['id']}"):
                    st.session_state.app_bg = g["url"]
                    user = load_user(artist)
                    user["bg"] = g["url"]
                    db = load_db()
                    db[artist] = user
                    save_db(db)
                    st.rerun()
                try:
                    img_data = requests.get(g["url"], timeout=10).content
                    c2.download_button(
                        "Ladda ner",
                        data=img_data,
                        file_name=f"{g['name']}.png",
                        mime="image/png",
                        key=f"dl_{g['id']}"
                    )
                except Exception:
                    pass
                if g["audio"]:
                    st.audio(g["audio"])

# =========================
# TAB 5: FEED
# =========================

with tabs[4]:
    st.subheader(L["feed_tab"])
    feed = get_global_feed()
    if not feed:
        st.info("Inga verk i feeden ännu.")
    else:
        for g in reversed(feed[-20:]):
            st.image(g["url"], caption=f"Artist: {g['artist']}")
            if g["audio"]:
                st.audio(g["audio"])
            st.divider()

# =========================
# TAB 6: ADMIN
# =========================

with tabs[5]:
    if st.session_state.artist == "TOMAS2026":
        st.subheader(L["admin_panel"])
        db = load_db()
        st.write("User DB:", db)
        if st.button("RENSA GALLERY FÖR ALLA"):
            for a in db:
                db[a]["gallery"] = []
            save_db(db)
            st.success("Alla gallerier rensade.")
            st.rerun()
    else:
        st.warning(L["admin_only"])

  
