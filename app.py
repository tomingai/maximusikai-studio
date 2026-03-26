# --- 2. DESIGN-MOTOR (UPPGRADRAD MED LJUSKONTROLL) ---
def apply_design():
    # Vi lägger på en subtil mörk toning (0.4 istället för 0.7) för att låta bakgrunden poppa mer
    bg_style = f'''
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
        url("{st.session_state.app_bg}") !important;
    ''' if st.session_state.app_bg else 'background-color: #1a1a1a !important;'
    
    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} background-size: cover !important; background-position: center !important; background-attachment: fixed !important; }}
        /* Gör korten lite mer transparenta för att se bakgrunden bakom */
        .card {{
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        h1, h2, h3, p {{ color: white !important; text-shadow: 0px 2px 4px rgba(0,0,0,0.8); }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (MED 4 TEMAN) ---
with st.sidebar:
    st.title("⚡ STUDIO CONTROL")
    
    st.subheader("🖼 VÄLJ ATMOSFÄR")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    
    themes = {
        "CYBER 🤖": "High-tech vaporwave city, neon lights, bright purple and cyan, cinematic 4k",
        "DRÖM ☁️": "Ethereal dreamscape, bright clouds, golden hour, cinematic lighting, peaceful, 4k",
        "LYX 💎": "Clean white marble studio, minimalist gold accents, bright daylight, 4k luxury",
        "ABSTRAKT 🎨": "Bright liquid explosion of colors, white background, artistic fluid motion, 4k"
    }

    # Logik för att generera vald bakgrund
    if c1.button("CYBER 🤖"):
        with st.spinner("Laddar neon..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["CYBER 🤖"]})
            st.session_state.app_bg = get_url(res); st.rerun()
            
    if c2.button("DRÖM ☁️"):
        with st.spinner("Svävar iväg..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["DRÖM ☁️"]})
            st.session_state.app_bg = get_url(res); st.rerun()

    if c3.button("LYX 💎"):
        with st.spinner("Städar studion..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["LYX 💎"]})
            st.session_state.app_bg = get_url(res); st.rerun()

    if c4.button("ABSTRAKT 🎨"):
        with st.spinner("Blandar färger..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["ABSTRAKT 🎨"]})
            st.session_state.app_bg = get_url(res); st.rerun()

    if st.button("❌ RESET (MÖRK)", use_container_width=True):
        st.session_state.app_bg = None; st.rerun()

    with tabs[4]:
        st.subheader("⚙️ SYSTEM CONTROL")
        st.write("Användare:", st.session_state.user_db)
        if st.button("RENSA ALL DATA"):
            st.session_state.gallery = []
            st.rerun()
