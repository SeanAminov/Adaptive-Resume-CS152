import os
import json

# Flask + request handling
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

# Core pipeline logic
from matcher import match_resume_to_job
from parser import parse_resume
from skill_extractor import extract_skills
from skill_resources import get_resources

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
# Helpers
# ----------------------------
def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def guess_job_title(job_text):
    """
    Pull a title from the first non-empty line of the pasted
    description. Job postings almost always lead with the role.
    """
    for line in job_text.splitlines():
        line = line.strip()
        if line:
            # Cap length so a giant first line doesn't blow up the UI.
            return line[:100]
    return 'Untitled Job'


def build_roadmap(missing_skills):
    """Pair each missing skill with a couple of learning resources."""
    return [(skill, get_resources(skill)) for skill in missing_skills]


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

    # 1. Validate uploaded file
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

    # 2. Save file locally
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # 3. Parse resume PDF into text
    try:
        resume_text = parse_resume(filepath)
    except Exception as e:
        flash(f'Could not parse resume: {e}')
        return redirect(url_for('index'))

    if not resume_text.strip():
        flash('No text could be extracted from this PDF. It might be scanned or image-only.')
        return redirect(url_for('index'))

    # 4. Get optional job description + title input
    job_text = request.form.get('job_description', '').strip()
    user_job_title = request.form.get('job_title', '').strip()

    # 5. Extract skills from uploaded resume
    resume_skills = extract_skills(resume_text)

    # 6. Save uploaded resume to DB
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (filename, resume_text, skills)
        VALUES (?, ?, ?)
    """, (filename, resume_text, json.dumps(resume_skills)))
    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 7. Match against job (if one was provided)
    match_result = None
    job_id = None
    match_id = None
    roadmap = []

    if job_text:
        # 7a. Save or reuse job - same description = same job_id.
        # Prefer the user-provided title; otherwise grab the first
        # line of the description as a heuristic.
        job_title = user_job_title or guess_job_title(job_text)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM jobs WHERE job_description = ?", (job_text,))
        existing_job = cursor.fetchone()

        if existing_job:
            job_id = existing_job[0]
        else:
            cursor.execute("""
                INSERT INTO jobs (title, job_description)
                VALUES (?, ?)
            """, (job_title, job_text))
            job_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # 7b. Run the match (only on the resume that was just uploaded)
        match_result = match_resume_to_job(resume_text, job_text)

        # 7c. Save the match
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
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()

        roadmap = build_roadmap(match_result.get('missing_skills', []))

    # 8. Render results
    return render_template(
        'result.html',
        filename=filename,
        job_id=job_id,
        match_id=match_id,
        text=resume_text,
        skills=resume_skills,
        skill_count=len(resume_skills),
        job_text=job_text,
        match=match_result,
        roadmap=roadmap,
    )


# ----------------------------
# Route: Find best resume for a job
# ----------------------------
@app.route('/best-match/<int:job_id>')
def best_match(job_id):
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

    if not best:
        flash('No matches found for this job yet.')
        return redirect(url_for('index'))

    best_filename, best_score, missing_skills = best
    missing = json.loads(missing_skills)

    return render_template(
        'best_match.html',
        best_filename=best_filename,
        best_score=best_score,
        missing_skills=missing,
        roadmap=build_roadmap(missing),
    )


# ----------------------------
# Route: List all saved jobs
# ----------------------------
@app.route('/jobs')
def jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            jobs.id,
            jobs.title,
            jobs.created_at,
            COUNT(matches.id) AS match_count
        FROM jobs
        LEFT JOIN matches ON matches.job_id = jobs.id
        GROUP BY jobs.id
        ORDER BY jobs.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    job_list = [
        {'id': r[0], 'title': r[1], 'created_at': r[2], 'match_count': r[3]}
        for r in rows
    ]
    return render_template('jobs.html', jobs=job_list)


# ----------------------------
# Route: View a single saved job
# ----------------------------
@app.route('/jobs/<int:job_id>')
def view_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, job_description, created_at
        FROM jobs WHERE id = ?
    """, (job_id,))
    job_row = cursor.fetchone()

    if not job_row:
        conn.close()
        flash('Job not found.')
        return redirect(url_for('jobs'))

    # Pull every resume that's been scored against this job, best first.
    cursor.execute("""
        SELECT
            matches.id,
            resumes.id,
            resumes.filename,
            matches.score,
            matches.missing_skills,
            matches.created_at
        FROM matches
        JOIN resumes ON matches.resume_id = resumes.id
        WHERE matches.job_id = ?
        ORDER BY matches.score DESC
    """, (job_id,))
    match_rows = cursor.fetchall()
    conn.close()

    matches = [
        {
            'match_id': m[0],
            'resume_id': m[1],
            'filename': m[2],
            'score': m[3],
            'missing_skills': json.loads(m[4]) if m[4] else [],
            'created_at': m[5],
        }
        for m in match_rows
    ]

    job = {
        'id': job_row[0],
        'title': job_row[1],
        'description': job_row[2],
        'created_at': job_row[3],
    }

    return render_template('job_detail.html', job=job, matches=matches)


# ----------------------------
# Route: Rename a saved job
# ----------------------------
@app.route('/jobs/<int:job_id>/rename', methods=['POST'])
def rename_job(job_id):
    new_title = request.form.get('title', '').strip()
    if not new_title:
        flash('Title cannot be empty.')
        return redirect(url_for('view_job', job_id=job_id))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET title = ? WHERE id = ?",
                   (new_title[:100], job_id))
    conn.commit()
    conn.close()

    flash('Job renamed.')
    return redirect(url_for('view_job', job_id=job_id))


# ----------------------------
# Route: Delete a saved job
# ----------------------------
@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Drop matches first so we don't leave orphans.
    cursor.execute("DELETE FROM matches WHERE job_id = ?", (job_id,))
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

    flash('Job deleted.')
    return redirect(url_for('jobs'))


# ----------------------------
# Route: List all saved resumes
# ----------------------------
@app.route('/resumes')
def resumes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, skills, created_at
        FROM resumes
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    resume_list = []
    for r in rows:
        skills = json.loads(r[2]) if r[2] else []
        resume_list.append({
            'id': r[0],
            'filename': r[1],
            'skill_count': len(skills),
            'created_at': r[3],
        })
    return render_template('resumes.html', resumes=resume_list)


# ----------------------------
# Route: View a single saved resume
# ----------------------------
@app.route('/resumes/<int:resume_id>')
def view_resume(resume_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filename, resume_text, skills, created_at
        FROM resumes WHERE id = ?
    """, (resume_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        flash('Resume not found.')
        return redirect(url_for('resumes'))

    filename, resume_text, skills_json, created_at = row
    skills = json.loads(skills_json) if skills_json else []

    return render_template(
        'resume_detail.html',
        filename=filename,
        text=resume_text,
        skills=skills,
        skill_count=len(skills),
        created_at=created_at,
    )


# ----------------------------
# Route: Delete a saved resume
# ----------------------------
@app.route('/resumes/<int:resume_id>/delete', methods=['POST'])
def delete_resume(resume_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Drop any related matches first.
    cursor.execute("DELETE FROM matches WHERE resume_id = ?", (resume_id,))
    cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()
    conn.close()
    flash('Resume deleted.')
    return redirect(url_for('resumes'))


# ----------------------------
# Route: Submit feedback on a match
# ----------------------------
@app.route('/feedback/<int:match_id>/<int:rating>', methods=['POST'])
def feedback(match_id, rating):
    if rating not in (1, -1):
        flash('Invalid rating.')
        return redirect(url_for('index'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (match_id, rating) VALUES (?, ?)
    """, (match_id, rating))
    conn.commit()
    conn.close()

    flash('Thanks for the feedback. Future scores will adjust accordingly.')
    return redirect(url_for('index'))


# ----------------------------
# Run app
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
