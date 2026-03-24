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

STRIPE_LINK = "https://buy.stripe.com..." 
DB_FILE = "maximusikai_archive.json"
FEEDBACK_FILE = "maximusikai_feedback.json"
ADMIN_KEY = "TOMAS2026" # Skriv detta i Artist-namn fältet för att låsa upp Admin

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

if "gallery" not in st.session_state: st.session_state.gallery = load_data(DB_FILE)
if "community_feed" not in st.session_state: st.session_state.community_feed = []
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"
if "is_pro" not in st.session_state: st.session_state.is_pro = False

# --- 2. GLOBAL SPRÅK-ORDBOK ---
LANG_MAP = {
    "Svenska": {
        "t": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
        "p": "VAD SKALL VI SKAPA?", "b": "STARTA", "a": "ARTIST", "m": "VÄLJ STIL:", "dur": "LÄNGD (SEK):",
        "v_label": "RÖST (MELODI):", "theme": "FÄRGTEMA:", "buy_btn": "⭐ UPPGRADERA TILL PRO",
        "legal_title": "📜 VILLKOR", "help_title": "🆘 HJÄLP & FEEDBACK", "help_label": "Meddelande till Tomas:",
        "legal_text": "AI-genererat innehåll ägs av användaren. Missbruk förbjudet.",
        "pro_msg": "🔓 Endast PRO.", "send": "SKICKA"
    },
    "English": {
        "t": ["🪄 MAGIC", "🎬 DIRECT", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED", "⚙️ ADMIN"],
        "p": "WHAT TO CREATE?", "b": "START", "a": "ARTIST", "m": "SELECT STYLE:", "dur": "DURATION (SEC):",
        "v_label": "VOICE (MELODY):", "theme": "THEME COLOR:", "buy_btn": "⭐ UPGRADE TO PRO",
        "legal_title": "📜 TERMS", "help_title": "🆘 HELP & FEEDBACK", "help_label": "Message to Tomas:",
        "legal_text": "AI content is user-owned. Abuse is prohibited.",
        "pro_msg": "🔓 PRO only.", "send": "SEND"
    }
}

# --- 3. DESIGN ---
main_color = st.session_state.theme_color
st.markdown(f"""
    <style>
    .stApp, [data-testid="stSidebar"] {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    [data-testid="stSidebar"] .stMarkdown h3, [data-testid="stSidebar"] label p {{ color: {main_color} !important; font-weight: 900 !important; font-size: 14px !important; }}
    div[data-baseweb="tab-list"] {{ background-color: rgba(255, 255, 255, 0.05) !important; padding: 5px !important; border-radius: 12px !important; }}
    button[data-baseweb="tab"] div p {{ color: #FFFFFF !important; font-weight: 900 !important; font-size: 14px !important; }}
    button[aria-selected="true"] div p {{ color: {main_color} !important; text-shadow: 0 0 10px {main_color}; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.85); padding: 20px; border-radius: 20px; border: 1px solid {main_color}66; text-align: center; margin-bottom: 20px; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: 45px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .stButton>button {{ background: {main_color}1a; color: {main_color}; border: 1px solid {main_color}; border-radius: 10px; font-weight: bold; width: 100%; }}
    .stripe-btn {{ background: #635bff; color: white; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-bottom: 10px; }}
    .admin-card {{ background: rgba(255,0,0,0.1); border: 1px solid red; padding: 10px; border-radius: 10px; margin-bottom: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY ---
with st.sidebar:
    st.markdown(f"""<div style="border: 1px solid {main_color}; padding: 10px; border-radius: 10px; text-align: center;"><p style="color:{main_color}; font-weight:900; margin:0; font-size:12px;">MAXIMUSIKAI ENGINE ONLINE</p></div>""", unsafe_allow_html=True)
    
    sel_lang = st.selectbox("LANG / SPRÅK:", list(LANG_MAP.keys()))
    L = LANG_MAP[sel_lang]
    
    with st.expander(L["a"]):
        artist_name = st.text_input("", "ANONYM")
    
    if not st.session_state.is_pro:
        st.markdown(f'<a href="{STRIPE_LINK}" target="_blank" class="stripe-btn">{L["buy_btn"]}</a>', unsafe_allow_html=True)
        with st.expander("🔑 KEY"):
            if st.text_input("CODE:", type="password") == "MAXI2026": 
                st.session_state.is_pro = True
                st.rerun()

    theme_options = {"Neon Purple": "#bf00ff", "Cyber Amber": "#ffaa00", "Electric Blue": "#00f2ff", "Acid Green": "#ccff00"}
    chosen_theme = st.selectbox(L["theme"], list(theme_options.keys()))
    if theme_options[chosen_theme] != st.session_state.theme_color:
        st.session_state.theme_color = theme_options[chosen_theme]
        st.rerun()

    st.divider()
    mood = st.selectbox(L["m"], ["Cyberpunk", "Retro VHS", "Lo-fi", "Dark Techno", "Epic Cinematic", "Synthwave"])
    music_duration = st.slider(L["dur"], 10, 240 if st.session_state.is_pro else 11, 10)
    
    with st.expander(L["help_title"]):
        f_msg = st.text_area(L["help_label"])
        if st.button(L["send"]):
            feedback_list = load_data(FEEDBACK_FILE)
            feedback_list.append({"time": str(datetime.datetime.now())[:16], "user": artist_name, "msg": f_msg})
            save_data(feedback_list, FEEDBACK_FILE)
            st.success("OK!")
    
    st.caption("v3.4.0 // TOMAS INGVARSSON")

# TITEL
pro_tag = ' <span style="background:gold; color:black; padding:2px 8px; border-radius:5px; font-size:12px;">PRO</span>' if st.session_state.is_pro else ''
st.markdown(f"""<div class="neon-container"><p class="neon-title">MAXIMUSIKAI{pro_tag}</p></div>""", unsafe_allow_html=True)

# --- 5. HUVUDAPPEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    
    # ADMIN LOGIK: Visa flik 6 endast om nyckeln är skriven i Artist-fältet
    show_admin = artist_name == ADMIN_KEY
    tabs_to_show = L["t"] if show_admin else L["t"][:-1]
    tabs = st.tabs(tabs_to_show)

    with tabs[0]: # MAGI
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area(L["p"], value=st.session_state.remix_prompt if st.session_state.remix_prompt else f"A {mood} scene")
            if st.button(L["b"]):
                with st.status("BUILDING...") as status:
                    try:
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music", "duration": music_duration})
                            ly_f = exe.submit(replicate.run, "meta/llama-2-70b-chat", input={"prompt": f"{sel_lang} lyrics about {m_ide}"})
                            img_url, mu_url, lyrics = str(img_f.result()), str(mu_f.result()), "".join(ly_f.result())
                        vid_url = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic", "image_url": img_url})
                        entry = {"id": time.time(), "name": m_ide[:15], "video": str(vid_url), "audio": mu_url, "lyrics": lyrics, "time": datetime.datetime.now().strftime("%H:%M")}
                        st.session_state.gallery.append(entry); save_data(st.session_state.gallery, DB_FILE)
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    with tabs[1]: # REGI
        up_file = st.file_uploader("IMG:", type=["jpg", "png", "jpeg"])
        if up_file and st.button("ANIMATE"):
            res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Motion", "image_url": up_file})
            st.video(str(res))

    with tabs[2]: # MUSIK
        st.subheader("VOICE-TO-BEAT")
        v_file = st.file_uploader(L["v_label"], type=["mp3", "wav"], disabled=not st.session_state.is_pro)
        m_prompt = st.text_input("PROMPT:", f"{mood} beat")
        if st.button("GENERATE"):
            p = {"prompt": m_prompt, "duration": music_duration}
            if v_file: p["input_audio"] = v_file
            st.audio(str(replicate.run("facebookresearch/musicgen", input=p)))

    with tabs[3]: # ARKIV
        if st.session_state.is_pro and st.button("EXPORT ZIP"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf: zf.writestr("history.json", json.dumps(st.session_state.gallery))
            st.download_button("DL", data=buf.getvalue(), file_name="archive.zip")
        for item in reversed(st.session_state.gallery):
            with st.expander(f"📁 {item['name']}"):
                st.video(item['video']); st.audio(item['audio'])
                if st.button("DEL", key=f"d_{item['id']}"):
                    st.session_state.gallery = [x for x in st.session_state.gallery if x['id'] != item['id']]
                    save_data(st.session_state.gallery, DB_FILE); st.rerun()

    with tabs[4]: # FEED
        for post in reversed(st.session_state.community_feed):
            st.video(post['video'])

    if show_admin:
        with tabs[5]: # --- ADMIN PANEL ---
            st.subheader("🛠️ TOMAS CONTROL PANEL")
            feedbacks = load_data(FEEDBACK_FILE)
            st.write(f"**Totala arkiv-filer:** {len(st.session_state.gallery)}")
            st.write(f"**Nya meddelanden:** {len(feedbacks)}")
            
            if st.button("Rensa all feedback"):
                save_data([], FEEDBACK_FILE); st.rerun()
            
            for f in reversed(feedbacks):
                st.markdown(f"""<div class="admin-card">
                    <small>{f['time']} | Från: {f['user']}</small><br>
                    <strong>{f['msg']}</strong>
                </div>""", unsafe_allow_html=True)

else: st.error("REPLICATE_API_TOKEN MISSING")


















