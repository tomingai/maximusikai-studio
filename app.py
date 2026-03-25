import streamlit as st
import os
import json
import time

# --- 0. DATABAS FÖR ANVÄNDARE (UNITS + BAKGRUND) ---

DB_FILE = "users.json"


def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_user_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


# --- 1. SETUP & SESSION STATE ---

st.set_page_config(
    page_title="MAXIMUSIKAI STUDIO PRO 2026",
    page_icon="⚡",
    layout="wide",
)

if "gallery" not in st.session_state:
    st.session_state.gallery = []

if "user_db" not in st.session_state:
    st.session_state.user_db = load_user_db()

if "app_bg" not in st.session_state:
    st.session_state.app_bg = None

if "agreed" not in st.session_state:
    st.session_state.agreed = False

if "lang" not in st.session_state:
    st.session_state.lang = "Svenska"

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "units" not in st.session_state:
    st.session_state.units = 0


# --- 2. DESIGN ---

def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('{bg_url}') !important;
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
            }}
            .logo-text {{
                font-size: 3rem !important;
                font-weight: 900 !important;
                color: #fff !important;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 5px;
                text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00d2ff, 0 0 40px #00d2ff !important;
                margin-bottom: 20px;
            }}
            div[data-baseweb="base-input"], div[data-baseweb="textarea"], .stTextArea textarea, .stTextInput input {{
                background-color: rgba(255,255,255,0.1) !important;
                color: white !important;
                backdrop-filter: blur(15px) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                border-radius: 12px !important;
            }}
            label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{
                color: white !important;
                text-shadow: 2px 2px 8px rgba(0,0,0,1) !important;
                font-weight: 800 !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                background-color: rgba(0,0,0,0.4) !important;
                border-radius: 10px !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<style>.stApp { background-color: #050505 !important; }</style>",
            unsafe_allow_html=True,
        )


# --- 3. HJÄLPFUNKTION FÖR URL (OM DU SENARE ANVÄNDER API-RESPONSER) ---

def get_url(res):
    if isinstance(res, list) and res:
        return str(res[0])
    if hasattr(res, "url"):
        return str(res.url)
    return str(res)


# --- 4. SPRÅK / TEXTER ---

texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "RYMDEN 🌌",
        "atm_forest": "SKOGEN 🌲",
        "atm_city": "STADEN 🌆",
        "atm_bake": "BAKNING 🥐",
        "status": "STATUS",
        "units": "UNITS",
        "set_bg": "🖼 SÄTT SOM BAKGRUND",
        "download": "💾 LADDA NER",
        "studio": "STUDIO",
        "lang_label": "Språk:",
        "artist_id": "ARTIST ID:",
        "atmosphere": "ATMOSFÄR",
        "reset_design": "❌ NOLLSTÄLL DESIGN",
        "agree_open": "GODKÄNN & ÖPPNA STUDION",
        "prompt_label": "VAD SKALL VI SKAPA?",
        "start_gen": "STARTA GENERERING",
        "no_units": "Du har slut på Units!",
        "empty_prompt": "Skriv en prompt först.",
        "ai_working": "AI arbetar...",
        "luma_sub": "🎬 LUMA DREAM MACHINE",
        "need_magic_first": "Skapa en bild i MAGI först!",
        "select_image_label": "Välj bild:",
        "instruction": "Instruktion:",
        "create_video": "SKAPA VIDEO (5 UNITS)",
        "too_few_units": "För få Units!",
        "music_desc": "Beskriv beatet:",
        "create_sound": "SKAPA LJUD",
        "need_music_desc": "Skriv en beskrivning först.",
        "composing": "Komponerar...",
        "archive_empty": "Inga sparade verk.",
        "work_saved": "Verket är skapat och sparat i ARKIV & FEED.",
        "no_image": "Ingen bild kunde skapas.",
        "bg_fail": "Kunde inte generera bakgrund:",
        "img_fail": "Bildgenerering misslyckades:",
        "music_fail": "Musikgenerering misslyckades:",
        "luma_fail": "Luma är upptagen eller kräver betalkonto.",
        "admin_panel": "ADMIN PANEL",
        "user_db": "User DB:",
        "gallery_cleared": "Gallery rensat.",
        "api_missing": "API TOKEN SAKNAS",
    }
}


# --- 5. FUNKTIONER FÖR ANVÄNDARE / UNITS ---

def get_or_create_user(user_id: str):
    db = st.session_state.user_db
    if user_id not in db:
        db[user_id] = {
            "units": 20,
            "bg_url": None,
            "gallery": [],
        }
        save_user_db(db)
    return db[user_id]


def update_user(user_id: str, data: dict):
    db = st.session_state.user_db
    db[user_id].update(data)
    save_user_db(db)


# --- 6. SIDOPANEL (SPRÅK, ARTIST, ATMOSFÄR) ---

def sidebar_ui():
    t = texts[st.session_state.lang]

    with st.sidebar:
        st.markdown(f"### {t['studio']}")
        lang = st.selectbox(t["lang_label"], list(texts.keys()), index=list(texts.keys()).index(st.session_state.lang))
        st.session_state.lang = lang
        t = texts[st.session_state.lang]

        artist_id = st.text_input(t["artist_id"], value=st.session_state.current_user or "")
        if st.button("🔑 Logga in / skapa"):
            if artist_id.strip():
                user = get_or_create_user(artist_id.strip())
                st.session_state.current_user = artist_id.strip()
                st.session_state.units = user["units"]
                st.session_state.app_bg = user.get("bg_url")
                st.session_state.gallery = user.get("gallery", [])
                st.success(f"Inloggad som {artist_id}")
            else:
                st.warning("Fyll i ett ARTIST ID.")

        st.markdown(f"**{t['status']}:**")
        st.write(f"{t['units']}: {st.session_state.units}")

        st.markdown(f"**{t['atmosphere']}**")
        atm = st.radio(
            " ",
            [t["atm_space"], t["atm_forest"], t["atm_city"], t["atm_bake"]],
            label_visibility="collapsed",
        )

        # Dummy bakgrunds-URL beroende på val (du kan koppla till riktig bildgenerator sen)
        bg_map = {
            t["atm_space"]: "https://images.pexels.com/photos/2150/sky-space-dark-galaxy.jpg",
            t["atm_forest"]: "https://images.pexels.com/photos/4827/nature-forest-trees-fog.jpg",
            t["atm_city"]: "https://images.pexels.com/photos/373912/pexels-photo-373912.jpeg",
            t["atm_bake"]: "https://images.pexels.com/photos/230325/pexels-photo-230325.jpeg",
        }
        if st.button(t["set_bg"]):
            if st.session_state.current_user:
                st.session_state.app_bg = bg_map.get(atm)
                update_user(st.session_state.current_user, {"bg_url": st.session_state.app_bg})
                st.success("Bakgrund uppdaterad.")
            else:
                st.warning("Logga in med ARTIST ID först.")

        if st.button(t["reset_design"]):
            st.session_state.app_bg = None
            if st.session_state.current_user:
                update_user(st.session_state.current_user, {"bg_url": None})
            st.info("Design nollställd.")


# --- 7. HUVUDINNEHÅLL / TABS ---

def tab_magi():
    t = texts[st.session_state.lang]
    st.subheader("🪄 MAGI – Bildgenerering (mock)")

    prompt = st.text_area(t["prompt_label"])
    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button(t["start_gen"]):
            if not st.session_state.current_user:
                st.warning("Logga in först.")
                return
            if not prompt.strip():
                st.warning(t["empty_prompt"])
                return
            if st.session_state.units <= 0:
                st.error(t["no_units"])
                return

            with st.spinner(t["ai_working"]):
                time.sleep(2)  # mock
                # Dummybild
                img_url = "https://images.pexels.com/photos/1767434/pexels-photo-1767434.jpeg"
                st.session_state.units -= 1

                work = {
                    "type": "image",
                    "prompt": prompt,
                    "url": img_url,
                    "timestamp": time.time(),
                }
                st.session_state.gallery.append(work)
                if st.session_state.current_user:
                    update_user(
                        st.session_state.current_user,
                        {
                            "units": st.session_state.units,
                            "gallery": st.session_state.gallery,
                        },
                    )
                st.success(t["work_saved"])

    with col2:
        if st.session_state.gallery:
            last_images = [w for w in st.session_state.gallery if w["type"] == "image"]
            if last_images:
                st.markdown("**Senaste bild:**")
                st.image(last_images[-1]["url"], use_container_width=True)
        else:
            st.info("Inga bilder ännu.")


def tab_regi():
    t = texts[st.session_state.lang]
    st.subheader("🎬 REGI – Video (mock)")

    if not st.session_state.gallery:
        st.info(t["need_magic_first"])
        return

    images = [w for w in st.session_state.gallery if w["type"] == "image"]
    if not images:
        st.info(t["need_magic_first"])
        return

    options = [f"Bild {i+1}: {w['prompt'][:40]}" for i, w in enumerate(images)]
    idx = st.selectbox(t["select_image_label"], range(len(images)), format_func=lambda i: options[i])
    instruction = st.text_area(t["instruction"])

    if st.button(t["create_video"]):
        if not st.session_state.current_user:
            st.warning("Logga in först.")
            return
        if st.session_state.units < 5:
            st.error(t["too_few_units"])
            return
        if not instruction.strip():
            st.warning("Skriv en instruktion först.")
            return

        with st.spinner(t["ai_working"]):
            time.sleep(3)  # mock
            st.session_state.units -= 5
            video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
            work = {
                "type": "video",
                "prompt": instruction,
                "from_image": images[idx]["url"],
                "url": video_url,
                "timestamp": time.time(),
            }
            st.session_state.gallery.append(work)
            if st.session_state.current_user:
                update_user(
                    st.session_state.current_user,
                    {
                        "units": st.session_state.units,
                        "gallery": st.session_state.gallery,
                    },
                )
            st.success(t["work_saved"])

    if st.session_state.gallery:
        vids = [w for w in st.session_state.gallery if w["type"] == "video"]
        if vids:
            st.markdown("**Senaste video:**")
            st.video(vids[-1]["url"])


def tab_musik():
    t = texts[st.session_state.lang]
    st.subheader("🎧 MUSIK – Ljud (mock)")

    desc = st.text_area(t["music_desc"])

    if st.button(t["create_sound"]):
        if not st.session_state.current_user:
            st.warning("Logga in först.")
            return
        if not desc.strip():
            st.warning(t["need_music_desc"])
            return
        if st.session_state.units <= 0:
            st.error(t["no_units"])
            return

        with st.spinner(t["composing"]):
            time.sleep(2)  # mock
            st.session_state.units -= 1
            audio_url = "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav"
            work = {
                "type": "audio",
                "prompt": desc,
                "url": audio_url,
                "timestamp": time.time(),
            }
            st.session_state.gallery.append(work)
            if st.session_state.current_user:
                update_user(
                    st.session_state.current_user,
                    {
                        "units": st.session_state.units,
                        "gallery": st.session_state.gallery,
                    },
                )
            st.success(t["work_saved"])

    if st.session_state.gallery:
        audios = [w for w in st.session_state.gallery if w["type"] == "audio"]
        if audios:
            st.markdown("**Senaste ljud:**")
            st.audio(audios[-1]["url"])


def tab_arkiv():
    t = texts[st.session_state.lang]
    st.subheader("📚 ARKIV")

    if not st.session_state.gallery:
        st.info(t["archive_empty"])
        return

    for i, w in enumerate(sorted(st.session_state.gallery, key=lambda x: x["timestamp"], reverse=True)):
        st.markdown(f"### #{i+1} – {w['type'].upper()}")
        st.write(f"Prompt: {w['prompt']}")
        if w["type"] == "image":
            st.image(w["url"], use_container_width=True)
        elif w["type"] == "video":
            st.video(w["url"])
        elif w["type"] == "audio":
            st.audio(w["url"])
        st.markdown("---")


def tab_feed():
    t = texts[st.session_state.lang]
    st.subheader("🌐 FEED")

    if not st.session_state.gallery:
        st.info(t["archive_empty"])
        return

    st.write("En enkel feed över dina senaste verk:")
    for w in sorted(st.session_state.gallery, key=lambda x: x["timestamp"], reverse=True)[:10]:
        st.markdown(f"**{w['type'].upper()}** – {w['prompt'][:80]}")
        if w["type"] == "image":
            st.image(w["url"], use_container_width=True)
        elif w["type"] == "video":
            st.video(w["url"])
        elif w["type"] == "audio":
            st.audio(w["url"])
        st.markdown("---")


def tab_admin():
    t = texts[st.session_state.lang]
    st.subheader(f"⚙️ {t['admin_panel']}")

    st.markdown("### " + t["user_db"])
    st.json(st.session_state.user_db)

    if st.button("🧹 Rensa gallery (endast session)"):
        st.session_state.gallery = []
        st.success(t["gallery_cleared"])

    if st.session_state.current_user:
        if st.button("➕ Ge mig 50 units (dev)"):
            st.session_state.units += 50
            update_user(st.session_state.current_user, {"units": st.session_state.units})
            st.success(f"Units uppdaterade: {st.session_state.units}")


# --- 8. HUVUDAPP ---

def main():
    apply_design()
    t = texts[st.session_state.lang]

    st.markdown(f"<div class='logo-text'>{t['title']}</div>", unsafe_allow_html=True)

    sidebar_ui()

    if not st.session_state.current_user:
        st.info("Logga in med ARTIST ID i sidopanelen för att öppna studion.")
        return

    tabs = st.tabs(t["tab_names"])

    with tabs[0]:
        tab_magi()
    with tabs[1]:
        tab_regi()
    with tabs[2]:
        tab_musik()
    with tabs[3]:
        tab_arkiv()
    with tabs[4]:
        tab_feed()
    with tabs[5]:
        tab_admin()


if __name__ == "__main__":
    main()

