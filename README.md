# Adaptive Resume Matcher

Adaptive Resume Matcher is a Flask-based web app that analyzes resumes against job descriptions using a combination of **TF-IDF text similarity** and **skill matching**. It helps users understand how well their resume fits a role and identify missing skills.

---
## Project Members
* Sean Aminov
* Nagi Ebeid

## Features

* Upload PDF resumes
* Extract resume text and skills
* Compute match score using:

  * Skill overlap (weighted higher)
  * Text similarity (TF-IDF + cosine similarity)
* Highlight:

  * Matched skills
  * Missing skills
* Store data using SQLite:

  * Multiple resumes
  * Multiple job descriptions
  * Match results
* Find best resume for a job (on demand)

---

## Tech Stack

* Python (Flask)
* SQLite (via `sqlite3`)
* scikit-learn (TF-IDF + cosine similarity)
* pdfplumber (PDF parsing)
* HTML/CSS

---

## Project Structure

```
Adaptive-Resume/
│
├── app.py                  # Main Flask app
├── db.py                   # Database setup (SQLite)
├── matcher.py              # Matching logic (scoring)
├── parser.py               # PDF parsing
├── skill_extractor.py      # Skill extraction + comparison
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── best_match.html
│
├── static/
│   └── style.css
│
├── uploads/                # Uploaded resumes
├── resumes.db              # SQLite database (auto-created)
└── README.md
```

---

## Setup Instructions

### 1. Clone the repo

```
git clone <your-repo-url>
cd Adaptive-Resume-CS152
```

---

### 2. Create virtual environment (recommended)

```
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# or
venv\Scripts\activate         # Windows
```

---

### 3. Install dependencies

```
pip install flask pdfplumber scikit-learn
```

---

### 4. Run the app

```
python3 app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## Database

The app uses SQLite (`resumes.db`) with three tables:

### resumes

Stores uploaded resumes

```
id | filename | resume_text | skills
```

### jobs

Stores job descriptions

```
id | title | job_description | created_at
```

### matches

Links resumes to jobs

```
id | job_id | resume_id | score | missing_skills
```

---

## How It Works

1. User uploads a resume (PDF)
2. App extracts text and skills
3. User optionally provides a job description
4. App:

   * Saves job (or reuses existing one)
   * Computes match score for the uploaded resume
   * Stores result in database
5. User can click:

   * **"Find Best Resume for This Job"**
   * App compares all stored resumes and returns the best match

---

## Scoring Logic

Final score is a weighted combination:

```
score = (0.7 * skill_overlap) + (0.3 * text_similarity)
```

* Skill overlap = % of job skills present in resume
* Text similarity = cosine similarity of TF-IDF vectors

---

## Resetting the Database (if needed)

If you change schema:

```
rm resumes.db
python3 app.py
```

---

## Future Improvements

* Resume ranking (top N instead of just best)
* Feedback-based learning
* Job naming / labeling
* UI dashboard for job history
* Better NLP (e.g., embeddings instead of TF-IDF)
