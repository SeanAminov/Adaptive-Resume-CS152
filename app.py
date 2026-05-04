import os
import json

# Flask + request handling
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

# Core pipeline logic
from matcher import match_resume_to_job
from parser import parse_resume
from skill_extractor import extract_skills

# Database helpers
from db import init_db, get_connection


# ----------------------------
# App configuration
# ----------------------------
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE_MB = 5

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024
app.secret_key = 'dev-secret-change-for-prod'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database tables at startup
init_db()


# ----------------------------
# Helper: check file extension
# ----------------------------
def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


# ----------------------------
# Route: Home page
# ----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# ----------------------------
# Route: Upload + Process Resume
# ----------------------------
@app.route('/upload', methods=['POST'])
def upload():

    # ----------------------------
    # 1. Validate uploaded file
    # ----------------------------
    if 'resume' not in request.files:
        flash('No file uploaded.')
        return redirect(url_for('index'))

    file = request.files['resume']

    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('File type not supported. Please upload a PDF.')
        return redirect(url_for('index'))

    # ----------------------------
    # 2. Save file locally
    # ----------------------------
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # ----------------------------
    # 3. Parse resume PDF into text
    # ----------------------------
    try:
        resume_text = parse_resume(filepath)
    except Exception as e:
        flash(f'Could not parse resume: {e}')
        return redirect(url_for('index'))

    # ----------------------------
    # 4. Get optional job description input
    # ----------------------------
    job_text = request.form.get('job_description', '').strip()

    # ----------------------------
    # 5. Extract skills from uploaded resume
    # ----------------------------
    resume_skills = extract_skills(resume_text)

    # ----------------------------
    # 6. Save uploaded resume to DB
    # ----------------------------
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resumes (filename, resume_text, skills)
        VALUES (?, ?, ?)
    """, (filename, resume_text, json.dumps(resume_skills)))

    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # ----------------------------
    # 7. Analyze only THIS uploaded resume
    # ----------------------------
    match_result = None
    job_id = None

    if job_text:

        # ----------------------------
        # 7a. Save or reuse job
        # Same job description = same job_id
        # ----------------------------
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM jobs
            WHERE job_description = ?
        """, (job_text,))

        existing_job = cursor.fetchone()

        if existing_job:
            job_id = existing_job[0]
        else:
            cursor.execute("""
                INSERT INTO jobs (title, job_description)
                VALUES (?, ?)
            """, ("Untitled Job", job_text))

            job_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # ----------------------------
        # 7b. Match ONLY the uploaded resume
        # This prevents auto-picking best resume every upload
        # ----------------------------
        match_result = match_resume_to_job(resume_text, job_text)

        # ----------------------------
        # 7c. Save this resume's match result
        # Links uploaded resume ↔ job via job_id
        # ----------------------------
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO matches (job_id, resume_id, score, missing_skills)
            VALUES (?, ?, ?, ?)
        """, (
            job_id,
            resume_id,
            match_result['overall_score'],
            json.dumps(match_result.get('missing_skills', []))
        ))

        conn.commit()
        conn.close()

    # ----------------------------
    # 8. Render uploaded resume analysis
    # ----------------------------
    return render_template(
        'result.html',
        filename=filename,
        job_id=job_id,
        text=resume_text,
        skills=resume_skills,
        skill_count=len(resume_skills),
        job_text=job_text,
        match=match_result,
    )


# ----------------------------
# Route: Find best resume for a job
# Triggered by UI button
# ----------------------------
@app.route('/best-match/<int:job_id>')
def best_match(job_id):

    # ----------------------------
    # 1. Query best saved match for this job
    # ----------------------------
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            resumes.filename,
            matches.score,
            matches.missing_skills
        FROM matches
        JOIN resumes ON matches.resume_id = resumes.id
        WHERE matches.job_id = ?
        ORDER BY matches.score DESC
        LIMIT 1
    """, (job_id,))

    best = cursor.fetchone()
    conn.close()

    # ----------------------------
    # 2. Handle case where no matches exist
    # ----------------------------
    if not best:
        flash('No matches found for this job yet.')
        return redirect(url_for('index'))

    best_filename, best_score, missing_skills = best

    # ----------------------------
    # 3. Render best match result
    # ----------------------------
    return render_template(
        'best_match.html',
        best_filename=best_filename,
        best_score=best_score,
        missing_skills=json.loads(missing_skills)
    )


# ----------------------------
# Run app
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)