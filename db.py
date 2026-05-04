import sqlite3

DB_NAME = "resumes.db"


# ----------------------------
# Get DB connection
# ----------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# ----------------------------
# Initialize database schema
# ----------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------
    # Resumes table
    # Stores uploaded resumes
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        resume_text TEXT,
        skills TEXT
    )
    """)

    # ----------------------------
    # Jobs table (NEW)
    # Stores each job description
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        job_description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ----------------------------
    # Matches table (UPDATED)
    # Links resumes ↔ jobs
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        resume_id INTEGER,
        score REAL,
        missing_skills TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(job_id) REFERENCES jobs(id),
        FOREIGN KEY(resume_id) REFERENCES resumes(id)
    )
    """)

    conn.commit()
    conn.close()