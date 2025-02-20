from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import spacy
import re
import os
import fitz
from datetime import datetime
from config.tech_stack import TECH_STACK_DICT, SKILL_CATEGORIES, get_skill_category, get_related_skills

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobmatch.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'candidate' or 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100))
    resume_path = db.Column(db.String(200))
    skills = db.Column(db.Text)
    experience = db.Column(db.Integer)
    education = db.Column(db.Text)
    github_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    extracted_keywords = db.Column(db.Text)

class RecruiterProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profile.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    experience_required = db.Column(db.Integer)
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profile.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    match_score = db.Column(db.Float)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions from the original script (cleaned_up and modified)
def clean_text(text):
    """Clean the extracted text by removing non-ASCII characters and normalizing whitespace."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return clean_text(text)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'candidate':
        return render_template('candidate_dashboard.html')
    else:
        return render_template('recruiter_dashboard.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.user_type == 'candidate':
        profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
        if request.method == 'POST':
            # Handle candidate profile update
            pass
        return render_template('candidate_profile.html', profile=profile)
    else:
        profile = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
        if request.method == 'POST':
            # Handle recruiter profile update
            pass
        return render_template('recruiter_profile.html', profile=profile)

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.user_type != 'recruiter':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        job = JobPosting(
            recruiter_id=current_user.id,
            title=request.form['title'],
            description=request.form['description'],
            required_skills=request.form['required_skills'],
            experience_required=int(request.form['experience_required']),
            location=request.form['location'],
            salary_range=request.form['salary_range']
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('post_job.html')

@app.route('/search-jobs')
@login_required
def search_jobs():
    if current_user.user_type != 'candidate':
        return redirect(url_for('dashboard'))
    
    jobs = JobPosting.query.filter_by(status='active').all()
    return render_template('search_jobs.html', jobs=jobs)

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.user_type != 'candidate':
        return redirect(url_for('dashboard'))
    
    candidate_profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
    job = JobPosting.query.get_or_404(job_id)
    
    # Calculate match score
    match_score = calculate_match_score(candidate_profile, job)
    
    application = Application(
        job_id=job_id,
        candidate_id=candidate_profile.id,
        match_score=match_score
    )
    db.session.add(application)
    db.session.commit()
    
    flash('Application submitted successfully')
    return redirect(url_for('search_jobs'))

def calculate_match_score(candidate_profile, job_posting, tech_stack_dict):
    """
    Calculate a comprehensive match score between a candidate and job posting.
    Uses multiple data sources: profile data, resume text, and keyword matching.
    Returns a score between 0 and 100, with detailed breakdown.
    """
    # Initialize score components
    skill_match_score = 0
    experience_match_score = 0
    keyword_match_score = 0
    education_match_score = 0
    
    # Get required skills from job posting
    required_skills = set(skill.strip().lower() for skill in job_posting.required_skills.split(','))
    
    # Get candidate skills from profile
    candidate_skills = set(skill.strip().lower() for skill in candidate_profile.skills.split(','))
    
    # Extract keywords from resume if available
    resume_keywords = set()
    if candidate_profile.resume_path:
        try:
            resume_text = extract_text_from_pdf(candidate_profile.resume_path)
            resume_keywords = extract_keywords_from_resume(resume_text, tech_stack_dict)
        except Exception as e:
            print(f"Error processing resume: {e}")
    
    # Combine profile skills and resume keywords
    all_candidate_skills = candidate_skills.union(resume_keywords)
    
    # Calculate skill match score (40% of total)
    if required_skills:
        matched_skills = required_skills.intersection(all_candidate_skills)
        skill_match_score = (len(matched_skills) / len(required_skills)) * 40
    
    # Calculate experience match score (25% of total)
    if job_posting.experience_required:
        experience_ratio = min(candidate_profile.experience / job_posting.experience_required, 1.5)
        experience_match_score = min(experience_ratio * 25, 25)
    
    # Calculate keyword match using tech stack dictionary (20% of total)
    job_description_keywords = extract_keywords_from_text(job_posting.description, tech_stack_dict)
    if job_description_keywords:
        matched_keywords = job_description_keywords.intersection(all_candidate_skills)
        keyword_match_score = (len(matched_keywords) / len(job_description_keywords)) * 20
    
    # Calculate education match score (15% of total)
    education_match_score = calculate_education_match(
        candidate_profile.education,
        job_posting.description
    )
    
    # Calculate total score
    total_score = (
        skill_match_score +
        experience_match_score +
        keyword_match_score +
        education_match_score
    )
    
    # Round to 2 decimal places
    total_score = round(total_score, 2)
    
    # Prepare detailed breakdown
    score_breakdown = {
        'total_score': total_score,
        'skill_match': {
            'score': skill_match_score,
            'matched_skills': list(required_skills.intersection(all_candidate_skills)),
            'missing_skills': list(required_skills - all_candidate_skills)
        },
        'experience_match': {
            'score': experience_match_score,
            'candidate_experience': candidate_profile.experience,
            'required_experience': job_posting.experience_required
        },
        'keyword_match': {
            'score': keyword_match_score,
            'matched_keywords': list(matched_keywords),
            'total_keywords': len(job_description_keywords)
        },
        'education_match': {
            'score': education_match_score
        }
    }
    
    return total_score, score_breakdown

def extract_keywords_from_resume(text, tech_stack_dict):
    """
    Extract technical keywords from resume text using the tech stack dictionary.
    Includes fuzzy matching and context analysis.
    """
    keywords = set()
    text = text.lower()
    
    # Process text with spaCy for better context understanding
    doc = nlp(text)
    
    # Extract sentences containing technical terms for context
    tech_sentences = []
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if any(term.lower() in sent_text for terms in tech_stack_dict.values() for term in terms):
            tech_sentences.append(sent_text)
    
    # Check for tech stack terms in the context of technical sentences
    for tech, terms in tech_stack_dict.items():
        for term in terms:
            term = term.lower()
            # Check in whole text
            if term in text:
                keywords.add(tech)
            # Check in technical sentences for better context
            for sent in tech_sentences:
                if term in sent:
                    keywords.add(tech)
    
    return keywords

def extract_keywords_from_text(text, tech_stack_dict):
    """Extract keywords from any text using the tech stack dictionary."""
    keywords = set()
    text = text.lower()
    
    for tech, terms in tech_stack_dict.items():
        if any(term.lower() in text for term in terms):
            keywords.add(tech)
    
    return keywords

def calculate_education_match(candidate_education, job_description):
    """
    Calculate education match score based on requirements in job description
    and candidate's education.
    """
    education_score = 0
    education_levels = {
        'phd': 5,
        'master': 4,
        'bachelor': 3,
        'associate': 2,
        'high school': 1
    }
    
    # Convert education text to lowercase for matching
    candidate_education = candidate_education.lower()
    job_description = job_description.lower()
    
    # Find highest education level mentioned in job description
    required_level = 0
    for level, score in education_levels.items():
        if level in job_description:
            required_level = max(required_level, score)
    
    # Find candidate's highest education level
    candidate_level = 0
    for level, score in education_levels.items():
        if level in candidate_education:
            candidate_level = max(candidate_level, score)
    
    # Calculate education score
    if required_level == 0 or candidate_level >= required_level:
        education_score = 15  # Full score if no specific requirement or exceeds requirement
    else:
        # Partial score based on how close candidate is to required level
        education_score = (candidate_level / required_level) * 15
    
    return round(education_score, 2)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)