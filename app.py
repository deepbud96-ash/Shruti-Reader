import streamlit as st

# --- PAGE CONFIGURATION ---
# This tells the browser the name of the tab and sets the layout.
st.set_page_config(
    page_title="Shruti Reader",
    layout="wide"
)

# --- MAIN UI ---
# st.title creates the main header on the page.
st.title("Shruti Reader")

# st.write prints standard text to the screen.
st.write("Welcome to Shruti Reader. The system infrastructure is successfully deployed and running.")

# A simple divider line to make it look professional
st.divider()

# A placeholder for where our uploader will go in Step 2
st.subheader("Document Upload")
st.write("PDF upload functionality will be added in the next step.")
