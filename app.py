import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI GALAXY", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State Init
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "wallpaper" not in st.session_state: 
    st.session_state.wallpaper = "https://images.unsplash.com"
if "accent_color" not in st.session_state:
    st.session_state.accent_color = "#00f2ff"
if "bg_gallery" not in st.session_state:
    st.session_state.bg_gallery = [st.session_state.wallpaper]

# --- 2. DESIGN (CSS) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important;
            background-position: center !important;
            transition: 1.5s ease-in-out !important;
        }}
        .main, .stAppHeader, .stAppViewBlockContainer {{ background: transparent !important; }}

        /* MEGA KNAPPAR 200PX */
        div[data-testid="stButton"] > button {{
            display: flex !important; align-items: center !important; justify-content: center !important;
            margin: 0 auto !important; width: 200px !important; height: 200px !important;
            border-radius: 50px !important; border: 2px solid {accent}44 !important;
            background: rgba(0,0,0,0.3) !important; backdrop-filter: blur(10px) !important;
            font-size: 8rem !important; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.8) !important;
        }}
        
        div[data-testid="stButton"] > button:hover {{
            transform: scale(1.1) translateY(-10px) !important;
            border-color: {accent} !important;
            box-shadow: 0 0 70px {accent}66 !important;
        }}

        .space-title {{
            text-align: center; color: white; font-size: 6rem; font-weight: 900; 
            letter-spacing: -3px; margin-top: 50px; text-shadow: 0 0 30px {accent}88;
        }}
        .label {{ 
            text-align: center; color: {accent}; font-family: monospace; 
            font-weight: bold; margin-top: 25px; letter-spacing: 5px; 
            font-size: 1rem; text-transform: uppercase;
        }}

        .window {{
            background: rgba(0, 5, 15, 0.96) !important;
            backdrop-filter: blur(50px); border: 1px solid {accent}44;
            border-radius: 40px; padding: 50px; color: white;
        }}
        
        /* Galleri-bilder */
        .gallery-img {{
            border-radius: 15px; border: 2px solid {accent}22;
            cursor: pointer; transition: 0.3s;
        }}
        .gallery-img:hover {{ transform: scale(1.05); border-color: {accent}; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<h1 class='space-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, c5, _ = st.columns([0.1, 1, 1, 1, 1, 1, 0.1])
    
    with c1:
        if st.button("🌌", key="s"): st.session_state.active_window = "SYNTHESIS"; st.rerun()
        st.markdown('<p class="label">Synth</p>', unsafe_allow_html=True)
    with c2:
        if st.button("👽", key="a"): st.session_state.active_window = "AUDIO"; st.rerun()
        st.markdown('<p class="label">Audio</p>', unsafe_allow_html=True)
    with c3:
        if st.button("🛸", key="v"): st.session_state.active_window = "VIDEO"; st.rerun()
        st.markdown('<p class="label">Video</p>', unsafe_allow_html=True)
    with c4:
        if st.button("🖼️", key="wp"): st.session_state.active_window = "BG_ENGINE"; st.rerun()
        st.markdown('<p class="label">BG Engine</p>', unsafe_allow_html=True)
    with c5:
        if st.button("☄️", key="sys"): st.session_state.active_window = "SYSTEM"; st.rerun()
        st.markdown('<p class="label">System</p>', unsafe_allow_html=True)

# --- 4. WINDOW MANAGER ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; font-size:3rem; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown(f"<hr style='border:1px solid {st.session_state.accent_color}44; margin:30px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "BG_ENGINE":
            st.write("### 🚀 GENERERA NY VÄRLD")
            bg_prompt = st.text_area("BESKRIV MILJÖN:", placeholder="Deep sea bioluminescent forest...")
            theme_color = st.color_picker("VÄLJ TEMA-FÄRG:", st.session_state.accent_color)

            if st.button("RENDERA OCH SPARA", use_container_width=True):
                with st.status("SYNTETISERAR..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": bg_prompt, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res
                    st.session_state.accent_color = theme_color
                    st.session_state.bg_gallery.append(res)
                st.rerun()
            
            st.markdown("---")
            st.write("### 🎞️ GALLERI (KLICKA FÖR ATT BYTA)")
            cols = st.columns(4)
            for i, img_url in enumerate(reversed(st.session_state.bg_gallery)):
                with cols[i % 4]:
                    if st.button(f"VAL {i}", key=f"gal_{i}", use_container_width=True):
                        st.session_state.wallpaper = img_url
                        st.rerun()
                    st.image(img_url, use_container_width=True)

        elif st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("COMMAND:")
            if st.button("EXECUTE", use_container_width=True):
                with st.status("WORKING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res, use_container_width=True)

        elif st.session_state.active_window == "SYSTEM":
            st.write(f"GALLERY_SIZE: {len(st.session_state.bg_gallery)} ITEMS")
            if st.button("RESET ALL"):
                st.session_state.bg_gallery = [st.session_state.bg_gallery[0]]
                st.session_state.wallpaper = st.session_state.bg_gallery[0]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


















