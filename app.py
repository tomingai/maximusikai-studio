    # --- FLIK 5: FEED (Hela studion) ---
    with tabs[4]: 
        st.subheader("🌐 GLOBAL STUDIO FEED")
        if not st.session_state.gallery:
            st.info("Inga skapelser ännu. Bli den första!")
        else:
            for item in reversed(st.session_state.gallery[-15:]): # Visar senaste 15
                with st.container():
                    st.markdown(f"**ARTIST:** `{item['artist']}` | **NAMN:** {item['name']}")
                    st.image(item["url"], use_container_width=True)
                    if item.get("audio"):
                        st.audio(item["audio"])
                    st.divider()

    # --- FLIK 6: ADMIN (Endast för TOMAS2026) ---
    if is_admin:
        with tabs[5]:
            st.subheader("⚙️ SYSTEM CONTROL")
            c1, c2 = st.columns(2)
            with c1:
                st.write("### USER DATABASE")
                st.json(st.session_state.user_db)
            with c2:
                st.write("### SESSION STATS")
                st.write(f"Antal objekt i galleri: {len(st.session_state.gallery)}")
                if st.button("🚨 RADERA ALLT GALLERI-DATA"):
                    st.session_state.gallery = []
                    st.rerun()
                
                new_credits = st.number_input("GE UNITS TILL ANVÄNDARE:", min_value=0, value=10)
                target_user = st.text_input("ANVÄNDAR-ID:")
                if st.button("UPPDATERA CREDITS"):
                    st.session_state.user_db[target_user.upper()] = new_credits
                    st.success(f"Gav {new_credits} till {target_user}")

# --- 7. FOOTER ---
st.markdown(f'<p style="text-align:center; color:gray; font-size:10px; margin-top:50px;">© 2026 {MY_NAME} | POWERED BY REPLICATE & STREAMLIT</p>', unsafe_allow_html=True)





























