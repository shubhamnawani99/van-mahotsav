import streamlit as st
from sqlalchemy import text

# Initialize connection using secrets configuration automatically
conn = st.connection("postgresql", type="sql")

def init_db():
    try:
        with conn.session as session:
            # Create Table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS van_mahotsav_submissions (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    mobile VARCHAR(15) NOT NULL,
                    designation VARCHAR(255) NOT NULL,
                    department VARCHAR(255) NOT NULL,
                    state VARCHAR(100) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    photo_filename VARCHAR(255),
                    photo_bytes BYTEA,
                    participant_count INT NOT NULL,
                    plantation_done_on DATE NOT NULL DEFAULT (CURRENT_DATE AT TIME ZONE 'Asia/Kolkata'),
                    submitted_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
                );
            """))
            
            # Create Index for performance
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_van_mahotsav_submitted_at 
                ON van_mahotsav_submissions (submitted_at DESC);

                CREATE INDEX IF NOT EXISTS idx_van_mahotsav_plantation_date 
                ON van_mahotsav_submissions (plantation_done_on DESC);
            """))
            
            session.commit()
    except Exception as e:
        st.error(f"Database Initialization Error: {e}")

@st.cache_data(ttl=30, show_spinner=False)
def fetch_submissions(limit=10):
    try:
        query = text("""
        SELECT name, designation, department, state, district, 
               description, photo_bytes, participant_count, plantation_done_on, submitted_at 
        FROM van_mahotsav_submissions 
        ORDER BY submitted_at DESC 
        LIMIT :limit
        """)
        
        with conn.session as session:
            result = session.execute(query, {"limit": limit})
            
            clean_rows = []
            for row in result:
                clean_row = []
                for item in row:
                    # Convert any memoryview objects (BYTEA) to pickle-safe bytes
                    if isinstance(item, memoryview):
                        clean_row.append(item.tobytes())
                    else:
                        clean_row.append(item)
                clean_rows.append(tuple(clean_row))
                
            return clean_rows
            
    except Exception as e:
        st.error(f"Failed to fetch media submissions: {e}")
        return []

def get_submission_by_identifier(identifier: str):
    """Fetch participant details by Mobile or Name."""
    try:
        query = text("""
            SELECT name, mobile, plantation_done_on 
            FROM van_mahotsav_submissions 
            WHERE mobile = :id OR LOWER(name) = LOWER(:id)
            ORDER BY submitted_at DESC 
            LIMIT 1
        """)
        with conn.session as session:
            result = session.execute(query, {"id": identifier.strip()}).fetchone()
            return result
    except Exception as e:
        st.error(f"Error searching database: {e}")
        return None