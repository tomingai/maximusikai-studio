import streamlit as st
import replicate
import os
import json
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.1.5"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. URL-SANITIZER & MOTOR (Regel 21 & 12) ---
def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        # Moondream returnerar text, inte URL
        if "moondream" in model: return res
        return sanitize_url(res)
    except Exception as e:
        st.error(f"Neural Error: {str(e)[:50]}")
        return None

# --- 3. INITIALISERING (Återställer alla trimmare) ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "hd_mode": True, "enhance_lvl": 0.7, "analysis": ""
    })

# --- 4. UI ENGINE (Full HD Gloss) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 20, 0.9); backdrop-filter: blur(50px); border: 1px solid {accent}44; border-radius: 25px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; color: white !important; background: {accent}22 !important; border-radius: 12px; height: 3.5rem; transition: 0.3s; width: 100%; font-weight: bold; }}
    .stButton>button:hover {{ background: {accent}44 !important; box-shadow: 0 0 20px {accent}77; transform: translateY(-2px); }}
    .locked-btn button {{ opacity: 0.1 !important; cursor: not-allowed !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION (SYNTH, ARKIV, ENGINE UNLOCKED) ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
nav_cols = st.columns(7)
nav_config = [
    ("🏠", "HOME", True), ("🪄", "SYNTH", False), ("🎧", "AUDIO", True), 
    ("🎬", "MOVIE", True), ("📚", "ARKIV", False), ("🖼", "ENGINE", False), ("⚙️", "SYSTEM", True)
]
for i, (icon, target, is_locked) in enumerate(nav_config):
    if is_locked:
        nav_cols[i].markdown('<div class="locked-btn">', unsafe_allow_html=True)
        nav_cols[i].button(icon, key=f"nav_l_{i}")
        nav_cols[i].markdown('</div>', unsafe_allow_html=True)
    else:
        if nav_cols[i].button(icon, key=f"nav_a_{target}"):
            st.session_state.page = target; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# --- SYNTH (ÅTERSTÄLLD TILL FULL PRECISION) ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:3px;'>🪄 ULTRA-HD SYNTH STATION</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.7, 0.3])
    user_p = c1.text_input("VISION PROMPT (SV/EN):", placeholder="Beskriv din vision...")
    st.session_state.style = c2.selectbox("STIL:", ["Photorealistic", "Cinematic 8K", "Cyberpunk", "Macro Photography", "Digital Art"])

    st.markdown("---")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.session_state.hd_mode = st.toggle("ACTIVATE ULTRA-HD", value=st.session_state.hd_mode)
    with t2:
        st.session_state.enhance_lvl = st.slider("AI KREATIVITET (LLM)", 0.0, 1.0, st.session_state.enhance_lvl)
    with t3:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "21:9"], index=1)

    if st.button("🚀 EXEKVERA NEURAL HD-SYNTES", use_container_width=True):
        if user_p:
            with st.status("Neural process...") as status:
                final_p = user_p
                if st.session_state.hd_mode or st.session_state.enhance_lvl > 0.1:
                    status.update(label="Llama-3 optimerar visionen...")
                    instr = f"Act as a professional cinematographer. Expand this to a {st.session_state.style} 8k prompt. Focus on sharp textures and cinematic light. Creativity {st.session_state.enhance_lvl}: {user_p}"
                    res_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": instr, "max_new_tokens": 250})
                    final_p = "".join(list(res_llm))
                
                status.update(label="FLUX renderar pixlar...")
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x")})
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
        else: st.error("Skriv in en vision.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, caption=f"Senaste resultat | {st.session_state.style}")
        if st.button("🖼 ANVÄND SOM BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ENGINE (ANALYS) ---
elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ENGINE [ANALYS]</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=450)
        if st.button("🔍 KÖR NEURAL INSPEKTION"):
            with st.status("Analyserar texturer...") as status:
                res = safe_replicate_run("lucataco/moondream2", {
                    "image": st.session_state.last_img, 
                    "prompt": "Describe the lighting, materials, and technical quality in detail. Is it 8K quality?"
                })
                st.session_state.analysis = res
                status.update(label="Analys klar!", state="complete")
        if st.session_state.analysis:
            st.info(st.session_state.analysis)
    else: st.warning("Skapa en bild i SYNTH först.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ARKIV ---
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 DITT ARKIV")
    if not st.session_state.library:
        st.info("Arkivet är tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("SET WALLPAPER", key=f"ark_w_{i}"):
                    st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)





































































