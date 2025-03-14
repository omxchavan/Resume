import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, current_user, logout_user
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from models import db, User
from auth import auth
from candidate import candidate
from recruiter import recruiter
from utils import (
    extract_text_from_pdf, extract_keywords_from_resume, tech_stack_dict,
    search_terms_in_text, calculate_score, process_resumes, extract_social_links
)
from config import Config

# Load environment variables from .flaskenv file
load_dotenv()

app = Flask(__name__)
app.secret_key = "resume_ranking_secret_key"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(candidate, url_prefix='/candidate')
app.register_blueprint(recruiter, url_prefix='/recruiter')

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page."""
    try:
        if current_user.is_authenticated:
            if current_user.user_type == 'candidate':
                return redirect(url_for('candidate.dashboard'))
            elif current_user.user_type == 'recruiter':
                return redirect(url_for('recruiter.dashboard'))
            else:
                # If user type is invalid, log them out
                logout_user()
                flash('Invalid user type. Please login again.')
                return render_template('index.html')
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f'Error in index route: {str(e)}')
        return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle resume file uploads."""
    try:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('results', file_path=file_path))
        flash('Invalid file type')
        return redirect(request.url)
    except Exception as e:
        app.logger.error(f'Error in upload_file route: {str(e)}')
        flash('An error occurred while uploading the file.')
        return redirect(request.url)

@app.route('/results', methods=['GET', 'POST'])
def results():
    """Handle skill input and display ranking results."""
    try:
        file_path = request.args.get('file_path')
        if not file_path:
            return redirect(url_for('index'))
        
        text = extract_text_from_pdf(file_path)
        keywords = extract_keywords_from_resume(text, tech_stack_dict)
        social_links = extract_social_links(text)
        
        return render_template('results.html', 
                             keywords=keywords, 
                             social_links=social_links,
                             file_path=file_path)
    except Exception as e:
        app.logger.error(f'Error in results route: {str(e)}')
        flash('An error occurred while processing the resume.')
        return redirect(url_for('index'))

@app.route('/clear', methods=['GET'])
def clear_uploads():
    """Clear all uploaded resumes."""
    try:
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
        
        flash('All resumes have been cleared')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f'Error in clear_uploads route: {str(e)}')
        flash('An error occurred while clearing uploads.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)