import streamlit as st
import fitz  # PyMuPDF
from db import get_submission_by_identifier
from utils.certificate import generate_paalna_certificate

st.markdown("## 📜 Search & Download PAALNA Certificate")
st.write("Enter your **Student Name** or **Tree's Name** to generate your adoption certificate.")

search_query = st.text_input("Enter Search Term", placeholder="e.g. Rahul Sharma or Green Warrior")

if st.button("Search & Generate", type="primary"):
    if search_query.strip():
        record = get_submission_by_identifier(search_query)
        if record:
            (s_name, s_class, sch_name, t_name, species, p_date, height, loc, teacher, h_guardian) = record
            
            # 1. Generate PDF Bytes
            cert_bytes = generate_paalna_certificate(
                student_name=s_name, student_class=s_class, school_name=sch_name,
                tree_name=t_name, species=species, planted_on=str(p_date),
                height_cm=str(height), location=loc, teacher_name=teacher,
                holiday_guardian=h_guardian
            )
            
            # 2. Render PDF Page to PNG image bytes
            doc = fitz.open(stream=cert_bytes, filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            preview_img_bytes = pix.tobytes("png")
            
            st.success(f"Certificate generated for student: **{s_name}** ({sch_name})")
            
            # 3. Compact Layout: Place the image inside a smaller centered column
            col1, col2, col3 = st.columns([1, 2, 1])  # Centers preview at ~50% width
            with col2:
                st.image(preview_img_bytes, caption="Certificate Preview", use_container_width=True)
            
            # 4. Download Button
            st.download_button(
                label="📥 Download Certificate (PDF)",
                data=cert_bytes,
                file_name=f"PAALNA_Certificate_{s_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("No record found matching that search term.")
    else:
        st.error("Please enter a search string.")