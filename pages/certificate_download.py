import fitz  # PyMuPDF
import streamlit as st
from db import conn, search_submissions_by_name_or_tree_id
from utils.certificate import generate_paalna_certificate

st.markdown("## 📜 Search & Download PAALNA Certificate")
st.write(
    "Enter a **Student Name** or **Tree ID** to search matching records."
)

search_query = st.text_input(
    "Enter Search Term", placeholder="e.g. Rahul Sharma or 1042"
)

if st.button("Search", type="primary"):
    if search_query.strip():
        # Retrieve up to 20 matching records from the database
        records = search_submissions_by_name_or_tree_id(
            search_query.strip(), limit=20
        )

        if records:
            st.session_state["search_results"] = records
            st.success(f"Found {len(records)} matching record(s).")
        else:
            st.session_state["search_results"] = []
            st.warning("No records found matching that search term.")
    else:
        st.error("Please enter a student name or tree ID.")

# Display search results if available in session state
if "search_results" in st.session_state and st.session_state["search_results"]:
    records = st.session_state["search_results"]

    # Let the user select a specific student/tree record from the matching list
    options = {
        f"ID: {rec[0]} | Student: {rec[1]} | School: {rec[3]} | Tree Species: {rec[5]}": rec
        for rec in records
    }

    selected_label = st.radio(
        "Select the record you want to generate a certificate for:",
        options=list(options.keys()),
    )

    selected_record = options[selected_label]

    if st.button("Generate Selected Certificate", type="secondary"):
        (
            sub_id,
            s_name,
            s_class,
            sch_name,
            t_name,
            species,
            p_date,
            height,
            loc,
            teacher,
            h_guardian,
            photo_bytes,
        ) = selected_record

        # 1. Generate PDF Bytes
        cert_bytes = generate_paalna_certificate(
            student_name=s_name,
            student_class=s_class,
            school_name=sch_name,
            tree_name=t_name,
            species=species,
            planted_on=str(p_date),
            height_cm=str(height),
            location=loc,
            teacher_name=teacher,
            holiday_guardian=h_guardian,
            submission_id=sub_id,
            photo_bytes=photo_bytes,
        )

        # 2. Render PDF Page to PNG image bytes using PyMuPDF
        doc = fitz.open(stream=cert_bytes, filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        preview_img_bytes = pix.tobytes("png")

        # 3. Preview & Download Section
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(
                preview_img_bytes,
                caption=f"Certificate Preview: {s_name}",
                use_container_width=True,
            )

        st.download_button(
            label="📥 Download Certificate (PDF)",
            data=cert_bytes,
            file_name=f"PAALNA_Certificate_{s_name.replace(' ', '_')}_{sub_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )