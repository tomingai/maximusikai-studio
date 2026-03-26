                if units > 0 or is_admin:
                    img_url = generate_image(prompt)
                    if img_url:
                        # Dra av en unit om inte admin
                        if not is_admin:
                            update_user(artist, "units", units - 1)
                        
                        # Spara i galleriet och sätt som bakgrund
                        add_to_gallery(artist, prompt, img_url, None)
                        st.session_state.app_bg = img_url
                        update_user(artist, "bg", img_url)
                        
                        st.image(img_url, caption="Din skapelse", use_container_width=True)
                        st.success("Bild skapad och satt som bakgrund! Ladda om sidan om den inte syns direkt.")
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("Slut på Units! Kontakta admin.")

# =========================
# TAB 2 & 3: REGI & MUSIK (Förenklad logik)
# =========================
with tabs[1]:
    st.subheader(L["director_tab"])
    v_prompt = st.text_input(L["video_instr"])
    if st.button(L["create_video"]):
        st.info("Video-generering kräver en startbild från Arkivet.")

with tabs[2]:
    st.subheader(L["music_tab"])
    m_prompt = st.text_input(L["beat_label"])
    if st.button(L["create_sound"]):
        with st.spinner("Komponerar..."):
            audio = generate_music(m_prompt)
            if audio:
                st.audio(audio)
                add_to_gallery(artist, f"Beat: {m_prompt}", st.session_state.app_bg, audio)

# =========================
# TAB 4: ARKIV (Ditt galleri)
# =========================
with tabs[3]:
    st.subheader(L["archive_tab"])
    my_items = get_user_gallery(artist)
    if not my_items:
        st.write(L["no_gallery"])
    else:
        for item in reversed(my_items):
            with st.expander(f"🎨 {item['name']}"):
                st.image(item['url'])
                if item.get("audio"):
                    st.audio(item['audio'])
                if st.button("Sätt som bakgrund", key=f"set_bg_{item['id']}"):
                    st.session_state.app_bg = item['url']
                    update_user(artist, "bg", item['url'])
                    st.rerun()

# =========================
# TAB 5: FEED (Globalt)
# =========================
with tabs[4]:
    st.subheader(L["feed_tab"])
    feed = get_global_feed()
    for item in reversed(feed[-20:]): # Visa de 20 senaste
        st.markdown(f"**Artist:** {item['artist']}")
        st.image(item['url'], width=300)
        st.divider()

# =========================
# TAB 6: ADMIN
# =========================
with tabs[5]:
    st.subheader(L["admin_panel"])
    if artist == "TOMAS2026":
        db = load_db()
        target_user = st.selectbox("Välj användare", list(db.keys()))
        new_units = st.number_input("Ge Units", 0, 1000, 20)
        if st.button("Uppdatera Units"):
            update_user(target_user, "units", new_units)
            st.success(f"{target_user} har nu {new_units} units.")
    else:
        st.warning(L["admin_only"])

  
