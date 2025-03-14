from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from models import db, Resume, JobPosting, Application
from utils import extract_text_from_pdf, extract_keywords_from_resume, tech_stack_dict

candidate = Blueprint('candidate', __name__)

@candidate.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'candidate':
        flash('Access denied. This page is for candidates only.')
        return redirect(url_for('auth.logout'))
    
    resume = Resume.query.filter_by(user_id=current_user.id).first()
    applications = Application.query.filter_by(candidate_id=current_user.id).all()
    return render_template('candidate/dashboard.html', resume=resume, applications=applications)

@candidate.route('/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        flash('No file selected')
        return redirect(url_for('candidate.dashboard'))
    
    file = request.files['resume']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('candidate.dashboard'))
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text and skills from resume
        text = extract_text_from_pdf(file_path)
        skills = list(extract_keywords_from_resume(text, tech_stack_dict))
        
        # Create or update resume record
        resume = Resume.query.filter_by(user_id=current_user.id).first()
        if resume:
            resume.file_path = file_path
            resume.skills = skills
        else:
            resume = Resume(
                user_id=current_user.id,
                file_path=file_path,
                skills=skills
            )
            db.session.add(resume)
        
        db.session.commit()
        flash('Resume uploaded successfully!')
    else:
        flash('Invalid file type. Please upload a PDF file.')
    
    return redirect(url_for('candidate.dashboard'))

@candidate.route('/jobs')
@login_required
def view_jobs():
    jobs = JobPosting.query.all()
    return render_template('candidate/jobs.html', jobs=jobs)

@candidate.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_for_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    resume = Resume.query.filter_by(user_id=current_user.id).first()
    
    if not resume:
        flash('Please upload your resume before applying')
        return redirect(url_for('candidate.view_jobs'))
    
    # Calculate match score
    job_skills = set(job.required_skills)
    resume_skills = set(resume.skills)
    match_score = len(job_skills.intersection(resume_skills)) / len(job_skills) * 100 if job_skills else 0
    
    # Create application
    application = Application(
        candidate_id=current_user.id,
        job_posting_id=job_id,
        match_score=match_score
    )
    db.session.add(application)
    db.session.commit()
    
    flash(f'Application submitted successfully! Match score: {match_score:.1f}%')
    return redirect(url_for('candidate.view_jobs')) 