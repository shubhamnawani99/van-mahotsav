import streamlit as st
from db import get_submission_by_identifier
from utils.certificate import generate_certificate

st.markdown("## 📜 Search & Download Certificate")
st.write("Enter your registered **Mobile Number** or **Full Name** to generate your participation certificate.")

search_query = st.text_input("Enter Mobile Number or Full Name", placeholder="e.g. 9876543210 or Rahul Sharma")

if st.button("Search Registration", type="primary"):
    if search_query.strip():
        record = get_submission_by_identifier(search_query)
        if record:
            rec_name, rec_mobile, rec_date = record
            cert_bytes = generate_certificate(rec_name, str(rec_date))
            
            st.success(f"Record found for **{rec_name}**!")
            st.image(cert_bytes, caption="Certificate Preview", use_container_width=True)
            
            st.download_button(
                label="📥 Download Certificate (PNG)",
                data=cert_bytes,
                file_name=f"Certificate_{rec_name.replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            st.warning("No registration record found matching that Mobile Number or Name.")
    else:
        st.error("Please enter a valid search term.")