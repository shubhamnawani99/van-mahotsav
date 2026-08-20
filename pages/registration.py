import io
import datetime
import zoneinfo
import streamlit as st
from PIL import Image
from sqlalchemy import text
from db import conn
from utils.certificate import generate_paalna_certificate

ist_today = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).date()

st.markdown("### 🌳 PAALNA - Tree Adoption Registration Form")

with st.form(key="paalna_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("1. Student Name*", placeholder="Enter student full name")
        student_class = st.text_input("2. Class*", placeholder="e.g., 8th-A")
        school_name = st.text_input("3. School Name*", placeholder="e.g., Govt Higher Sec School Jammu")
        tree_name = st.text_input("4. Tree's Name*", placeholder="e.g., Green Warrior")
        species = st.text_input("5. Tree Species*", placeholder="e.g., Neem / Mango / Chinar")
    
    with col2:
        planted_on = st.date_input("6. Planted On*", value=ist_today, max_value=ist_today)
        height_cm = st.number_input("7. Height at Planting (cm)*", min_value=10, max_value=500, value=50)
        location = st.text_input("8. Location / Lat-Long*", placeholder="e.g., School Garden (32.7266, 74.8570)")
        teacher_name = st.text_input("9. Co-guardian Teacher Name*", placeholder="Teacher in-charge name")
        holiday_guardian = st.text_input("10. Holiday Guardian Name*", placeholder="Holiday caretaker name")

    photo = st.file_uploader("11. Upload Plantation Photo*", type=["jpg", "jpeg", "png"])
    submit_button = st.form_submit_button("Submit & Generate Certificate", use_container_width=True)

if submit_button:
    if not all([student_name, student_class, school_name, tree_name, species, location, teacher_name, holiday_guardian, photo]):
        st.error("Please fill in all mandatory fields (*).")
    else:
        try:
            img = Image.open(photo)
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            img.thumbnail((800, 800))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=70)
            photo_bytes = buffer.getvalue()

            insert_query = text("""
                INSERT INTO paalna_submissions 
                (student_name, student_class, school_name, tree_name, species, planted_on, height_cm, location, teacher_name, holiday_guardian, photo_bytes)
                VALUES (:s_name, :s_class, :sch_name, :t_name, :species, :p_date, :height, :loc, :teacher, :h_guardian, :photo)
            """)

            with conn.session as session:
                session.execute(insert_query, {
                    "s_name": student_name, "s_class": student_class, "sch_name": school_name,
                    "t_name": tree_name, "species": species, "p_date": planted_on,
                    "height": height_cm, "loc": location, "teacher": teacher_name,
                    "h_guardian": holiday_guardian, "photo": photo_bytes
                })
                session.commit()

            st.cache_data.clear()

            cert_bytes = generate_paalna_certificate(
                student_name=student_name, student_class=student_class, school_name=school_name,
                tree_name=tree_name, species=species, planted_on=str(planted_on),
                height_cm=str(height_cm), location=location, teacher_name=teacher_name,
                holiday_guardian=holiday_guardian
            )

            st.toast("Registration Successful!", icon="🎉")
            st.balloons()
            st.image(cert_bytes, caption="Generated Certificate Preview", use_container_width=True)
            st.download_button(
                label="📥 Download Certificate (PNG)",
                data=cert_bytes,
                file_name=f"PAALNA_Certificate_{student_name.replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error saving registration: {e}")