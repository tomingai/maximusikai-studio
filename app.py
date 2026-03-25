import streamlit as st
import replicate
import os
import time

# --- 1. GRUNDINSTÄLLNINGAR ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "app_bg" not in st.session_state: st.session_state.app_bg = None

# --- 2. DYNAMISK DESIGN (FIXAD FÖR BILD-URL) ---
bg_img = st.session_state.app_bg
if bg_img:
    # Här säkerställer vi att URL:en är ren och fungerar i CSS
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("{bg_img}");
            background-size: cover; 
            background-position: center;
            background-attachment: fixed;
        }}
        /* Gör texten extra tydlig mot bakgrunden */
        label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; 
            text-shadow: 1px 1px 3px black !important;
            font-weight: bold !important;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #050505 !important; }</style>", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.title("MAXIMUSIKAI ⚡")
    artist_id = st.text_input("ARTIST ID:", "ANONYM").upper()
    
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = 10
    
    st.info(f"UNITS: ⚡ {st.session_state.user_db[artist_id]}")
    
    st.divider()
    st.subheader("VÄLJ ATMOSFÄR:")
    
    # Tre snabbknappar för bakgrund
    col1, col2, col3 = st.columns(3)
    
    atm_prompts = {
        "Space": "Deep space nebula, cinematic stars, 4k, dark background",
        "Forest": "Mystic green forest, sunlight through trees, 4k",
        "Stad": "Cyberpunk city night, neon rain, futuristic, 4k"
    }

    if col1.button("🌌 SPACE"):
        with st.spinner("Skapar rymden..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": atm_prompts["Space"]})
            # FIX: Plocka ut första URL:en ur listan
            st.session_state.app_bg = res[0] if isinstance(res, list) else str(res)
            st.rerun()

    if col2.button("🌲 FOREST"):
        with st.spinner("Skapar skogen..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": atm_prompts["Forest"]})
            st.session_state.app_bg = res[0] if isinstance(res, list) else str(res)
            st.rerun()

    if col3.button("🌆 STAD"):
        with st.spinner("Skapar staden..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": atm_prompts["Stad"]})
            st.session_state.app_bg = res[0] if isinstance(res, list) else str(res)
            st.rerun()

    if st.button("❌ ÅTERSTÄLL"):
        st.session_state.app_bg = None
        st.rerun()

# --- 4. HUVUDAPP ---
st.markdown('<h1 style="text-align:center; color:white;">STUDIO PRO 2026</h1>', unsafe_allow_html=True)

tabs = st.tabs(["🪄 MAGI", "📚 ARKIV"])

with tabs[0]: # MAGI
    prompt = st.text_area("VAD SKALL VI SKAPA?")
    if st.button("STARTA GENERERING"):
        if st.session_state.user_db[artist_id] > 0:
            with st.status("AI:n arbetar..."):
                try:
                    out = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    img_url = out[0] if isinstance(out, list) else str(out)
                    
                    st.session_state.gallery.append({
                        "artist": artist_id,
                        "url": img_url,
                        "name": prompt[:20]
                    })
                    st.session_state.user_db[artist_id] -= 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Fel: {e}")
        else:
            st.warning("Units slut!")

with tabs[1]: # ARKIV
    my_pics = [p for p in st.session_state.gallery if p["artist"] == artist_id]
    if not my_pics:
        st.write("Ditt arkiv är tomt.")
    for i, p in enumerate(reversed(my_pics)):
        st.image(p["url"], caption=p["name"])
        if st.button("ANVÄND SOM BAKGRUND", key=f"bg_btn_{i}"):
            st.session_state.app_bg = p["url"]
            st.rerun()
        st.divider()
























