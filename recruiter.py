from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import db, JobPosting, Application, Resume, User, RecruiterProfile, CandidateProfile
import os
from dotenv import load_dotenv
from github_utils import get_github_user_profile, get_github_user_repos, get_github_user_languages
from utils import ask_resume_question
import google.generativeai as genai
import json
import subprocess
import shlex

load_dotenv()

recruiter = Blueprint('recruiter', __name__)

def escape_prompt(prompt):
    escaped_prompt = (
        prompt.replace('\\', '\\\\')  # Escape backslashes first
        .replace('"', '\\"')  # Escape double quotes
        .replace('\n', '\\n')  # Escape newlines
        .replace('*', '\\*')  # Escape asterisks
        .replace("'", "\\'")  # Escape single quotes
        .replace("\t", "\\t")  # Escape tabs
    )
    return escaped_prompt

# Helper function for the Gemini API
def ask_resume_question(resume_text, question, api_key):
    """
    Ask a question about a resume using Google's Gemini API via curl
    
    Args:
        resume_text (str): The extracted text from the resume
        question (str): The question to ask about the resume
        api_key (str): The Gemini API key
        
    Returns:
        str: The AI-generated answer
    """
    # Create the prompt
    prompt = f"""
    You are a helpful assistant for recruiters. 
    Based on the resume text provided below, answer the following question as accurately as possible.
    If the information is not present in the resume, clearly state that.
    dont give any astericks or symbold in ouput
    
    RESUME TEXT:
    {resume_text}
    
    QUESTION:
    {question}
    """
    
    # Escape the prompt for JSON
    escaped_prompt =escape_prompt(prompt)
    
    # Prepare the curl command - using regular strings instead of f-strings for the parts with backslashes
    curl_command = [
        "curl",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}",
        "-H", "Content-Type: application/json",
        "-X", "POST",
        "-d", f'{{"contents": [{{"parts":[{{"text": "{escaped_prompt}"}}]}}]}}'
    ]
    
    try:
        # Execute the curl command as a list of arguments
        result = subprocess.run(
            curl_command, 
            capture_output=True, 
            text=True,
            check=True
        )
        
        # Parse the JSON response
        response_data = json.loads(result.stdout)
        
        # Extract the text from the response
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            content = response_data['candidates'][0]['content']
            if 'parts' in content and len(content['parts']) > 0:
                return content['parts'][0]['text']
        
        return "Sorry, I couldn't process the resume question. Please try again."
    
    except subprocess.CalledProcessError as e:
        # If curl command fails
        error_message = f"Error executing curl command: {e.stderr}"
        return f"An error occurred: {error_message}"
    
    except json.JSONDecodeError:
        # If response is not valid JSON
        return "Error: Received invalid response from the API"
    
    except Exception as e:
        # For any other exceptions
        return f"An unexpected error occurred: {str(e)}"

@recruiter.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'recruiter':
        flash('Access denied. Please log in as a recruiter.')
        return redirect(url_for('auth.logout'))
    
    job_postings = JobPosting.query.filter_by(recruiter_id=current_user.id).all()
    profile = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('recruiter/dashboard.html', job_postings=job_postings, profile=profile)

@recruiter.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.user_type != 'recruiter':
        flash('Access denied. This page is for recruiters only.')
        return redirect(url_for('auth.logout'))
    
    profile = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        if not profile:
            profile = RecruiterProfile(user_id=current_user.id)
            db.session.add(profile)
        
        profile.company_name = request.form.get('company_name')
        profile.position = request.form.get('position')
        profile.phone = request.form.get('phone')
        profile.location = request.form.get('location')
        profile.bio = request.form.get('bio')
        profile.company_website = request.form.get('company_website')
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('recruiter.profile'))
    
    return render_template('recruiter/profile.html', profile=profile)

@recruiter.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    profile = RecruiterProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        flash('Profile not found.')
        return redirect(url_for('recruiter.dashboard'))
    return render_template('recruiter/view_profile.html', profile=profile)

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
    
    applications = Application.query.filter_by(job_posting_id=job_id).order_by(Application.match_score.desc()).all()
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

@recruiter.route('/view-github/<int:candidate_id>')
@login_required
def view_github_profile(candidate_id):
    """View a candidate's GitHub profile details"""
    if current_user.user_type != 'recruiter':
        flash('Access denied. This page is for recruiters only.')
        return redirect(url_for('auth.logout'))
    
    # Get candidate profile
    candidate_profile = CandidateProfile.query.filter_by(user_id=candidate_id).first()
    if not candidate_profile or not candidate_profile.github_username:
        flash('GitHub username not found for this candidate.')
        return redirect(url_for('recruiter.dashboard'))
    
    # Get GitHub data
    github_username = candidate_profile.github_username
    profile = get_github_user_profile(github_username)
    repos = get_github_user_repos(github_username, per_page=5)
    languages = get_github_user_languages(github_username)
    
    if not profile:
        flash('Could not fetch GitHub profile. The username may be invalid or GitHub API rate limit exceeded.')
        return redirect(url_for('recruiter.dashboard'))
    
    # Get candidate user info
    candidate_user = User.query.get(candidate_id)
    
    return render_template(
        'recruiter/github_profile.html',
        profile=profile,
        repos=repos,
        languages=languages,
        candidate=candidate_user,
        candidate_profile=candidate_profile
    )

@recruiter.route('/ask-resume/<int:application_id>', methods=['GET', 'POST'])
@login_required
def ask_resume_question_route(application_id):
    """Ask questions about a candidate's resume using AI"""
    if current_user.user_type != 'recruiter':
        flash('Access denied. This page is for recruiters only.')
        return redirect(url_for('auth.logout'))
    
    # Get the application
    application = Application.query.get_or_404(application_id)
    job = application.job_posting
    
    # Verify the recruiter has access to this application
    if job.recruiter_id != current_user.id:
        flash('Access denied. You do not have permission to view this application.')
        return redirect(url_for('recruiter.dashboard'))
    
    # Get the resume
    resume = Resume.query.filter_by(user_id=application.candidate_id).first()
    if not resume or not resume.extracted_text:
        flash('Resume text not found for this candidate.')
        return redirect(url_for('recruiter.view_applications', job_id=job.id))
    
    # Get the candidate user
    candidate = User.query.get(application.candidate_id)
    
    # Initialize answer
    answer = None
    
    # Process question if POST request
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            # Get the Gemini API key from config
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                flash('Gemini API key not configured. Please check your .env file.')
            else:
                try:
                    # Ask the question using the improved resume question-answering system
                    answer = ask_resume_question(resume.extracted_text, question, api_key)
                except Exception as e:
                    flash(f'Error processing your question: {str(e)}')
        else:
            flash('Please enter a question.')
    
    return render_template(
        'recruiter/ask_resume.html',
        resume=resume,
        application=application,
        candidate=candidate,
        job=job,
        answer=answer
    )

@recruiter.route('/api/ask-resume/<int:application_id>', methods=['POST'])
@login_required
def api_ask_resume(application_id):
    """API endpoint to ask questions about a resume"""
    if current_user.user_type != 'recruiter':
        return jsonify({'error': 'Access denied. This endpoint is for recruiters only.'}), 403
    
    # Get the application
    application = Application.query.get_or_404(application_id)
    job = application.job_posting
    
    # Verify the recruiter has access to this application
    if job.recruiter_id != current_user.id:
        return jsonify({'error': 'Access denied. You do not have permission to view this application.'}), 403
    
    # Get the resume
    resume = Resume.query.filter_by(user_id=application.candidate_id).first()
    if not resume or not resume.extracted_text:
        return jsonify({'error': 'Resume text not found for this candidate.'}), 404
    
    # Get the question from the JSON request
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided.'}), 400
    
    question = data['question'].strip()
    if not question:
        return jsonify({'error': 'Question cannot be empty.'}), 400
    
    # Get the Gemini API key from config
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'Gemini API key not configured. Please check your .env file.'}), 500
    
    try:
        # Ask the question using the improved resume question-answering system
        answer = ask_resume_question(resume.extracted_text, question, api_key)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': f'Error processing your question: {str(e)}'}), 500