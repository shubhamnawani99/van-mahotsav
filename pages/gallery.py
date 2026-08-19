import io
import streamlit as st
from PIL import Image, ImageOps
from db import fetch_submissions

st.markdown("## 📸 Media Submissions Gallery")

# B. Manage display count using session state (default = 10)
if "gallery_limit" not in st.session_state:
    st.session_state["gallery_limit"] = 10

# A. Display loading spinner while fetching submissions
with st.spinner("Loading media gallery..."):
    submissions = fetch_submissions(limit=st.session_state["gallery_limit"])

if not submissions:
    st.info("No submissions found in the database yet.")
else:
    cols_per_row = 3
    cols = st.columns(cols_per_row)

    for index, item in enumerate(submissions):
        (rec_name, rec_designation, rec_dept, rec_state, rec_district, 
         rec_desc, rec_photo, rec_participants, rec_date) = item
        
        col_target = cols[index % cols_per_row]
        
        with col_target:
            # C. Form-matching styled card wrapper using unique, dynamic keys
            with st.container(border=True, key=f"gallery_card_{index}"):
                # D. Fix image rendering for PostgreSQL BYTEA / memoryview
                if rec_photo:
                    try:
                        # Handle memoryview/bytes conversion safely
                        if isinstance(rec_photo, memoryview):
                            photo_bytes = rec_photo.tobytes()
                        elif isinstance(rec_photo, bytes):
                            photo_bytes = rec_photo
                        else:
                            photo_bytes = bytes(rec_photo)

                        # Render with Streamlit or PIL fallback
                        img = Image.open(io.BytesIO(photo_bytes))
                        fixed_img = ImageOps.fit(img, (400, 250), Image.Resampling.LANCZOS)
                        st.image(fixed_img, use_container_width=True)
                    except Exception:
                        try:
                            # Direct byte array fallback
                            st.image(photo_bytes, use_container_width=True)
                        except Exception:
                            st.warning("⚠️ Image preview unavailable")
                
                formatted_date = rec_date.strftime("%b %d, %Y - %I:%M %p") if rec_date else "N/A"
                desc_snippet = rec_desc[:100] + "..." if len(rec_desc) > 100 else rec_desc

                st.markdown(f"##### 👤 {rec_name}")
                st.markdown(f"**Designation:** {rec_designation}")
                st.markdown(f"**🏢 Dept:** {rec_dept}")
                st.markdown(f"**📍 Location:** {rec_district}, {rec_state}")
                st.markdown(f"**👥 Participants:** {rec_participants}")
                st.markdown(f"**📝 Description:** {desc_snippet}")
                st.caption(f"📅 *Submitted on: {formatted_date}*")

    # B. "Load More" button at the bottom (shown if more entries exist)
    if len(submissions) >= st.session_state["gallery_limit"]:
        st.markdown("<br>", unsafe_allow_html=True)
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            if st.button("🔄 Load More Submissions", key="load_more_btn", use_container_width=True):
                st.session_state["gallery_limit"] += 10
                st.rerun()

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