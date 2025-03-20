import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Use strong secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'resume_ranking_secret_key'
    
    # Database configuration
    # Using SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///resume_platform.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Production settings
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    TESTING = False
    
    # Google Gemini API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Security settings for production
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True 