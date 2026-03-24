import streamlit as st
import replicate
import os
import requests
import time
import datetime
import json
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

DB_FILE = "maximusikai_archive.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

if "gallery" not in st.session_state: st.session_state.gallery = load_data()
if "community_feed" not in st.session_state: st.session_state.community_feed = []
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"

# --- 2. THEME & LANGUAGES ---
theme_options = {"Neon Purple": "#bf00ff", "Cyber Amber": "#ffaa00", "Electric Blue": "#00f2ff", "Acid Green": "#ccff00"}
main_color = st.session_state.theme_color

LANG_MAP = {
    "Svenska": {"t": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"], "p": "VAD SKALL VI SKAPA?", "b": "STARTA", "a": "ARTIST", "m": "VÄLJ STIL:", "dur": "LÄNGD (SEK):", "v_label": "RÖST (MELODI):", "live": "SENASTE", "remix": "REMIX", "theme": "FÄRGTEMA:", "warn": "⚠️ VARNING: Lång produktionstid vald!", "ly_instr": "Skriv på svenska."},
    "English": {"t": ["🪄 MAGIC", "🎬 DIRECT", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED"], "p": "WHAT TO CREATE?", "b": "START", "a": "ARTIST", "m": "SELECT STYLE:", "dur": "DURATION (SEC):", "v_label": "VOICE (MELODY):", "live": "LATEST", "remix": "REMIX", "theme": "THEME COLOR:", "warn": "⚠️ WARNING: Long production time!", "ly_instr": "Write in English."},
    "Deutsch": {"t": ["🪄 MAGIE", "🎬 REGIE", "🎧 MUSIK", "📚 ARCHIV", "🌐 FEED"], "p": "WAS ERSCHAFFEN?", "b": "STARTEN", "a": "KÜNSTLER", "m": "STIL WÄHLEN:", "dur": "DAUER (SEK):", "v_label": "STIMME (MELODIE):", "live": "NEUESTE", "remix": "REMIX", "theme": "FARBTHEMA:", "warn": "⚠️ WARNUNG: Lange Dauer!", "ly_instr": "Schreib auf Deutsch."},
    "Français": {"t": ["🪄 MAGIE", "🎬 RÉGIE", "🎧 MUSIQUE", "📚 ARCHIVE", "🌐 FEED"], "p": "QUE CRÉER?", "b": "LANCER", "a": "ARTISTE", "m": "CHOISIR STYLE:", "dur": "DURÉE (SEC):", "v_label": "VOIX (MÉLODIE):", "live": "RÉCENT", "remix": "REMIXER", "theme": "THÈME:", "warn": "⚠️ ATTENTION: Temps long!", "ly_instr": "Écris en français."},
    "Español": {"t": ["🪄 MAGIA", "🎬 CINE", "🎧 MÚSICA", "📚 ARCHIVE", "🌐 FEED"], "p": "¿QUÉ CREAR?", "b": "INICIAR", "a": "ARTISTA", "m": "ESTILO:", "dur": "DURACIÓN (SEG):", "v_label": "VOZ (MELODÍA):", "live": "RECIENTE", "remix": "REMIX", "theme": "TEMA:", "warn": "⚠️ ADVERTENCIA: ¡Tiempo largo!", "ly_instr": "Escribe en español."},
    "Italiano": {"t": ["🪄 MAGIA", "🎬 REGIA", "🎧 MUSICA", "📚 ARCHIVE", "🌐 FEED"], "p": "COSA CREARE?", "b": "AVVIA", "a": "ARTISTA", "m": "STILE:", "dur": "DURATA (SEC):", "v_label": "VOCE (MELODIA):", "live": "RECENTI", "remix": "REMIX", "theme": "TEMA:", "warn": "⚠️ ATTENZIONE: Tempo lungo!", "ly_instr": "Scrivi in italiano."}
}

# --- 3. DESIGN ---
st.markdown(f"""
    <style>
    .stApp, [data-testid="stSidebar"] {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    [data-testid="stSidebar"] .stMarkdown h3, [data-testid="stSidebar"] label p {{ color: {main_color} !important; font-weight: 900 !important; font-size: 14px !important; }}
    div[data-baseweb="tab-list"] {{ background-color: rgba(255, 255, 255, 0.05) !important; padding: 5px !important; border-radius: 12px !important; }}
    button[data-baseweb="tab"] div p {{ color: #FFFFFF !important; font-weight: 900 !important; font-size: 16px !important; }}
    button[aria-selected="true"] div p {{ color: {main_color} !important; text-shadow: 0 0 10px {main_color}; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.85); padding: 25px; border-radius: 20px; border: 1px solid {main_color}66; text-align: center; margin-bottom: 20px; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: 50px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .stButton>button {{ background: {main_color}1a; color: {main_color}; border: 1px solid {main_color}; border-radius: 10px; font-weight: bold; }}
    .stButton>button:hover {{ background: {main_color}; color: #000; box-shadow: 0px 0px 25px {main_color}; }}
    .live-preview-box {{ border: 1px solid {main_color}; border-radius: 10px; padding: 5px; margin-bottom: 10px; background: {main_color}1a; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY ---
with st.sidebar:
    st.markdown(f"""<div style="border: 1px solid {main_color}; padding: 10px; border-radius: 10px; text-align: center;"><p style="color:{main_color}; font-weight:900; margin:0; font-size:12px;">MAXIMUSIKAI ENGINE ONLINE</p><p style="color:#555; font-size:9px; margin:0;">TOMAS INGVARSSON PRODUCTION</p></div>""", unsafe_allow_html=True)
    
    sel_lang = st.selectbox("LANG / SPRÅK:", list(LANG_MAP.keys()))
    L = LANG_MAP[sel_lang]
    
    chosen_theme_name = st.selectbox(L["theme"], list(theme_options.keys()))
    if theme_options[chosen_theme_name] != st.session_state.theme_color:
        st.session_state.theme_color = theme_options[chosen_theme_name]
        st.rerun()

    with st.expander(L["a"]): artist_name = st.text_input("", "ANONYM")
    
    st.divider()
    # RULLMENY FÖR STIL/MOOD
    mood = st.selectbox(L["m"], [
        "Cyberpunk 2077", "Retro VHS 80s", "Lo-fi Dreams", "Dark Techno", 
        "Cinematic Epic", "Synthwave Neon", "Deep Space", "Urban Drill", 
        "Psych Rock", "Minimalist Zen", "Horror Gothic", "Vaporwave"
    ])
    
    st.divider()
    music_duration = st.slider(L["dur"], 10, 240, 10, step=10)
    if music_duration > 60: st.error(L["warn"])
    
    if st.session_state.gallery:
        st.divider()
        st.markdown(f"### ⚡ {L['live']}")
        for item in list(reversed(st.session_state.gallery))[:2]:
            st.markdown(f'<div class="live-preview-box">', unsafe_allow_html=True)
            st.video(item['video'])
            st.markdown('</div>', unsafe_allow_html=True)
    st.caption("MAXIMUSIKAI v2.9.7")

st.markdown(f"""<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p><p style="color:{main_color}; letter-spacing: 4px; font-size: 12px; margin-top: -5px; opacity: 0.8;">{sel_lang.upper()} PRO STUDIO</p></div>""", unsafe_allow_html=True)

# --- 5. HUVUDAPPEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(L["t"])

    with tab1: # MAGI
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area(L["p"], value=st.session_state.remix_prompt if st.session_state.remix_prompt else f"A {mood} scene")
            if st.button(L["b"]):
                with st.status("BUILDING...") as status:
                    try:
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music", "duration": music_duration})
                            ly_f = exe.submit(replicate.run, "meta/llama-2-70b-chat", input={"prompt": f"{L['ly_instr']} Write 2 short rhyming lines about {m_ide}. No intro."})
                            img_url, mu_url, lyrics = str(img_f.result()), str(mu_f.result()), "".join(ly_f.result()).replace('"', '')
                        vid_url = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": img_url})
                        entry = {"id": time.time(), "name": m_ide[:15], "video": str(vid_url), "audio": mu_url, "lyrics": lyrics, "time": datetime.datetime.now().strftime("%H:%M"), "full_prompt": m_ide}
                        st.session_state.gallery.append(entry); save_data(st.session_state.gallery)
                        st.session_state.remix_prompt = ""; st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    with tab2: # REGI
        up_file = st.file_uploader("UPLOAD IMAGE:", type=["jpg", "png", "jpeg"])
        if up_file and st.button("ANIMATE"):
            with st.status("..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up_file})
                st.video(str(res))

    with tab3: # MUSIK
        voice_file = st.file_uploader(L["v_label"], type=["mp3", "wav", "m4a"])
        mu_ide = st.text_input("PROMPT:", f"{mood} beat")
        if st.button("GENERATE"):
            with st.status("..."):
                p = {"prompt": mu_ide, "duration": music_duration}
                if voice_file: p["input_audio"] = voice_file
                st.audio(str(replicate.run("facebookresearch/musicgen", input=p)))

    with tab4: # ARKIV
        if st.button("ZIP EXPORT"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf: zf.writestr("history.json", json.dumps(st.session_state.gallery))
            st.download_button("DOWNLOAD", data=buf.getvalue(), file_name="maximusikai_pro.zip")
        for item in reversed(st.session_state.gallery):
            with st.expander(f"📁 {item['name']} ({item['time']})"):
                st.video(item['video']); st.audio(item['audio'])
                c_rem, c_del = st.columns(2)
                with c_rem:
                    if st.button(f"🔄 {L['remix']}", key=f"rem_{item['id']}"):
                        st.session_state.remix_prompt = item.get('full_prompt', item['name']); st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        st.session_state.gallery = [x for x in st.session_state.gallery if x['id'] != item['id']]
                        save_data(st.session_state.gallery); st.rerun()

    with tab5: # FEED
        if st.button("SHARE LATEST"):
            if st.session_state.gallery: st.session_state.community_feed.append(st.session_state.gallery[-1])
        for post in reversed(st.session_state.community_feed):
            st.divider(); st.video(post['video']); st.caption(f"Artist: {artist_name}")

else: st.error("REPLICATE_API_TOKEN MISSING")
st.markdown("<center><p style='color:#333; font-size:10px;'>MAXIMUSIKAI SPEED PRO // 2026 // T.I.</p></center>", unsafe_allow_html=True)














