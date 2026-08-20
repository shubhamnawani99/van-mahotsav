import io
import datetime
import zoneinfo
import streamlit as st
from sqlalchemy import text
from PIL import Image
from db import conn
from utils.certificate import generate_certificate

# Get current date in IST for max_value bound and default value
ist_today = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).date()

with st.form(key="van_mahotsav_form", clear_on_submit=True):
    st.markdown("### Registration & Activity Submission Form")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("1. Name*", placeholder="Enter your full name")
    with col2:
        mobile = st.text_input("2. Mobile Number*", max_chars=10, placeholder="10-digit mobile number")

    col1, col2 = st.columns(2)
    with col1:
        designation = st.text_input("3. Designation*", placeholder="e.g., Forest Officer, Teacher, Citizen")
    with col2:
        department = st.text_input("4. Department Name*", placeholder="e.g., Forest Department, Education, General Public")
    
    # 5. State & 6. District
    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("5. State*", ["Jammu & Kashmir", "Other"])
        if state == "Other":
            state = st.text_input("Specify State*")
    
    with col2:
        district = st.text_input("6. District*", value="Jammu" if state == "Jammu & Kashmir" else "")

    # 7. Date of Plantation
    plantation_done_on = st.date_input(
        "7. Plantation Date*", 
        value=ist_today,
        max_value=ist_today
    )

    # 8. Description
    description = st.text_area("8. Description*", placeholder="Briefly describe the activity or event details...")

    # 9. Photo Upload (Max size: 2MB)
    photo = st.file_uploader("9. Photo Upload* (Max size: 2MB)", type=["jpg", "jpeg", "png"])
    MAX_FILE_SIZE = 2 * 1024 * 1024
    
    if photo is not None:
        if photo.size > MAX_FILE_SIZE:
            st.error("File size exceeds the 2 MB limit. Please upload a smaller image.")
            photo = None

    # Add widget alongside participant count
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        participant_count = st.number_input("10. Number of Participants*", min_value=1, step=1, value=1)
    with col_p2:
        no_of_trees_planted = st.number_input("11. Total Number of Trees Planted*", min_value=1, step=1, value=1)
        
    # Submit and Reset Buttons with unique keys
    col_submit, col_reset = st.columns(2)

    with col_submit:
        submit_button = st.form_submit_button(
            label="Submit Registration", 
            key="submit_btn", 
            use_container_width=True
        )

    with col_reset:
        reset_button = st.form_submit_button(
            label="Reset Form", 
            key="reset_btn", 
            use_container_width=True
        )

# Form Submission Logic
if reset_button:
    st.toast("Form has been reset and cleared.", icon="🧹")

elif submit_button:
    if not name or not mobile or not designation or not department or not state or not district or not description or not plantation_done_on or photo is None:
        st.error("Please fill in all mandatory fields (*) and upload a valid photo (<= 2MB).")
    elif len(mobile) != 10 or not mobile.isdigit():
        st.error("Please enter a valid 10-digit mobile number.")
    else:
        try:
            # Compress image before saving to DB
            img = Image.open(photo)
            # Convert transparency (RGBA / P / LA) to RGB for JPEG compatibility
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            img.thumbnail((800, 800))  # Resize max dimensions to 800px
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=70)  # Compress JPEG quality
            photo_bytes = buffer.getvalue()
            photo_filename = photo.name

            # Parameterized query using SQLAlchemy named syntax
            insert_query = text("""
                INSERT INTO van_mahotsav_submissions 
                (name, mobile, designation, department, state, district, description, photo_filename, photo_bytes, participant_count, no_of_trees_planted, plantation_done_on)
                VALUES (:name, :mobile, :designation, :department, :state, :district, :description, :filename, :bytes, :count, :trees, :plantation_date)
            """)

            # Execute via st.connection session
            with conn.session as session:
                session.execute(insert_query, {
                    "name": name,
                    "mobile": mobile,
                    "designation": designation,
                    "department": department,
                    "state": state,
                    "district": district,
                    "description": description,
                    "filename": photo_filename,
                    "bytes": photo_bytes,  # Raw bytes are automatically mapped to BYTEA
                    "count": participant_count,
                    "trees": no_of_trees_planted,
                    "plantation_date": plantation_done_on
                })
                session.commit()
            # Generate Certificate Bytes
            cert_bytes = generate_certificate(name, str(plantation_done_on), no_of_trees_planted)

            st.toast("Form submitted successfully! Thank you for participating in Van Mahotsav 2026.", icon="🎉")
            st.balloons()

            st.success("✅ Submission Successful! Your certificate is ready.")
            st.image(cert_bytes, caption="Generated Certificate Preview", use_container_width=True)

            st.download_button(
                label="📥 Download Your Certificate",
                data=cert_bytes,
                file_name=f"Van_Mahotsav_Certificate_{name.replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True
            )

            # Clear cached queries so the new entry immediately reflects in the gallery
            st.cache_data.clear()

        except Exception as e:
            st.error(f"Failed to save data to NeonDB: {e}")

# Universal Government Footer (Always renders)
st.markdown(
    """
    <div class="gov-footer-wrapper">
        <div class="gov-footer-content">
            <p class="gov-footer-owner">Content Owned by District Administration</p>
            <p class="gov-footer-host">
                Developed and hosted by <span class="nic-brand-text">National Informatics Centre, District Centre Jammu</span>,<br>
                Ministry of Electronics & Information Technology, Government of India
            </p>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)