# Flask app for the Adaptive Resume Matcher.
# Handles resume uploads, text extraction, skill detection, and
# (optionally) matching the resume against a pasted job description.

import os

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from matcher import match_resume_to_job
from parser import parse_resume
from skill_extractor import extract_skills


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE_MB = 5

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024
# Only used for flash messages. Not a real secret.
app.secret_key = 'dev-secret-change-for-prod'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Basic guards on the uploaded file.
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

    # Save the uploaded resume.
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Parse it.
    try:
        resume_text = parse_resume(filepath)
    except Exception as e:
        flash(f'Could not parse resume: {e}')
        return redirect(url_for('index'))

    # Job description is optional - if it's there we run matching too.
    job_text = request.form.get('job_description', '').strip()
    match_result = None
    if job_text:
        match_result = match_resume_to_job(resume_text, job_text)
        resume_skills = match_result['resume_skills']
    else:
        resume_skills = extract_skills(resume_text)

    return render_template(
        'result.html',
        filename=filename,
        text=resume_text,
        skills=resume_skills,
        skill_count=len(resume_skills),
        job_text=job_text,
        match=match_result,
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
