import streamlit as st
import replicate
import os
import time
import requests
import json
import os.path

# --- 0. DATABAS FÖR ANVÄNDARE (UNITS + BAKGRUND) ---

DB_FILE = "users.json"

def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# --- 1. SETUP & SESSION STATE (LÅST GRUND) ---

st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

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

# --- 2. DESIGN-MOTOR (HELT LÅST) ---

def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
                background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
            }}
            .logo-text {{
                font-size: 3rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
                text-transform: uppercase; letter-spacing: 5px;
                text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00d2ff, 0 0 40px #00d2ff !important;
                margin-bottom: 20px;
            }}
            div[data-baseweb="base-input"], div[data-baseweb="textarea"], .stTextArea textarea, .stTextInput input {{
                background-color: rgba(255,255,255,0.1) !important; color: white !important;
                backdrop-filter: blur(15px) !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important;
            }}
            label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
                color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; font-weight: 800 !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(0,0,0,0.4) !important; border-radius: 10px !important; }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 3. HJÄLPFUNKTION FÖR URL ---

def get_url(res):
    if isinstance(res, list):
        return str(res[0])
    if hasattr(res, "url"):
        return str(res.url)
    return str(res)

# --- 4. SPRÅK ---

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
        "download": "💾 LADDA NER"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "SPACE 🌌",
        "atm_forest": "FOREST 🌲",
        "atm_city": "CITY 🌆",
        "atm_bake": "BAKING 🥐",
        "status": "STATUS",
        "units": "UNITS",
        "set_bg": "🖼 SET AS BACKGROUND",
        "download": "💾 DOWNLOAD"
    }
}
L = texts[st.session_state.lang]

# --- 5. SIDOMENY / "LOGIN" VIA ARTIST ID ---

with st.sidebar:
    st.title("STUDIO")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English"], horizontal=True)

    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id == "":
        artist_id = "ANONYM"

    # Se till att artist finns i user_db med struktur
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = {
            "units": 10,
            "bg": None
        }
        save_user_db(st.session_state.user_db)

    user_entry = st.session_state.user_db[artist_id]
    u_creds = user_entry.get("units", 0)
    is_admin = (artist_id == "TOMAS2026")

    # Ladda bakgrund från DB om ingen satt i sessionen
    if st.session_state.app_bg is None and user_entry.get("bg"):
        st.session_state.app_bg = user_entry["bg"]

    u_units_label = L["units"]
    status_msg = "💎 ADMIN" if is_admin else f"⚡ {u_creds} {u_units_label}"
    st.info(f"{L['status']}: {status_msg}")

    st.divider()
    st.subheader("ATMOSPHERE")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    def set_bg_and_save(url):
        st.session_state.app_bg = url
        st.session_state.user_db[artist_id]["bg"] = url
        save_user_db(st.session_state.user_db)
        st.rerun()

    if c1.button(L["atm_space"]):
        try:
            img = replicate.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": "Deep space nebula, 4k"}
            )
            set_bg_and_save(get_url(img))
        except Exception as e:
            st.error(f"Kunde inte generera bakgrund: {e}")

    if c2.button(L["atm_forest"]):
        try:
            img = replicate.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": "Magic forest, sunlight, 4k"}
            )
            set_bg_and_save(get_url(img))
        except Exception as e:
            st.error(f"Kunde inte generera bakgrund: {e}")

    if c3.button(L["atm_city"]):
        try:
            img = replicate.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": "Cyberpunk city neon, 4k"}
            )
            set_bg_and_save(get_url(img))
        except Exception as e:
            st.error(f"Kunde inte generera bakgrund: {e}")

    if c4.button(L["atm_bake"]):
        try:
            img = replicate.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": "Artisan bakery, 4k"}
            )
            set_bg_and_save(get_url(img))
        except Exception as e:
            st.error(f"Kunde inte generera bakgrund: {e}")

    if st.button("❌ NOLLSTÄLL DESIGN"):
        st.session_state.app_bg = None
        st.session_state.user_db[artist_id]["bg"] = None
        save_user_db(st.session_state.user_db)
        st.rerun()

# --- 6. HUVUDAPP ---

apply_design()
st.markdown(f'<div class="logo-text">⚡ {L["title"]} ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tab_list = L["tab_names"] if is_admin else L["tab_names"][:-1]
    tabs = st.tabs(tab_list)

    # --- MAGI ---
    with tabs[0]:
        prompt = st.text_area("VAD SKALL VI SKAPA?", key="main_p")
        if st.button("STARTA GENERERING", use_container_width=True):
            if not prompt.strip():
                st.error("Skriv en prompt först.")
            elif u_creds <= 0 and not is_admin:
                st.error("Du har slut på Units!")
            else:
                with st.status("AI arbetar..."):
                    # Dra 1 unit
                    if not is_admin:
                        st.session_state.user_db[artist_id]["units"] = max(
                            0, st.session_state.user_db[artist_id]["units"] - 1
                        )
                        save_user_db(st.session_state.user_db)

                    img_url = None
                    mu_url = None

                    # Bild
                    try:
                        img_res = replicate.run(
                            "black-forest-labs/flux-schnell",
                            input={"prompt": prompt}
                        )
                        img_url = get_url(img_res)
                    except Exception as e:
                        st.error(f"Bildgenerering misslyckades: {e}")

                    # Musik
                    try:
                        mu_res = replicate.run(
                            "facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47",
                            input={"prompt": prompt, "duration": 8}
                        )
                        mu_url = str(mu_res)
                    except Exception:
                        mu_url = None

                    if img_url:
                        if st.session_state.app_bg is None:
                            st.session_state.app_bg = img_url
                            st.session_state.user_db[artist_id]["bg"] = img_url
                            save_user_db(st.session_state.user_db)

                        st.session_state.gallery.append({
                            "id": time.time(),
                            "artist": artist_id,
                            "name": (prompt[:20] or "UNTITLED"),
                            "url": img_url,
                            "audio": mu_url
                        })
                        st.success("Verket är skapat och sparat i ARKIV & FEED.")
                        st.image(img_url)
                        if mu_url:
                            st.audio(mu_url)
                        st.rerun()
                    else:
                        st.error("Ingen bild kunde skapas.")

    # --- REGI ---
    with tabs[1]:
        st.subheader("🎬 LUMA DREAM MACHINE")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_imgs:
            st.info("Skapa en bild i MAGI först!")
        else:
            img_choice = st.selectbox("Välj bild:", [p["name"] for p in my_imgs])
            selected = next(p for p in my_imgs if p["name"] == img_choice)
            selected_url = selected["url"]
            st.image(selected_url, width=300)
            vid_p = st.text_input("Instruktion:", "Cinematic motion")
            if st.button("SKAPA VIDEO (5 UNITS)"):
                current_units = st.session_state.user_db[artist_id]["units"]
                if not is_admin and current_units < 5:
                    st.error("För få Units!")
                else:
                    with st.status("Luma arbetar..."):
                        try:
                            if not is_admin:
                                st.session_state.user_db[artist_id]["units"] = max(
                                    0, current_units - 5
                                )
                                save_user_db(st.session_state.user_db)
                            vid_res = replicate.run(
                                "luma-ai/luma-dream-machine",
                                input={"prompt": vid_p, "image_url": selected_url}
                            )
                            st.video(get_url(vid_res))
                        except Exception as e:
                            st.error(f"Luma är upptagen eller kräver betalkonto. ({e})")

    # --- MUSIK ---
    with tabs[2]:
        mu_in = st.text_input("Beskriv beatet:", key="mu_input")
        if st.button("SKAPA LJUD"):
            if not mu_in.strip():
                st.error("Skriv en beskrivning först.")
            else:
                with st.spinner("Komponerar..."):
                    try:
                        res = replicate.run(
                            "facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47",
                            input={"prompt": mu_in, "duration": 10}
                        )
                        st.audio(str(res))
                    except Exception as e:
                        st.error(f"Musikgenerering misslyckades: {e}")

    # --- ARKIV ---
    with tabs[3]:
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my:
            st.info("Inga sparade verk.")
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(str(p["url"]))
                c1, c2 = st.columns(2)
                if c1.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = str(p["url"])
                    st.session_state.user_db[artist_id]["bg"] = str(p["url"])
                    save_user_db(st.session_state.user_db)
                    st.rerun()
                try:
                    img_data = requests.get(p["url"], timeout=10).content
                    c2.download_button(
                        L["download"],
                        data=img_data,
                        file_name=f"{p['name']}.png",
                        mime="image/png",
                        key=f"dl_{p['id']}"
                    )
                except Exception:
                    pass
                if p["audio"]:
                    st.audio(str(p["audio"]))

    # --- FEED ---
    with tabs[4]:
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(str(p["url"]), caption=f"Artist: {p['artist']}")
            if p["audio"]:
                st.audio(str(p["audio"]))
            st.divider()

    # --- ADMIN ---
    if is_admin and len(tabs) > 5:
        with tabs[5]:
            st.subheader("ADMIN PANEL")
            st.write("User DB:", st.session_state.user_db)
            if st.button("RENSA GALLERY"):
                st.session_state.gallery = []
                st.success("Gallery rensat.")
                st.rerun()
else:
    st.error("API TOKEN SAKNAS")














































































































































































































































































