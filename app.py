import json

# --- 1. DATABASE ENGINE (PLACERA ÖVERST I FILEN) ---
DB_PATH = "maximus_vault.json"

def load_database():
    """Laddar historik från disk till session_state."""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_event(f"DB_LOAD_ERROR: {e}")
            return []
    return []

def save_to_database(entry):
    """Sparar ett nytt asset permanent."""
    db = load_database()
    # Lägg till metadata för sökbarhet
    entry["id"] = f"HEX_{datetime.now().strftime('%y%m%d%H%M%S')}"
    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.append(entry)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)
    st.session_state.vault = db  # Uppdatera UI direkt

# Initiera databasen vid boot
if "vault" not in st.session_state or not st.session_state.vault:
    st.session_state.vault = load_database()

# --- 2. UPPDATERAD SYNTHESIS-LOGIK (Spara automatiskt) ---
# Hitta din "EXECUTE"-knapp i tab_gen och uppdatera sparningen:
if st.button("EXECUTE"):
    with st.status("ENGINE_SYNC..."):
        # ... din befintliga replicate-kod ...
        res = replicate.run(model, input={"prompt": prompt, "aspect_ratio": ratio})
        
        # SKAPA DATA-ENTRY
        new_asset = {
            "type": "GENERATION",
            "url": res[0] if isinstance(res, list) else res,
            "prompt": prompt,
            "engine": engine,
            "ratio": ratio
        }
        save_to_database(new_asset) # <--- HÄR SKER MAGIN
        st.rerun()

# --- 3. UPPDATERAD VAULT-FLIK (Med Sök & Filter) ---
with tab_vault:
    st.markdown("### `ARCHIVE_EXPLORER`")
    
    # SÖK-GRÄNSSNITT (Ökar kodmängden och nyttan)
    v_col1, v_col2 = st.columns([3, 1])
    search_query = v_col1.text_input("SEARCH_VAULT_PROMPTS", placeholder="Keywords...", label_visibility="collapsed")
    filter_type = v_col2.selectbox("FILTER", ["ALL", "GENERATIONS", "ANALYSES"])

    # FILTRERINGSLOGIK
    filtered_vault = [
        item for item in st.session_state.vault 
        if search_query.lower() in item.get("prompt", "").lower()
    ]

    if not filtered_vault:
        st.info("NO_RECORDS_FOUND_IN_LOCAL_BUFFER")
    else:
        # GRID-SYSTEM (4 kolumner)
        cols = st.columns(4)
        for idx, item in enumerate(reversed(filtered_vault)):
            with cols[idx % 4]:
                st.image(item["url"], use_container_width=True)
                with st.expander(f"ID: {item['id']}"):
                    st.code(item["prompt"], language="text")
                    st.caption(f"📅 {item['timestamp']}")
                    if st.button("LOAD_TO_STUDIO", key=f"load_{item['id']}"):
                        st.session_state.last_res = item["url"]
                        st.rerun()

# --- 4. EXPORT MODUL ---
with st.sidebar:
    st.markdown("---")
    st.subheader("DATA_EXPORT")
    if st.button("EXPORT_DB_TO_JSON"):
        db_str = json.dumps(st.session_state.vault, indent=2)
        st.download_button("DOWNLOAD_MANIFEST", db_str, "maximus_export.json", "application/json")






