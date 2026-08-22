import streamlit as st
from sqlalchemy import text

conn = st.connection("postgresql", type="sql")

def init_db():
    try:
        with conn.session as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS paalna_submissions (
                    id SERIAL PRIMARY KEY,
                    student_name VARCHAR(255) NOT NULL,
                    student_class VARCHAR(50) NOT NULL,
                    school_name VARCHAR(255) NOT NULL,
                    tree_name VARCHAR(255) NOT NULL,
                    species VARCHAR(100) NOT NULL,
                    planted_on DATE NOT NULL,
                    height_cm INT NOT NULL,
                    location TEXT NOT NULL,
                    teacher_name VARCHAR(255) NOT NULL,
                    holiday_guardian VARCHAR(255) NOT NULL,
                    photo_bytes BYTEA,
                    submitted_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
                );
            """))
            
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_paalna_submitted_at 
                ON paalna_submissions (submitted_at DESC);
            """))
            session.commit()
    except Exception as e:
        st.error(f"Database Initialization Error: {e}")

@st.cache_data(ttl=30, show_spinner=False)
def fetch_submissions(limit=10):
    try:
        query = text("""
            SELECT student_name, student_class, school_name, tree_name, species, 
                   planted_on, height_cm, location, teacher_name, holiday_guardian, 
                   photo_bytes, submitted_at 
            FROM paalna_submissions 
            ORDER BY submitted_at DESC 
            LIMIT :limit
        """)
        with conn.session as session:
            result = session.execute(query, {"limit": limit})
            clean_rows = []
            for row in result:
                clean_row = []
                for item in row:
                    if isinstance(item, memoryview):
                        clean_row.append(item.tobytes())
                    else:
                        clean_row.append(item)
                clean_rows.append(tuple(clean_row))
            return clean_rows
    except Exception as e:
        st.error(f"Failed to fetch submissions: {e}")
        return []

def get_submission_by_identifier(identifier: str):
    try:
        query = text("""
            SELECT id, student_name, student_class, school_name, tree_name, species, 
                   planted_on, height_cm, location, teacher_name, holiday_guardian, photo_bytes
            FROM paalna_submissions 
            WHERE LOWER(student_name) = LOWER(:id) OR LOWER(tree_name) = LOWER(:id)
            ORDER BY submitted_at DESC 
            LIMIT 1
        """)
        with conn.session as session:
            row = session.execute(query, {"id": identifier.strip()}).fetchone()
            if row:
                data = list(row)
                if isinstance(data[11], memoryview):
                    data[11] = data[11].tobytes()
                return tuple(data)
            return None
    except Exception as e:
        st.error(f"Error searching record: {e}")
        return None