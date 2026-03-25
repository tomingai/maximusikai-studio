import streamlit as st
import replicate
import os
import time

# --- 1. SETUP & SESSION STATE (FÖRSTÖR EJ DESSA) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Initiera alla variabler om de inte finns
for key, default in {
    "gallery": [],
    "user_db": {},
    "app_bg": None,
    "agreed": False,
    "lang": "Svenska"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- 2. DESIGN-MOTORN (HÅLLER ALLT PÅ PLATS) ---
def apply_design():
    if st.session_state.app_bg:
        bg_url = st.session_state.app_bg
        if isinstance(bg_url, list): bg_url = bg_url[0]
        
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
            /* Transparenta rutor utan grått */
            div[data-baseweb="base-input"], div[data-baseweb="textarea"] {{ background-color: transparent !important; }}
            .stTextArea textarea, .stTextInput input {{ 
                background-color: rgba(255,255,255,0.1) !important; 
                color: white !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                backdrop-filter: blur(15px);
            }}
            /* Text-synlighet */
            label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
                color: white !important; 
                text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; 
            }}
            .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(0,0,0,0.3) !important; border-radius: 10px; }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

apply_design()

# --- 3. SPRÅK & LOGIK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tabs": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SÄTT SOM BAKGRUND"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tabs": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED", "⚙️ ADMIN"],
        "units": "UNITS", "status": "STATUS", "set_bg": "🖼 SET AS BACKGROUND"
    }
}
L = texts[st.session_state.lang]

# --- 4. SIDOMENY ---
with st.sidebar:
    st.title("STUDIO")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English"], horizontal=True)
    
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    
    is_admin = (artist_id == "TOMAS2026")
    u_creds = st.session_state.user_db[artist_id]
    
    st.info(f"{L['status']}: {'💎 ADMIN' if is_admin else f'⚡ {u_creds} {L['units']}'}")
    
    if st.button("❌ NOLLSTÄLL DESIGN"):
        st.session_state.app_bg = None
        st.rerun()

# --- 5. HUVUDSTUDION ---
st.markdown(f'<h1 style="text-align:center;">{L["title"]}</h1>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# API-Token
token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    
    # Skapa fasta flikar
    tab_objs = st.tabs(L["tabs"] if is_admin else L["tabs"][:-1])

    # FLIK 1: MAGI
    with tab_objs[0]:
        prompt = st.text_area("VAD SKALL VI SKAPA?", key="p_in")
        if st.button("STARTA GENERERING"):
            if u_creds > 0 or is_admin:
                with st.status("AI arbetar..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    mu = replicate.run("facebookresearch/musicgen", input={"prompt": prompt, "duration": 5})
                    
                    url = img[0] if isinstance(img, list) else str(img)
                    
                    # Sätt bakgrund ENDAST om den är tom (LÅS)
                    if st.session_state.app_bg is None:
                        st.session_state.app_bg = url
                        
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt[:15], "url": url, "audio": str(mu)})
                    st.rerun()

    # FLIK 2: REGI
    with tab_objs[1]:
        st.subheader("BILD TILL VIDEO")
        if st.file_uploader("Ladda upp:", type=["jpg", "png"]):
            if st.button("ANIMERA"):
                st.info("Kör Luma...")

    # FLIK 3: MUSIK
    with tab_objs[2]:
        m_prompt = st.text_input("Beskriv beatet:")
        if st.button("SKAPA"):
            res = replicate.run("facebookresearch/musicgen", input={"prompt": m_prompt, "duration": 10})
            st.audio(str(res))

    # FLIK 4: ARKIV
    with tab_objs[3]:
        my = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        for p in reversed(my):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(p["url"])
                if st.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = p["url"]
                    st.rerun()

    # FLIK 5: FEED
    with tab_objs[4]:
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            st.divider()

    # FLIK 6: ADMIN (Endast Tomas)
    if is_admin:
        with tab_objs[5]:
            st.write(st.session_state.user_db)
            if st.button("RENSA"): 
                st.session_state.gallery = []
                st.rerun()
else:
    st.error("API TOKEN SAKNAS")




























