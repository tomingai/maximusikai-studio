import streamlit as st
import replicate
import os
import datetime
import pandas as pd
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from st_supabase_connection import SupabaseConnection

# --- 1. GRUNDLÄGGANDE KONFIGURATION ---
st.set_page_config(
    page_title="MAXIMUSIKAI STUDIO PRO 2026", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kontrollera att Secrets finns (Viktigt för Streamlit Cloud)
if "connections" not in st.secrets or "supabase" not in st.secrets["connections"]:
    st.error("❌ SUPABASE-INSTÄLLNINGAR SAKNAS! Lägg till URL och KEY i Streamlit Secrets.")
    st.stop()

# Anslut till Supabase
conn = st.connection("supabase", type=SupabaseConnection)

# --- 2. DATABAS-FUNKTIONER ---
def get_user(artist_id):
    res = conn.table("users").select("*").eq("artist", artist_id).execute()
    return res.data[0] if res.data else None

def update_user(user_data):
    conn.table("users").upsert(user_data).execute()

def get_gallery():
    res = conn.table("gallery").select("*").order("id", desc=True).limit(30).execute()
    return res.data if res.data else []

def save_to_gallery(entry):
    conn.table("gallery").insert(entry).execute()

# --- 3. UI-DESIGN (CYBERPUNK THEME) ---
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

main_color = st.session_state.theme_color
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    [data-testid="stSidebar"] {{ background: #0a0a0a !important; border-right: 1px solid {main_color}33; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 25px; border-radius: 20px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 25px; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: clamp(30px, 5vw, 60px); font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .share-btn {{ background: {main_color}15; border: 1px solid {main_color}66; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 11px; font-weight: bold; margin-right: 8px; transition: 0.3s; }}
    .share-btn:hover {{ background: {main_color}; color: black; box-shadow: 0 0 15px {main_color}; }}
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; width: 100%; border-radius: 8px; font-weight: bold; }}
    .stButton>button:hover {{ background: {main_color}; color: black; box-shadow: 0 0 20px {main_color}; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDOMENY (ANVÄNDARE & KONTO) ---
with st.sidebar:
    st.markdown(f'<p style="color:{main_color}; font-weight:900; letter-spacing:2px; font-size:22px; margin-bottom:0;">MAXIMUSIKAI</p>', unsafe_allow_html=True)
    st.caption("AI MULTIMEDIA STUDIO v5.5")
    
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    # Hämta användardata
    user = get_user(artist_id)
    if not user:
        user = {"artist": artist_id, "is_pro": False, "credits": 3}
        update_user(user)

    is_admin = (artist_id == "TOMAS2026")
    status_icon = "💎" if user["is_pro"] else "⚡"
    st.markdown(f"""
        <div style="padding:15px; border:1px solid {main_color}44; border-radius:10px; margin: 10px 0;">
            <small style="color:#888;">STATUS</small><br>
            <b style="color:{main_color};">{status_icon} {"PREMIUM" if user["is_pro"] else f"POWER: {user['credits']} UNITS"}</b>
        </div>
    """, unsafe_allow_html=True)

    if not user["is_pro"]:
        with st.expander("🚀 UPGRADE TO PRO"):
            st.write("Få obegränsade credits och video-generering.")
            st.markdown(f"[**ACTIVATE VIA STRIPE**](https://buy.stripe.com)")
            if st.button("LÅS UPP MED NYCKEL"):
                pwd = st.text_input("KEY:", type="password")
                if pwd == "PRO2026":
                    user["is_pro"] = True
                    update_user(user)
                    st.success("PRO AKTIVERAT!")
                    st.rerun()

    st.divider()
    mood = st.selectbox("VISUAL STYLE:", ["Cyberpunk Neon", "Retro VHS 80s", "Dark Cinematic", "Lo-fi Aesthetic", "Surreal Dream"])
    st.caption("© 2026 T. INGVARSSON")

# --- 5. HJÄLPFUNKTIONER ---
def share_component(item_name, item_url):
    """Skapar delningsknappar för varje objekt."""
    text = f"Kolla in min AI-konst: '{item_name}' skapad i MAXIMUSIKAI! ⚡"
    tweet = f"https://twitter.com{urllib.parse.quote(text)}&url={urllib.parse.quote(item_url)}"
    wa = f"https://wa.me{urllib.parse.quote(text + ' ' + item_url)}"
    
    st.markdown(f"""
        <div style="margin: 10px 0;">
            <a class="share-btn" href="{tweet}" target="_blank">𝕏 SHARE</a>
            <a class="share-btn" href="{wa}" target="_blank">💬 WHATSAPP</a>
        </div>
    """, unsafe_allow_html=True)

# --- 6. HUVUDAPPLIKATION ---
st.markdown(f'<div class="neon-container"><p class="neon-title">MAXIMUSIKAI STUDIO</p></div>', unsafe_allow_html=True)

# API-Check
api_key = st.secrets.get("REPLICATE_API_TOKEN") or os.environ.get("REPLICATE_API_TOKEN")

if api_key:
    os.environ["REPLICATE_API_TOKEN"] = api_key
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"])

    # --- FLIK: MAGI (BILD + MUSIK) ---
    with tabs[0]:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            prompt = st.text_area("VAD VILL DU SKAPA?", value=st.session_state.remix_prompt, height=120, placeholder="En futuristisk krigare i en neonstad...")
            if st.button("SKAPA MULTIMEDIA"):
                if user["credits"] > 0 or user["is_pro"]:
                    with st.status("AI GENERERAR... ✨") as status:
                        try:
                            # Minska credits
                            if not user["is_pro"]:
                                user["credits"] -= 1
                                update_user(user)
                            
                            # Kör bild och musik parallellt
                            # Vattenstämpel läggs till i prompten för att synas på bilden
                            watermark_prompt = f"{prompt}, {mood}, cinematic lighting, high quality. Watermark: 'Created with MAXIMUSIKAI' in small text bottom corner."
                            
                            with ThreadPoolExecutor() as executor:
                                img_future = executor.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": watermark_prompt})
                                mu_future = executor.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music for {prompt}", "duration": 8})
                                
                                img_res = img_future.result()
                                mu_res = mu_future.result()

                            img_url = img_res[0] if isinstance(img_res, list) else img_res
                            
                            # Spara till Supabase
                            save_to_gallery({
                                "artist": artist_id,
                                "name": prompt[:30] if prompt else "Untitled",
                                "video": str(img_url),
                                "audio": str(mu_res)
                            })
                            
                            status.update(label="KLART!", state="complete")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ett fel uppstod: {e}")
                else:
                    st.warning("Dina POWER UNITS är slut! Uppgradera till PRO.")

    # --- FLIK: REGI (VIDEO) ---
    with tabs[1]:
        st.subheader("ANIMERA BILDER")
        if not user["is_pro"]:
            st.warning("🎬 Video-animering kräver PRO-medlemskap.")
        else:
            up_file = st.file_uploader("Ladda upp bild för att skapa 5s video:", type=["jpg", "png", "jpeg"])
            if up_file and st.button("STARTA ANIMERING"):
                with st.spinner("Animerar med Luma Dream Machine..."):
                    video_res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic motion", "image_url": up_file})
                    st.video(str(video_res))

    # --- FLIK: MUSIK (ENDAST LJUD) ---
    with tabs[2]:
        st.subheader("AI LJUDSTUDIO")
        mu_prompt = st.text_input("Beskriv beatet:", placeholder="Aggressive dark techno beat 128bpm")
        if st.button("GENERERA BEAT"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_prompt, "duration": 15})
                st.audio(str(mu_res))

    # --- FLIK: ARKIV (DINA SKAPELSER) ---
    with tabs[3]:
        all_data = get_gallery()
        my_files = [p for p in all_data if p["artist"] == artist_id or is_admin]
        if not my_files:
            st.info("Ditt arkiv är tomt. Börja skapa i MAGI-fliken!")
        
        for item in my_files:
            with st.expander(f"📁 {item['name'].upper()}"):
                col_i, col_m = st.columns([1, 1])
                with col_i: st.image(item['video'])
                with col_m:
                    if item.get('audio'): st.audio(item['audio'])
                    share_component(item['name'], item['video'])
                    if st.button("REMIX IDÉ", key=f"remix_{item['id']}"):
                        st.session_state.remix_prompt = item['name']
                        st.rerun()

    # --- FLIK: FEED (COMMUNITY) ---
    with tabs[4]:
        st.subheader("GLOBAL FEED 🌐")
        feed = get_gallery()
        for item in feed:
            f_col1, f_col2 = st.columns([1, 1.5])
            with f_col1:
                st.image(item['video'])
            with f_col2:
                st.write(f"**{item['name']}**")
                st.caption(f"Artist: {item['artist']}")
                if item.get('audio'): st.audio(item['audio'])
                share_component(item['name'], item['video'])
            st.divider()

    # --- FLIK: ADMIN (ENDAST TOMAS) ---
    if is_admin:
        with tabs[5]:
            st.subheader("STUDIO KONTROLLPANEL")
            users_list = conn.table("users").select("*").execute().data
            st.dataframe(pd.DataFrame(users_list))
            if st.button("EXPORT DATA"):
                st.write(get_gallery())

else:
    st.error("⚠️ REPLICATE_API_TOKEN saknas i systemet.")













