import io
import streamlit as st
from PIL import Image, ImageOps
from db import fetch_submissions

st.markdown("## 📸 PAALNA Media Submissions Gallery")

# Manage display count using session state (default = 10)
if "gallery_limit" not in st.session_state:
    st.session_state["gallery_limit"] = 10

# Display loading spinner while fetching submissions
with st.spinner("Loading media gallery..."):
    submissions = fetch_submissions(limit=st.session_state["gallery_limit"])

if not submissions:
    st.info("No submissions found in the database yet.")
else:
    cols_per_row = 3
    cols = st.columns(cols_per_row)

    for index, item in enumerate(submissions):
        (s_name, s_class, sch_name, t_name, species, 
         p_date, height, loc, teacher, h_guardian, photo, sub_date) = item
        
        col_target = cols[index % cols_per_row]
        
        with col_target:
            # Form-matching styled card wrapper using unique, dynamic keys
            with st.container(border=True, key=f"gallery_card_{index}"):
                # Fix image rendering for PostgreSQL BYTEA / memoryview
                photo_bytes = None
                if photo:
                    try:
                        # Handle memoryview/bytes conversion safely
                        if isinstance(photo, memoryview):
                            photo_bytes = photo.tobytes()
                        elif isinstance(photo, bytes):
                            photo_bytes = photo
                        else:
                            photo_bytes = bytes(photo)

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
                
                formatted_submitted_date = sub_date.strftime("%b %d, %Y - %I:%M %p") if sub_date else "N/A"
                formatted_plantation_date = p_date.strftime("%b %d, %Y") if p_date else "N/A"

                st.markdown(f"##### 🌳 {t_name}")
                st.markdown(f"**👤 Student:** {s_name} ({s_class})")
                st.markdown(f"**🏫 School:** {sch_name}")
                st.markdown(f"**🌿 Species:** {species} ({height} cm)")
                st.markdown(f"**📍 Location:** {loc}")
                st.markdown(f"**🌱 Planted On:** {formatted_plantation_date}")
                st.caption(f"📅 *Submitted on: {formatted_submitted_date}*")

    # "Load More" button at the bottom
    if len(submissions) >= st.session_state.get("gallery_limit", 10):
        st.markdown("<br>", unsafe_allow_html=True)
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            if st.button("🔄 Load More Submissions", key="load_more_btn", use_container_width=True):
                st.session_state["gallery_limit"] = st.session_state.get("gallery_limit", 10) + 10
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