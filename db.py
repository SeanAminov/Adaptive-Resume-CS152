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
        skills TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ----------------------------
    # Jobs table
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
    # Matches table
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

    # ----------------------------
    # Feedback table
    # Thumbs up / down on a match.
    # rating is 1 (up) or -1 (down).
    # ----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        rating INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(match_id) REFERENCES matches(id)
    )
    """)

    # Older databases may not have a created_at column on resumes.
    # Try to add it; ignore the error if it's already there.
    try:
        cursor.execute("ALTER TABLE resumes ADD COLUMN created_at TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
