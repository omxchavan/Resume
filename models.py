from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20), nullable=False)  # 'candidate' or 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = db.relationship('Resume', backref='candidate', uselist=False)
    applications = db.relationship('Application', backref='candidate')
    job_postings = db.relationship('JobPosting', backref='recruiter')
    candidate_profile = db.relationship('CandidateProfile', backref='user', uselist=False)
    recruiter_profile = db.relationship('RecruiterProfile', backref='user', uselist=False)

class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    github_username = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    bio = db.Column(db.Text)
    years_of_experience = db.Column(db.Integer)
    education = db.Column(db.JSON)  # Store education history as JSON
    skills = db.Column(db.JSON)  # Store skills as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RecruiterProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(200))
    position = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    bio = db.Column(db.Text)
    company_website = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)  # Store the extracted text from the resume
    skills = db.Column(db.JSON)  # Store extracted skills as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.JSON)  # Store required skills as JSON
    location = db.Column(db.String(200))
    salary_range = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='job_posting')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, accepted, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    match_score = db.Column(db.Float)  # Store the matching score 