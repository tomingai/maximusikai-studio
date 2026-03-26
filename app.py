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

# --- 1. SETUP & SESSION STATE ---

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

# --- 2. DESIGN ---

def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
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
        "api_missing": "API TOKEN SAKNAS"
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
        "download": "💾 DOWNLOAD",
        "studio": "STUDIO",
        "lang_label": "Language:",
        "artist_id": "ARTIST ID:",
        "atmosphere": "ATMOSPHERE",
        "reset_design": "❌ RESET DESIGN",
        "agree_open": "ACCEPT & OPEN STUDIO",
        "prompt_label": "WHAT SHALL WE CREATE?",
        "start_gen": "START GENERATION",
        "no_units": "You are out of Units!",
        "empty_prompt": "Write a prompt first.",
        "ai_working": "AI is working...",
        "luma_sub": "🎬 LUMA DREAM MACHINE",
        "need_magic_first": "Create an image in MAGIC first!",
        "select_image_label": "Select image:",
        "instruction": "Instruction:",
        "create_video": "CREATE VIDEO (5 UNITS)",
        "too_few_units": "Not enough Units!",
        "music_desc": "Describe the beat:",
        "create_sound": "CREATE SOUND",
        "need_music_desc": "Write a description first.",
        "composing": "Composing...",
        "archive_empty": "No saved works.",
        "work_saved": "Your work is created and saved in ARCHIVE & FEED.",
        "no_image": "No image could be created.",
        "bg_fail": "Could not generate background:",
        "img_fail": "Image generation failed:",
        "music_fail": "Music generation failed:",
        "luma_fail": "Luma is busy or requires a paid account.",
        "admin_panel": "ADMIN PANEL",
        "user_db": "User DB:",
        "gallery_cleared": "Gallery cleared.",
        "api_missing": "API TOKEN MISSING"
    },
    "Deutsch": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIE", "🎬 REGIE", "🎧 MUSIK", "📚 ARCHIV", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "WELTRAUM 🌌",
        "atm_forest": "WALD 🌲",
        "atm_city": "STADT 🌆",
        "atm_bake": "BÄCKEREI 🥐",
        "status": "STATUS",
        "units": "EINHEITEN",
        "set_bg": "🖼 ALS HINTERGRUND SETZEN",
        "download": "💾 HERUNTERLADEN",
        "studio": "STUDIO",
        "lang_label": "Sprache:",
        "artist_id": "KÜNSTLER ID:",
        "atmosphere": "ATMOSPHÄRE",
        "reset_design": "❌ DESIGN ZURÜCKSETZEN",
        "agree_open": "AKZEPTIEREN & STUDIO ÖFFNEN",
        "prompt_label": "WAS SOLLEN WIR ERSCHAFFEN?",
        "start_gen": "GENERIERUNG STARTEN",
        "no_units": "Du hast keine Einheiten mehr!",
        "empty_prompt": "Schreibe zuerst eine Prompt.",
        "ai_working": "KI arbeitet...",
        "luma_sub": "🎬 LUMA DREAM MACHINE",
        "need_magic_first": "Erstelle zuerst ein Bild in MAGIE!",
        "select_image_label": "Bild wählen:",
        "instruction": "Anweisung:",
        "create_video": "VIDEO ERSTELLEN (5 EINHEITEN)",
        "too_few_units": "Zu wenige Einheiten!",
        "music_desc": "Beschreibe den Beat:",
        "create_sound": "TON ERSTELLEN",
        "need_music_desc": "Schreibe zuerst eine Beschreibung.",
        "composing": "Komponiere...",
        "archive_empty": "Keine gespeicherten Werke.",
        "work_saved": "Werk erstellt und in ARCHIV & FEED gespeichert.",
        "no_image": "Kein Bild konnte erstellt werden.",
        "bg_fail": "Hintergrund konnte nicht generiert werden:",
        "img_fail": "Bildgenerierung fehlgeschlagen:",
        "music_fail": "Musikgenerierung fehlgeschlagen:",
        "luma_fail": "Luma ist beschäftigt oder benötigt ein Bezahlkonto.",
        "admin_panel": "ADMIN PANEL",
        "user_db": "Benutzer DB:",
        "gallery_cleared": "Galerie geleert.",
        "api_missing": "API TOKEN FEHLT"
    },
    "Français": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIE", "🎬 RÉALISATION", "🎧 MUSIQUE", "📚 ARCHIVE", "🌐 FLUX", "⚙️ ADMIN"],
        "atm_space": "ESPACE 🌌",
        "atm_forest": "FORÊT 🌲",
        "atm_city": "VILLE 🌆",
        "atm_bake": "BOULANGERIE 🥐",
        "status": "STATUT",
        "units": "UNITÉS",
        "set_bg": "🖼 DÉFINIR COMME FOND",
        "download": "💾 TÉLÉCHARGER",
        "studio": "STUDIO",
        "lang_label": "Langue :",
        "artist_id": "ID ARTISTE :",
        "atmosphere": "ATMOSPHÈRE",
        "reset_design": "❌ RÉINITIALISER LE DESIGN",
        "agree_open": "ACCEPTER & OUVRIR LE STUDIO",
        "prompt_label": "QUE VA-T-ON CRÉER ?",
        "start_gen": "LANCER LA GÉNÉRATION",
        "no_units": "Vous n'avez plus d'unités !",
        "empty_prompt": "Écrivez d'abord un prompt.",
        "ai_working": "L'IA travaille...",
        "luma_sub": "🎬 LUMA DREAM MACHINE",
        "need_magic_first": "Créez d'abord une image dans MAGIE !",
        "select_image_label": "Choisir une image :",
        "instruction": "Instruction :",
        "create_video": "CRÉER UNE VIDÉO (5 UNITÉS)",
        "too_few_units": "Pas assez d'unités !",
        "music_desc": "Décrivez le beat :",
        "create_sound": "CRÉER UN SON",
        "need_music_desc": "Écrivez d'abord une description.",
        "composing": "Composition...",
        "archive_empty": "Aucune œuvre enregistrée.",
        "work_saved": "Œuvre créée et enregistrée dans ARCHIVE & FLUX.",
        "no_image": "Aucune image n'a pu être créée.",
        "bg_fail": "Impossible de générer le fond :",
        "img_fail": "Échec de la génération d'image :",
        "music_fail": "Échec de la génération de musique :",
        "luma_fail": "Luma est occupé ou nécessite un compte payant.",
        "admin_panel": "PANEL ADMIN",
        "user_db": "Base utilisateurs :",
        "gallery_cleared": "Galerie vidée.",
        "api_missing": "TOKEN API MANQUANT"
    },
    "Español": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIA", "🎬 DIRECCIÓN", "🎧 MÚSICA", "📚 ARCHIVO", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "ESPACIO 🌌",
        "atm_forest": "BOSQUE 🌲",
        "atm_city": "CIUDAD 🌆",
        "atm_bake": "PANADERÍA 🥐",
        "status": "ESTADO",
        "units": "UNIDADES",
        "set_bg": "🖼 ESTABLECER COMO FONDO",
        "download": "💾 DESCARGAR",
        "studio": "ESTUDIO",
        "lang_label": "Idioma:",
        "artist_id": "ID ARTISTA:",
        "atmosphere": "ATMÓSFERA",
        "reset_design": "❌ RESTABLECER DISEÑO",
        "agree_open": "ACEPTAR Y ABRIR ESTUDIO",
        "prompt_label": "¿QUÉ VAMOS A CREAR?",
        "start_gen": "INICIAR GENERACIÓN",
        "no_units": "¡No te quedan unidades!",
        "empty_prompt": "Escribe un prompt primero.",
        "ai_working": "La IA está trabajando...",
        "luma_sub": "🎬 LUMA DREAM MACHINE",
        "need_magic_first": "¡Crea primero una imagen en MAGIA!",
        "select_image_label": "Seleccionar imagen:",
        "instruction": "Instrucción:",
        "create_video": "CREAR VIDEO (5 UNIDADES)",
        "too_few_units": "¡No hay suficientes unidades!",
        "music_desc": "Describe el beat:",
        "create_sound": "CREAR SONIDO",
        "need_music_desc": "Escribe una descripción primero.",
        "composing": "Componiendo...",
        "archive_empty": "No hay obras guardadas.",
        "work_saved": "Obra creada y guardada en ARCHIVO & FEED.",
        "no_image": "No se pudo crear ninguna imagen.",
        "bg_fail": "No se pudo generar el fondo:",
        "img_fail": "Fallo en la generación de imagen:",
        "music_fail": "Fallo en la generación de música:",
        "luma_fail": "Luma está ocupado o requiere cuenta de pago.",
        "admin_panel": "PANEL ADMIN",
        "user_db": "Base de usuarios:",
        "gallery_cleared": "Galería vaciada.",
        "api_missing": "FALTA TOKEN DE API"
    },
    "Italiano": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIA", "🎬 REGIA", "🎧 MUSICA", "📚 ARCHIVIO", "🌐 FEED", "⚙️ ADMIN"],
        "atm_space": "SPAZIO 🌌",
        "atm_forest": "FORESTA 🌲",
        "atm_city": "CITTÀ 🌆",
        "atm_bake": "PANETTERIA 🥐",
        "status": "STATO",
        "units": "UNITÀ",
        "set_bg": "🖼 IMPOSTA COME SFONDO",
        "download": "💾 SCARICA",
        "studio": "STUDIO",
        "lang_label": "Lingua:",
        "artist_id": "ID ARTISTA:",
        "atmosphere": "ATMOSFERA",
        "reset_design": "❌ REIMPOSTA DESIGN",
        "agree_open": "ACCETTA E APRI LO STUDIO",
        "prompt_label": "COSA CREIAMO?",
        "start_gen": "AVVIA GENERAZIONE",
        "no_units": "Hai finito le unità!",
        "empty_prompt": "Scrivi prima un prompt.",
        "ai_working": "L'IA sta lavorando...",
        "luma_sub": "🎬 LUMA DREAM MACHINE",
        "need_magic_first": "Crea prima un'immagine in MAGIA!",
        "select_image_label": "Seleziona immagine:",
        "instruction": "Istruzione:",
        "create_video": "CREA VIDEO (5 UNITÀ)",
        "too_few_units": "Unità insufficienti!",
        "music_desc": "Descrivi il beat:",
        "create_sound": "CREA SUONO",
        "need_music_desc": "Scrivi prima una descrizione.",
        "composing": "Composizione...",
        "archive_empty": "Nessuna opera salvata.",
        "work_saved": "Opera creata e salvata in ARCHIVIO & FEED.",
        "no_image": "Impossibile creare un'immagine.",
        "bg_fail": "Impossibile generare lo sfondo:",
        "img_fail": "Generazione immagine fallita:",
        "
