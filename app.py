def apply_space_ui():
    st.markdown("""
        <style>
        /* RYMDBAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        .main, .stAppHeader, .stAppViewBlockContainer {
            background: transparent !important;
        }

        /* STÖRRE OCH BILD-BASERADE IKONER */
        .desktop-icon {
            background-size: cover;
            background-position: center;
            border: 2px solid rgba(0, 242, 255, 0.2);
            border-radius: 25px;
            height: 180px; /* Större höjd */
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            padding-bottom: 15px;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            position: relative;
            overflow: hidden;
        }
        
        .desktop-icon:hover {
            border-color: #00f2ff;
            transform: scale(1.1);
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.4);
        }

        .icon-label {
            background: rgba(0, 0, 0, 0.7);
            width: 100%;
            text-align: center;
            padding: 5px 0;
            color: #00f2ff;
            font-family: monospace;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:4rem;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tre kolumner för de stora ikonerna
    _, i1, i2, i3, _ = st.columns([0.5, 1, 1, 1, 0.5])
    
    with i1:
        # SKOG för Synthesis
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">SYNTHESIS</div>
            </div>''', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with i2:
        # BERG för Audio
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">AUDIO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with i3:
        # TEMATISK BILD för Video (t.ex. norrsken/stjärnhimmel)
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">VIDEO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("V", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()





