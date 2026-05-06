import streamlit as st
import fitz  # This is the PyMuPDF library
import edge_tts
import asyncio
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Shruti Reader",
    layout="wide"
)

# --- SANSKRIT PRONUNCIATION DICTIONARY ---
def apply_pronunciation_rules(text):
    rules = {
        "ā": "aa",
        "ī": "ee",
        "ū": "oo",
        "ṛ": "ri",
        "ṝ": "ree",
        "ḷ": "lri",
        "ṅ": "ng",
        "ñ": "ny",
        "ṭ": "t",
        "ḍ": "d",
        "ṇ": "n",
        "ś": "sh",
        "ṣ": "sh",
        "ṃ": "m",
        "ḥ": "h",
        "krṣṇa": "krishna",
        "Caitanya": "Chaitanya",
        "Dr": "Doctor"
    }
    for key, value in rules.items():
        text = text.replace(key, value)
        text = text.replace(key.upper(), value.capitalize())
    return text

# --- AUDIO GENERATION ENGINE ---
async def generate_audio(text, voice="en-IN-NeerjaNeural"):
    processed_text = apply_pronunciation_rules(text)
    communicate = edge_tts.Communicate(processed_text, voice)
    await communicate.save("output.mp3")

# --- SESSION STATE (MEMORY) ---
if "pdf_pages" not in st.session_state:
    st.session_state.pdf_pages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

# --- MAIN UI ---
st.title("Shruti Reader")
st.write("Welcome to Shruti Reader. Upload your PDF below to extract the true text.")

st.divider()

# --- DOCUMENT UPLOADER ---
st.subheader("1. Document Upload")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Process Book"):
        with st.spinner("Extracting text with high-fidelity engine..."):
            # 1. Read the file into memory
            pdf_bytes = uploaded_file.read()
            
            # 2. Open it with our new PyMuPDF engine
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            # 3. Extract text
            extracted_pages = []
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    extracted_pages.append(text)
                else:
                    extracted_pages.append("[No text found on this page. It might be an image or scan.]")
            
            st.session_state.pdf_pages = extracted_pages
            st.session_state.current_page = 0
            st.success(f"Successfully extracted {total_pages} pages!")

# --- DOCUMENT READER & AUDIO PLAYER ---
if st.session_state.pdf_pages:
    st.divider()
    st.subheader("2. Reader")
    
    current_idx = st.session_state.current_page
    page_text = st.session_state.pdf_pages[current_idx]
    
    # --- AUDIO CONTROLS ---
    st.write("**Audio Settings**")
    col_voice, col_play, col_empty = st.columns([2, 2, 6])
    
    with col_voice:
        voice_choice = st.selectbox("Select Voice:", [
            "en-IN-NeerjaNeural (Female, India)", 
            "en-IN-PrabhatNeural (Male, India)", 
            "en-US-AriaNeural (Female, US)", 
            "en-US-GuyNeural (Male, US)",
            "en-GB-SoniaNeural (Female, UK)",
            "en-GB-RyanNeural (Male, UK)"
        ])
        voice_id = voice_choice.split(" ")[0]

    with col_play:
        st.write("") 
        st.write("")
        if st.button("Play Current Page"):
            with st.spinner("Generating natural speech..."):
                asyncio.run(generate_audio(page_text, voice_id))
                st.audio("output.mp3", format="audio/mp3")
                
    st.divider()
    
    st.write(f"**Page {current_idx + 1} of {len(st.session_state.pdf_pages)}**")
    
    # --- NAVIGATION BUTTONS ---
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("Previous Page"):
            if current_idx > 0:
                st.session_state.current_page -= 1
                st.rerun()
    with col2:
        if st.button("Next Page"):
            if current_idx < len(st.session_state.pdf_pages) - 1:
                st.session_state.current_page += 1
                st.rerun()

    # --- TEXT DISPLAY ---
    st.markdown(page_text)
