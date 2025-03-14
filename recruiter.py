from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, JobPosting, Application, Resume, User
import json

recruiter = Blueprint('recruiter', __name__)

@recruiter.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'recruiter':
        flash('Access denied. Please log in as a recruiter.')
        return redirect(url_for('auth.logout'))
    
    job_postings = JobPosting.query.filter_by(recruiter_id=current_user.id).all()
    return render_template('recruiter/dashboard.html', job_postings=job_postings)

@recruiter.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills').split(',')
        location = request.form.get('location')
        salary_range = request.form.get('salary_range')
        
        job = JobPosting(
            recruiter_id=current_user.id,
            title=title,
            company=company,
            description=description,
            required_skills=required_skills,
            location=location,
            salary_range=salary_range
        )
        
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!')
        return redirect(url_for('recruiter.dashboard'))
    
    return render_template('recruiter/post_job.html')

@recruiter.route('/applications/<int:job_id>')
@login_required
def view_applications(job_id):
    job = JobPosting.query.get_or_404(job_id)
    if job.recruiter_id != current_user.id:
        return redirect(url_for('recruiter.dashboard'))
    
    applications = Application.query.filter_by(job_posting_id=job_id).all()
    return render_template('recruiter/applications.html', job=job, applications=applications)

@recruiter.route('/update-application-status/<int:application_id>', methods=['POST'])
@login_required
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    job = application.job_posting
    
    if job.recruiter_id != current_user.id:
        return redirect(url_for('recruiter.dashboard'))
    
    new_status = request.form.get('status')
    if new_status in ['pending', 'reviewed', 'accepted', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated successfully!')
    
    return redirect(url_for('recruiter.view_applications', job_id=job.id))

@recruiter.route('/view-resume/<int:application_id>')
@login_required
def view_resume(application_id):
    application = Application.query.get_or_404(application_id)
    job = application.job_posting
    
    if job.recruiter_id != current_user.id:
        return redirect(url_for('recruiter.dashboard'))
    
    resume = Resume.query.filter_by(user_id=application.candidate_id).first()
    if not resume:
        flash('Resume not found')
        return redirect(url_for('recruiter.view_applications', job_id=job.id))
    
    return render_template('recruiter/view_resume.html', resume=resume, application=application) 