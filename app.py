import os
import streamlit as st
from db import init_db

# Page Configuration
st.set_page_config(
    page_title="VAN MAHOTSAV 2026 - Jammu",
    page_icon="🌳",
    layout="wide"
)

# Load External CSS File
def load_css(file_name="styles.css"):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

# Initialize Database Table
# init_db()

# Navigation setup using st.navigation and st.Page
page_1 = st.Page("pages/registration.py", title="Registration Form", icon="📝", default=True)
page_3 = st.Page("pages/gallery.py", title="Media Gallery", icon="🖼️")
page_2 = st.Page("pages/certificate_download.py", title="Download Certificate", icon="📜")

pg = st.navigation([page_1, page_2, page_3], position="top", expanded=True)

# Header Title
st.title("DISTRICT ADMINISTRATION JAMMU - VAN MAHOTSAV 2026")

pg.run()
    