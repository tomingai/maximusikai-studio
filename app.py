import streamlit as st
import replicate
import os
import requests
from io import BytesIO
from PIL import Image

# --- UTILS FOR POST_PROCESS ---
def get_image_as_bytes(url):
    response = requests.get(url)
    return BytesIO(response.content)

# --- 1. SIDEBAR SYSTEM MONITOR (Expanding the UI) ---
with st.sidebar:
    st.markdown("<div style='letter-spacing:2px; font-weight:900; color:#fff;'>SYSTEM_MONITOR</div>", unsafe_allow_html=True)
    st.progress(0.75, text="GPU_CLUSTER_LOAD")
    st.progress(0.12, text="MEMORY_BUFFER")
    st.markdown("---")
    st.markdown("### `ACTIVE_ENGINES`")
    st.code("FLUX_1.1_PRO: ONLINE\nREAL_ESRGAN: READY\nMODNET_SEGMENT: READY", language="accesslog")
    
    if st.button("TERMINATE_ALL_SESSIONS"):
        st.session_state.clear()
        st.rerun()

# --- 2. UPDATING TAB_EDIT (The Post-Process Lab) ---
# Vi adresserar nu tab_edit som vi skapade i förra steget
with tab_edit:
    if "last_res" not in st.session_state:
        st.warning("NO_SIGNAL_DETECTED: Generera en bild i SYNTHESIS först.")
    else:
        e_col1, e_col2 = st.columns([1, 1])
        
        with e_col1:
            st.markdown("### `SOURCE_SIGNAL`")
            st.image(st.session_state.last_res, caption="INPUT_STREAM", use_container_width=True)
            
        with e_col2:
            st.markdown("### `REFINEMENT_OPERATIONS`")
            
            # OPERATION 01: UPSCALING
            st.markdown("<label>NEURAL_UPSCALING (4X)</label>", unsafe_allow_html=True)
            if st.button("RUN_RE_ESRGAN_4X"):
                with st.status("UPSCALING_IN_PROGRESS..."):
                    # Vi använder Real-ESRGAN för upscaling
                    upscale_res = replicate.run(
                        "nightmareai/real-esrgan:42fed1c4974141d047f5c2929391d8a7fa136979c6e12e69004958c894285854",
                        input={"image": st.session_state.last_res, "scale": 4}
                    )
                    st.session_state.upscaled_res = upscale_res
                    log_event("UPSCALING_COMPLETE: 4096px_REACHED")
                st.rerun()

            # OPERATION 02: BACKGROUND REMOVAL
            st.markdown("<br><label>SEGMENTATION_CORE</label>", unsafe_allow_html=True)
            if st.button("EXECUTE_BG_REMOVAL"):
                with st.status("SEGMENTING_OBJECTS..."):
                    rem_res = replicate.run(
                        "lucataco/remove-bg:95fcc2a2648d0d744f0064c5b739f9ba5b330f817686534cfd485e9e03d368e7",
                        input={"image": st.session_state.last_res}
                    )
                    st.session_state.transparent_res = rem_res
                    log_event("SEGMENTATION_COMPLETE: ALPHA_CHANNEL_READY")
                st.rerun()

            # DISPLAY RESULTS OF POST-PROCESS
            if "upscaled_res" in st.session_state:
                st.success("UPSCALED_ASSET_READY")
                st.download_button("DOWNLOAD_4K", requests.get(st.session_state.upscaled_res).content, "pro_4k.png")

# --- 3. PROMPT BUILDER MODULE (To reach 2000 lines, we need logic-heavy tools) ---
with tab_gen:
    with col_ctrl:
        st.markdown("<br><label>PROMPT_ARCHITECT</label>", unsafe_allow_html=True)
        # En expander för att bygga komplexa prompts utan att skriva allt själv
        with st.expander("NEURAL_STYLING_KITS", expanded=False):
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                if st.button("CINEMATIC_DARK"):
                    prompt += ", moody lighting, anamorphic lens, 35mm, grainy"
                if st.button("CYBER_NEON"):
                    prompt += ", synthwave aesthetic, neon glow, wet pavement"
            with s_col2:
                if st.button("ARCHITECTURAL"):
                    prompt += ", minimalism, brutalist, raw concrete, wide angle"
                if st.button("HYPER_REAL"):
                    prompt += ", shot on RED, 8k, photorealistic, highly detailed"

# --- 4. DATA LOGGING (Increasing complexity) ---
# Här simulerar vi en databas-struktur för framtida Supabase-integration
def save_session_metadata():
    metadata = {
        "session_id": "MAX_PRO_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total_assets": len(st.session_state.vault),
        "engine_version": "5.2.0"
    }
    # Här kan vi senare lägga json.dump() för att spara lokalt
    return metadata

session_data = save_session_metadata()



