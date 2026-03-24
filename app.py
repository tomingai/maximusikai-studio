import streamlit as st
import replicate
import os
import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from st_supabase_connection import SupabaseConnection

# --- 1. SETUP & DATABAS (SUPABASE) ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Initiera Supabase-anslutning
# Kräver [connections.supabase] url och key i .streamlit/secrets.toml
conn = st.connection("supabase", type=SupabaseConnection)

def get_user_db(artist):
    res = conn.table("users").select("*").eq("artist", artist).execute()
    return res.data[0] if res.data else None

def update_user_db(user_data):
    conn.table("users").upsert(user_data).execute()

def get_full_gallery():
    res = conn.table("gallery").select("*").order("created_at", desc=True).execute()
    return res.data if res.data else []

def add_to_gallery(entry):
    conn.table("gallery").insert(entry).execute()

# --- 2. THEME & DESIGN ---
if "theme_color" not in st.session_state: st.session_state.theme_color = "#bf00ff"
if "remix_prompt" not in st.session_state: st.session_state.remix_prompt = ""

main_color = st.session_state.theme_color
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #050505 0%, #0b001a 100%) !important; color: white !important; }}
    [data-testid="stSidebar"] {{ background: #0a0a0a !important; border-right: 1px solid {main_color}33; }}
    .neon-container {{ background: rgba(10, 10, 10, 0.9); padding: 25px; border-radius: 20px; border: 1px solid {main_color}44; text-align: center; margin-bottom: 25px; }}
    .neon-title {{ font-family: 'Arial Black', sans-serif; font-size: clamp(30px, 5vw, 60px); font-weight: 900; color: #fff; text-shadow: 0 0 15px {main_color}; margin: 0; }}
    .stButton>button {{ background: transparent; color: {main_color}; border: 1px solid {main_color}; width: 100%; border-radius: 8px; transition: 0.3s; font-weight: bold; }}
    .stButton>button:hover {{ background: {main_color}; color: #000; box-shadow: 0 0 20px {main_color}; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDOMENY ---
with st.sidebar:
    st.markdown(f'<p style="color:{main_color}; font-weight:900; letter-spacing:2px; font-size:20px;">MAXIMUSIKAI</p>', unsafe_allow_html=True)
    artist_name = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    # Hämta eller skapa användare i Supabase
    current_user = get_user_db(artist_name)
    if not current_user:
        current_user = {"artist": artist_name, "is_pro": False, "credits": 3}
        update_user_db(current_user)

    is_admin = (artist_name == "TOMAS2026")
    status_txt = "PREMIUM ACCESS 💎" if current_user["is_pro"] else f"POWER: {current_user['credits']} units ⚡"
    st.markdown(f'<div style="font-size:12px; color:{main_color}; padding:10px; border:1px solid {main_color}33; border-radius:5px;">{status_txt}</div>', unsafe_allow_html=True)
    
    if not current_user["is_pro"]:
        with st.expander("⚡ UPGRADE"):
            st.markdown(f'[ACTIVATE PRO SUBSCRIPTION](https://buy.stripe.com)')
            master_key = st.text_input("USE MASTER KEY:", type="password")
            if st.button("UNLOCK"):
                if master_key == "PRO2026": 
                    current_user["is_pro"] = True
                    update_user_db(current_user)
                    st.success("PRO AKTIVERAT!")
                    st.rerun()

    st.divider()
    mood = st.selectbox("MOOD:", ["Cyberpunk", "Retro VHS", "Lo-fi", "Dark Techno", "Epic Cinematic", "Vaporwave"])
    music_duration = st.slider("LENGTH (SEC):", 5, 30 if current_user["is_pro"] else 10, 8)
    st.caption(f"v5.0.0-DB // BY T. INGVARSSON")

# --- 4. HUVUDAPPEN ---
st.markdown(f'<div class="neon-container"><p class="neon-title">MAXIMUSIKAI STUDIO</p></div>', unsafe_allow_html=True)

# Kontrollera API-nyckel
replicate_token = st.secrets.get("REPLICATE_API_TOKEN") or os.environ.get("REPLICATE_API_TOKEN")

if replicate_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_token
    
    tab_labels = ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"]
    if is_admin: tab_labels.append("⚙️ ADMIN")
    tabs = st.tabs(tab_labels)

    with tabs[0]: # --- MAGI (ASYNKRON) ---
        c1, c2 = st.columns([1, 1.2])
        with c1:
            m_ide = st.text_area("VAD SKALL VI SKAPA?", value=st.session_state.remix_prompt, placeholder="En futuristisk stad i regn...")
            if st.button("STARTA GENERERING"):
                if current_user["credits"] > 0 or current_user["is_pro"]:
                    with st.status("MAGI PÅGÅR... ✨") as status:
                        try:
                            # Dra av credits om inte Pro
                            if not current_user["is_pro"]: 
                                current_user["credits"] -= 1
                                update_user_db(current_user)
                            
                            with ThreadPoolExecutor() as executor:
                                img_task = executor.submit(replicate.run, "black-forest-labs/flux-schnell", input={"prompt": f"{m_ide}, {mood} style"})
                                mu_task = executor.submit(replicate.run, "facebookresearch/musicgen", input={"prompt": f"{mood} music, {m_ide}", "duration": music_duration})
                                
                                img_res = img_task.result()
                                mu_res = mu_task.result()

                            img_url = img_res[0] if isinstance(img_res, list) else img_res
                            
                            new_entry = {
                                "artist": artist_name,
                                "name": m_ide[:30] if m_ide else "Untitled",
                                "video": str(img_url),
                                "audio": str(mu_res)
                            }
                            
                            add_to_gallery(new_entry)
                            status.update(label="KLART!", state="complete")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fel: {e}")
                else:
                    st.warning("Credits slut! Uppgradera till PRO.")

    with tabs[1]: # --- REGISSÖREN ---
        up_file = st.file_uploader("ANIMERA BILD:", type=["jpg", "png", "jpeg"])
        if up_file and st.button("KÖR LUMA DREAM"):
            with st.spinner("Animerar..."):
                # Obs: Kräver ofta publik URL, fungerar bäst med Replicate upload API
                res = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Slow cinematic motion", "image_url": up_file})
                st.video(str(res))

    with tabs[2]: # --- MUSIK ---
        mu_p = st.text_input("BESKRIV BEATET:", f"{mood} vibes")
        if st.button("SKAPA LJUD"):
            with st.spinner("Komponerar..."):
                mu_res = replicate.run("facebookresearch/musicgen", input={"prompt": mu_p, "duration": 15})
                st.audio(str(mu_res))

    with tabs[3]: # --- ARKIV ---
        all_data = get_full_gallery()
        my_files = [p for p in all_data if p["artist"] == artist_name or is_admin]
        if not my_files: st.write("Inga filer hittades.")
        for item in my_files:
            with st.expander(f"📁 {item['name'].upper()}"):
                st.image(item['video'])
                if item.get('audio'): st.audio(item['audio'])
                if st.button("REMIX", key=f"rem_{item['id']}"):
                    st.session_state.remix_prompt = item['name']
                    st.rerun()

    with tabs[4]: # --- FEED ---
        feed_data = get_full_gallery()[:10]
        for item in feed_data:
            c1, c2 = st.columns([1, 2])
            with c1: st.image(item['video'])
            with c2:
                st.write(f"**Artist:** {item['artist']}")
                if item.get('audio'): st.audio(item['audio'])
            st.divider()

    if is_admin:
        with tabs[5]:
            st.subheader("ADMIN DASHBOARD")
            users = conn.table("users").select("*").execute().data
            st.dataframe(pd.DataFrame(users))
            if st.button("RADERA ALLA ANVÄNDARE (FARLIGT)"):
                conn.table("users").delete().neq("artist", "ADMIN").execute()

else:
    st.error("REPLICATE_API_TOKEN saknas i Secrets.")













