import streamlit as st
import PyPDF2
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Shruti Reader",
    layout="wide"
)

# --- SESSION STATE (MEMORY) ---
# Streamlit refreshes the script every time you click a button.
# "Session State" is our way of forcing it to remember our book and current page!
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
# This creates a drag-and-drop file uploader that only accepts PDFs
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # A button to confirm we want to process the file
    if st.button("Process Book"):
        with st.spinner("Extracting text... This might take a moment for large books."):
            # 1. Open the PDF file
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            total_pages = len(pdf_reader.pages)
            
            # 2. Extract text page by page
            extracted_pages = []
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Check if the page actually has text (to filter out pure image scans)
                if text:
                    extracted_pages.append(text)
                else:
                    extracted_pages.append("[No text found on this page. It might be an image or scan.]")
            
            # 3. Save the extracted text to our memory
            st.session_state.pdf_pages = extracted_pages
            st.session_state.current_page = 0
            
            # Show a success message!
            st.success(f"Successfully extracted {total_pages} pages!")

# --- DOCUMENT READER ---
# Only show the reader if we have pages saved in our memory
if st.session_state.pdf_pages:
    st.divider()
    st.subheader("2. Reader")
    
    # Get the current page number
    current_idx = st.session_state.current_page
    
    # Display page counter
    st.write(f"**Page {current_idx + 1} of {len(st.session_state.pdf_pages)}**")
    
    # --- NAVIGATION BUTTONS ---
    # We create three columns so our buttons sit neatly side-by-side
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("Previous Page"):
            if current_idx > 0:
                st.session_state.current_page -= 1
                st.rerun() # Force the page to refresh immediately
                
    with col2:
        if st.button("Next Page"):
            if current_idx < len(st.session_state.pdf_pages) - 1:
                st.session_state.current_page += 1
                st.rerun()

    # --- TEXT DISPLAY ---
    # st.markdown displays the text naturally and supports native browser zooming
    st.markdown(st.session_state.pdf_pages[current_idx])
