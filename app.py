import streamlit as st
import replicate
import os
import time

# --- 1. SETUP & SESSION STATE (SÄKERHETSLAGER) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Initiera variabler så de inte nollställs vid kodändring
if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. DESIGN-MOTORN (HÅLLER ALLT PÅ PLATS) ---
def apply_design():
    if st.session_state.app_bg:
        bg_url = st.session_state.app_bg
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
            /* GENOMSKINLIGA RUTOR UTAN GRÅTT */
            div[data-baseweb="base-input"], div[data-baseweb="textarea"] {{ background-color: transparent !important; }}
            .stTextArea textarea, .stTextInput input {{ 
                background-color: rgba(255,255,255,0.08) !important; 
                color: white !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                backdrop-filter: blur(15px);
            }}
            /* TEXT-SYNLIGHET */
            label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
                color: white !important; 
                text-shadow: 2px 2px 8px rgba(0,0,0,1) !important; 
                font-weight: 800 !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(0,0,0,0.3) !important; border-radius: 10px; }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

apply_design()

# --- 3. SPRÅK-ORDBOK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
        "status": "STATUS", "units": "UNITS", "set_bg": "🖼 SÄTT SOM BAKGRUND"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "🌐 FEED", "⚙️ ADMIN"],
        "status": "STATUS", "units": "UNITS", "set_bg": "🖼 SET AS BACKGROUND"
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
    
    # Fixad f-string för att undvika unmatched bracket error
    u_unit_label = L["units"]
    status_display = "💎 ADMIN" if is_admin else f"⚡ {u_creds} {u_unit_label}"
    st.info(f"{L['status']}: {status_display}")
    
    if st.button("❌ NOLLSTÄLL DESIGN"):
        st.session_state.app_bg = None
        st.rerun()

# --- 5. HUVUDAPP ---
st.markdown(f'<h1 style="text-align:center;">{L["title"]}</h1>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION"): 
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    
    # Skapa flikar (Admin ser alla 6, användare ser 5)
    tab_list = L["tab_names"] if is_admin else L["tab_names"][:-1]
    tabs = st.tabs(tab_list)

    with tabs[0]: # MAGI
        prompt = st.text_area("VAD SKALL VI SKAPA?", key="main_p", placeholder="Beskriv din vision...")
        if st.button("STARTA GENERERING", use_container_width=True):
            if u_creds > 0 or is_admin:
                with st.status("AI arbetar..."):
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    
                    # Generera Bild & Musik
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    img_url = img_res[0] if isinstance(img_res, list) else str(img_res)
                    mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": prompt, "duration": 8})
                    
                    # Lås bakgrunden om den är tom
                    if st.session_state.app_bg is None:
                        st.session_state.app_bg = img_url
                    
                    st.session_state.gallery.append({
                        "id": time.time(), "artist": artist_id, "name": prompt[:20], 
                        "url": img_url, "audio": str(mu_res)
                    })
                    st.rerun()

    with tabs[1]: # REGI
        st.subheader("BILD TILL VIDEO")
        up_img = st.file_uploader("Ladda upp bild:", type=["jpg", "png"], key="reg_up")
        if up_img and st.button("ANIMERA"):
            st.info("Luma Dream Machine arbetar... (Detta kräver en hostad URL)")

    with tabs[2]: # MUSIK
        mu_in = st.text_input("Beskriv beatet:", key="mu_input")
        if st.button("SKAPA LJUD"):
            with st.spinner("Komponerar..."):
                res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_in, "duration": 10})
                st.audio(str(res))

    with tabs[3]: # ARKIV
        my_creations = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_creations: st.info("Här var det tomt!")
        for p in reversed(my_creations):
            with st.expander(f"📁 {p['name'].upper()}"):
                st.image(p["url"])
                if st.button(L["set_bg"], key=f"set_{p['id']}"):
                    st.session_state.app_bg = p["url"]
                    st.rerun()

    with tabs[4]: # FEED
        for p in reversed(st.session_state.gallery[-10:]):
            st.image(p["url"], caption=f"Artist: {p['artist']}")
            if p["audio"]: st.audio(p["audio"])
            st.divider()

    if is_admin:
        with tabs[5]: # ADMIN
            st.write("Användardatabas:", st.session_state.user_db)
            if st.button("RENSA ALLT"): 
                st.session_state.gallery = []
                st.rerun()
else:
    st.error("API TOKEN SAKNAS I SECRETS")




























