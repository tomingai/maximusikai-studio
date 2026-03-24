import streamlit as st
import replicate
import os
import datetime
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP & MINNE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Initiera minnet (eftersom vi kör utan Supabase nu)
if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

# --- 2. DESIGN ---
main_color = "#bf00ff"
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 25px; border-radius: 20px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 25px; }}
    .neon-title {{ font-family: 'Arial Black'; font-size: 50px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; border-radius: 8px; font-weight: bold; width: 100%; transition: 0.3s; }}
    .stButton>button:hover {{ background: {main_color}; color: black; box-shadow: 0 0 20px {main_color}; }}
    .share-btn {{ background: {main_color}22; border: 1px solid {main_color}; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; font-size: 11px; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown(f'<h2 style="color:{main_color};">MAXIMUSIKAI</h2>', unsafe_allow_html=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    # Hantera användare i minnet
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = {"credits": 3, "is_pro": False}
    
    current_user = st.session_state.user_db[artist_id]
    is_admin = (artist_id == "TOMAS2026")
    
    status_txt = "💎 PREMIUM" if (current_user["is_pro"] or is_admin) else f"⚡ {current_user['credits']} UNITS"
    st.info(f"STATUS: {status_txt}")
    
    mood = st.selectbox("MOOD:", ["Cyberpunk", "Retro VHS", "Dark Techno", "Epic Cinematic"])
    st.caption("v6.5 // LOCAL STABLE 🥐")

# --- 4. HUVUDAPPEN ---
st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

# Hämta API-nyckel
token = st.secrets.get("REPLICATE_API_TOKEN")

if not token:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i Secrets!")
else:
    os.environ["REPLICATE_API_TOKEN"] = token
    
    # ALLA DINA FLIKAR ÄR TILLBAKA HÄR:
    tab_labels = ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"]
    if is_admin: tab_labels.append("⚙️ ADMIN")
    tabs = st.tabs(tab_labels)

    with tabs[0]: # --- 🪄 MAGI ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt)
            if st.button("STARTA GENERERING"):
                if current_user["credits"] > 0 or current_user["is_pro"] or is_admin:
                    with st.status("MAGI PÅGÅR..."):
                        if not (current_user["is_pro"] or is_admin): current_user["credits"] -= 1
                        
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music for {m_ide}", "duration": 8})
                            img_res, mu_res = img_f.result(), mu_f.result()

                        img_url = img_res if isinstance(img_res, list) else img_res
                        entry = {"id": datetime.datetime.now().timestamp(), "artist": artist_id, "name": m_ide[:20], "video": str(img_url), "audio": str(mu_res)}
                        st.session_state.gallery.append(entry)
                        st.rerun()

    with tabs[1]: # --- 🎬 REGI ---
        st.subheader("ANIMERA BILDER")
        up_file = st.file_uploader("Ladda upp bild:", type=["jpg", "png"])
        if up_file and st.button("KÖR LUMA DREAM MACHINE"):
            with st.spinner("Animerar..."):
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic slow motion", "image_url": up_file})
                st.video(str(res))

    with tabs[2]: # --- 🎧 MUSIK ---
        mu_p = st.text_input("BESKRIV BEATET:", f"{mood} vibes")
        if st.button("SKAPA LJUD"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 15})
                st.audio(str(mu_res))

    with tabs[3]: # --- 📚 ARKIV ---
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_files: st.write("Ditt arkiv är tomt.")
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])
                if st.button("REMIX", key=f"rem_{item['id']}"):
                    st.session_state.remix_prompt = item['name']; st.rerun()

    with tabs[4]: # --- 🌐 FEED ---
        for item in reversed(st.session_state.gallery[-10:]):
            c1, c2 = st.columns([1, 1.5])
            with c1: st.image(item['video'])
            with c2: 
                st.write(f"**{item['name']}** - Artist: {item['artist']}")
                if item.get('audio'): st.audio(item['audio'])
            st.divider()

    if is_admin:
        with tabs[5]: # --- ⚙️ ADMIN ---
            st.subheader("SYSTEM STATUS")
            st.write(f"Användare i session: {len(st.session_state.user_db)}")
            st.write(f"Bilder i session: {len(st.session_state.gallery)}")
            if st.button("RENSA ALLT"): 
                st.session_state.gallery = []; st.rerun()















