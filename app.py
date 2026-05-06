import streamlit as st
import fitz  # PyMuPDF
import edge_tts
import asyncio
import os
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Shruti Reader",
    layout="wide"
)

# --- PDF FONT DECRYPTOR ---
def fix_pdf_encoding(text):
    font_fixes = {
        # Original Balaram Font Fixes
        "ä": "ā", "Ä": "Ā",
        "é": "ī", "É": "Ī",
        "ü": "ū", "Ü": "Ū",
        "å": "ṛ", "Å": "Ṛ",
        "ñ": "ṣ", "Ñ": "Ṣ",
        "ë": "ṇ", "Ë": "Ṇ",
        "ö": "ṭ", "Ö": "Ṭ",
        "ò": "ḍ", "Ò": "Ḍ",
        "ç": "ś", "Ç": "Ś",
        "ì": "ṅ", "Ì": "Ṅ",
        "ï": "ñ", "Ï": "Ñ",
        "à": "ṁ", "À": "Ṁ",
        "ù": "ḥ", "Ù": "Ḥ",
        "Kåñëa": "Kṛṣṇa",
        "Rädhäräëé": "Rādhārāṇī",
        "Çréla": "Śrīla",
        "Prabhupäda": "Prabhupāda",
        
        # Sanskrit-Times / Tamal Font Fixes
        "ƒ": "ā",
        "Š": "ñ",
        "‡": "ṭ",
        "‚": "ṛ",
        "‰": "ṣ",
        "†": "ṇ",
        "’": "Ṛ",
        "™": "Ṣ",
        "–": "Ṇ",
        "Œ": "i",
        "K’™–A": "KṚṢṆA",
        "K‚‰†a": "Kṛṣṇa",
        "Rƒja": "Rāja",
        "JŠƒna": "Jñānā",
        "Ha‡ha": "Haṭha",
        "Kriyƒ": "Kriyā",
        "Rƒma": "Rāma",
        "s.tra": "sutra",
        "Satsvar.pa": "Satsvaroopa",
        "Rājas.ya": "Rājasūya",
        "pa7u": "paśu",
        "Ð": "-",
        "Śa...kara": "Śaṅkara",
        "
        
        # NEW: BBT Krsna Book Specific Fixes
        "": "0", "": "1", "": "2", "": "3", "": "4", 
        "": "5", "": "6", "": "7", "": "8", "": "9",
        "“": "Ā",
        "œ": "Ī",
        "Œ": "ī",
        ",,": "ṁ",
        "ˆ": "ḍ",
        "^": "ḍ",
        "": "Ś", 
        "Ã": "-",
        "Gau^ade3a": "Gauḍadeśa",
        "Krsna": "Krishna"
    }
    
    for old_char, new_char in font_fixes.items():
        text = text.replace(old_char, new_char)
    return text

# --- SANSKRIT PRONUNCIATION DICTIONARY ---
def apply_pronunciation_rules(text):
    text = re.sub(r'\bca\b', 'cha', text)
    text = re.sub(r'\bCa\b', 'Cha', text)
    text = re.sub(r'\bhare\b', 'harray', text, flags=re.IGNORECASE)

    rules = {
        "jñānā": "gnaanaa",
        "jñāna": "gnaana",
        "haṭha": "hatha",
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
        "ṁ": "m",
        "kṛṣṇa": "krishna",
        "caitanya": "chaitanya",
        "dr": "doctor"
    }
    
    for key, value in rules.items():
        text = text.replace(key, value)
        text = text.replace(key.capitalize(), value.capitalize())
        text = text.replace(key.upper(), value.upper())
        
    text = re.sub(r'\b([A-Za-z]*[^aA\W])a\b', r'\1aa', text)
    return text

# --- AUDIO GENERATION ENGINE ---
async def generate_audio(text, voice="en-IN-NeerjaNeural", rate="+0%"):
    processed_text = apply_pronunciation_rules(text)
    communicate = edge_tts.Communicate(processed_text, voice, rate=rate)
    await communicate.save("output.mp3")

# --- SESSION STATE & SMART URL MEMORY ---
if "pdf_pages" not in st.session_state:
    st.session_state.pdf_pages = []

if "current_page" not in st.session_state:
    if "page" in st.query_params:
        st.session_state.current_page = int(st.query_params["page"])
    else:
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
        with st.spinner("Extracting and decrypting multi-font ancient texts..."):
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            extracted_pages = []
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                raw_text = page.get_text()
                fixed_text = fix_pdf_encoding(raw_text)
                
                if fixed_text.strip():
                    extracted_pages.append(fixed_text)
                else:
                    extracted_pages.append("[No text found on this page. It might be an image or scan.]")
            
            st.session_state.pdf_pages = extracted_pages
            
            if st.session_state.current_page >= total_pages:
                st.session_state.current_page = 0
                
            st.success(f"Successfully extracted and decrypted {total_pages} pages!")

# --- DOCUMENT READER & AUDIO PLAYER ---
if st.session_state.pdf_pages:
    st.divider()
    st.subheader("2. Reader")
    
    current_idx = st.session_state.current_page
    page_text = st.session_state.pdf_pages[current_idx]
    
    # --- AUDIO CONTROLS ---
    st.write("**Audio Settings**")
    
    col_voice, col_speed, col_play = st.columns([3, 3, 4])
    
    with col_voice:
        voice_choice = st.selectbox("Select Voice:", [
            "en-IN-NeerjaNeural (Female, India)", 
            "en-IN-PrabhatNeural (Male, India)",
            "en-US-AriaNeural (Female, US)", 
            "en-US-GuyNeural (Male, US)",
            "en-US-ChristopherNeural (Male, US)",
            "en-US-EricNeural (Male, US)",
            "en-US-MichelleNeural (Female, US)",
            "en-US-RogerNeural (Male, US)",
            "en-GB-SoniaNeural (Female, UK)",
            "en-GB-RyanNeural (Male, UK)",
            "en-GB-LibbyNeural (Female, UK)",
            "en-GB-MaisieNeural (Female, UK)",
            "en-GB-ThomasNeural (Male, UK)",
            "en-AU-NatashaNeural (Female, Australia)",
            "en-AU-WilliamNeural (Male, Australia)",
            "en-CA-ClaraNeural (Female, Canada)",
            "en-CA-LiamNeural (Male, Canada)",
            "en-IE-ConnorNeural (Male, Ireland)",
            "en-IE-EmilyNeural (Female, Ireland)",
            "en-NZ-MitchellNeural (Male, New Zealand)",
            "en-NZ-MollyNeural (Female, New Zealand)",
            "en-ZA-LukeNeural (Male, South Africa)",
            "en-ZA-LeahNeural (Female, South Africa)",
            "en-NG-AbeoNeural (Male, Nigeria)",
            "en-NG-EzinneNeural (Female, Nigeria)",
            "en-PH-JamesNeural (Male, Philippines)",
            "en-PH-RosaNeural (Female, Philippines)",
            "en-SG-LunaNeural (Female, Singapore)",
            "en-SG-WayneNeural (Male, Singapore)"
        ])
        voice_id = voice_choice.split(" ")[0]

    with col_speed:
        speed_val = st.slider("Reading Speed:", min_value=-50, max_value=50, value=0, step=5, format="%d%%")
        speed_str = f"+{speed_val}%" if speed_val >= 0 else f"{speed_val}%"

    with col_play:
        st.write("") 
        st.write("")
        if st.button("Play Current Page"):
            with st.spinner("Generating natural speech..."):
                asyncio.run(generate_audio(page_text, voice_id, speed_str))
                st.audio("output.mp3", format="audio/mp3")
                
    st.divider()
    
    st.write(f"**Page {current_idx + 1} of {len(st.session_state.pdf_pages)}**")
    
    # --- NAVIGATION BUTTONS ---
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("Previous Page"):
            if current_idx > 0:
                st.session_state.current_page -= 1
                st.query_params["page"] = str(st.session_state.current_page)
                st.rerun()
    with col2:
        if st.button("Next Page"):
            if current_idx < len(st.session_state.pdf_pages) - 1:
                st.session_state.current_page += 1
                st.query_params["page"] = str(st.session_state.current_page)
                st.rerun()

    # --- TEXT DISPLAY ---
    st.markdown(page_text)
