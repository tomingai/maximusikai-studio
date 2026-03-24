import streamlit as st
import replicate
import os
import datetime
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO 2026", page_icon="⚡", layout="wide")

# Vi skapar en lokal "databas" i minnet som nollställs vid omstart
if "gallery" not in st.session_state:
    st.session_state.gallery = []
if "remix_prompt" not in st.session_state:
    st.session_state.remix_prompt = ""
if "user_credits" not in st.session_state:
    st.session_state.user_credits = 3

# --- 2. DESIGN (CYBERPUNK) ---
main_color = "#bf00ff"
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 20px; border-radius: 15px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 20px; }}
    .neon-title {{ font-family: 'Arial Black'; font-size: 45px; font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .share-btn {{ background: {main_color}22; border: 1px solid {main_color}; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; font-size: 11px; margin-right: 5px; }}
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; border-radius: 8px; font-weight: bold; width: 100%; }}
    .stButton>button:hover {{ background: {main_color}; color: black; box-shadow: 0 0 20px {main_color}; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown(f'<h2 style="color:{main_color};">MAXIMUSIKAI</h2>', unsafe_allow_html=True)
    artist_id = st.text_input("DITT ARTIST-ID:", "ANONYM").strip().upper()
    
    is_pro = (artist_id == "TOMAS2026")
    status = "💎 PRO" if is_pro else f"⚡ {st.session_state.user_credits} CREDITS"
    st.info(f"STATUS: {status}")
    
    mood = st.selectbox("STIL:", ["Cyberpunk", "80s Retro", "Dark Techno", "Cinematic"])
    st.caption("v6.1 // LOCAL EDITION 🥐")

# --- 4. FUNKTIONER ---
def share_ui(name, url):
    text = f"Kolla min AI-konst: {name} #MAXIMUSIKAI"
    tweet = f"https://twitter.com{urllib.parse.quote(text)}&url={urllib.parse.quote(url)}"
    st.markdown(f'<a class="share-btn" href="{tweet}" target="_blank">𝕏 DELA PÅ X</a>', unsafe_allow_html=True)

# --- 5. HUVUDAPP ---
st.markdown('<div class="neon-container"><p class="neon-title">MAXIMUSIKAI</p></div>', unsafe_allow_html=True)

# Hämta token från Secrets
replicate_token = st.secrets.get("REPLICATE_API_TOKEN")

if replicate_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_token
    tabs = st.tabs(["🪄 SKAPA", "📚 DITT ARKIV", "🌐 FEED (LOCAL)"])

    with tabs[0]: # SKAPA
        col1, col2 = st.columns([1, 1.2])
        with col1:
            prompt = st.text_area("VAD SKALL VI BYGGA?", value=st.session_state.remix_prompt, placeholder="En rymdstation i neon...")
            if st.button("STARTA MAGIN"):
                if st.session_state.user_credits > 0 or is_pro:
                    with st.status("AI:N BAKAR DIN IDÉ... 🥐"):
                        if not is_pro:
                            st.session_state.user_credits -= 1
                        
                        # Kör bild och musik parallellt
                        with ThreadPoolExecutor() as exe:
                            img_f = exe.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{prompt}, {mood} style"})
                            mu_f = exe.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music för {prompt}", "duration": 8})
                            
                            img_res = img_f.result()
                            mu_res = mu_f.result()

                        # Spara till galleriet (endast i minnet)
                        img_url = img_res if isinstance(img_res, list) else img_res
                        entry = {
                            "id": datetime.datetime.now().timestamp(),
                            "artist": artist_id,
                            "name": prompt[:20] if prompt else "Untitled",
                            "video": str(img_url),
                            "audio": str(mu_res)
                        }
                        st.session_state.gallery.append(entry)
                        st.rerun()
                else:
                    st.warning("Dina credits är slut! Logga in som ADMIN för att köra obegränsat.")

    with tabs[1]: # DITT ARKIV
        my_files = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if not my_files:
            st.info("Här hamnar det du skapar!")
        for item in reversed(my_files):
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])
                share_ui(item['name'], item['video'])

    with tabs[2]: # FEED
        if not st.session_state.gallery:
            st.write("Ingen har skapat något än i denna session.")
        for item in reversed(st.session_state.gallery):
            c1, c2 = st.columns([1, 1.5])
            with c1: st.image(item['video'])
            with c2:
                st.write(f"**{item['name']}** - *{item['artist']}*")
                if item.get('audio'): st.audio(item['audio'])
                share_ui(item['name'], item['video'])
            st.divider()
else:
    st.error("Lägg till 'REPLICATE_API_TOKEN' i dina Secrets på Streamlit Cloud för att starta!")














