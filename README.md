# Resume Platform

A Flask-based web application that connects job seekers with recruiters, featuring automated resume screening and job matching capabilities.

## Features

### For Job Seekers

- Upload and manage your resume
- Browse available job postings
- Apply to jobs with automatic skill matching
- Track application status
- View match scores for your applications

### For Recruiters

- Post new job openings
- View and manage applications
- Screen resumes with automated skill matching
- Track application status
- Compare candidate skills with job requirements

## Setup Instructions

1. Clone the repository:

```bash
git clone <repository-url>
cd resume-platform
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Download the spaCy model:

```bash
python -m spacy download en_core_web_sm
```

5. Initialize the database:

```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:

```bash
python app.py
```

7. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
resume-platform/
├── app.py              # Main application file
├── models.py           # Database models
├── auth.py            # Authentication routes
├── candidate.py       # Candidate-specific routes
├── recruiter.py       # Recruiter-specific routes
├── requirements.txt   # Project dependencies
├── uploads/           # Directory for uploaded resumes
└── templates/         # HTML templates
    ├── base.html
    ├── auth/
    ├── candidate/
    └── recruiter/
```

## Technologies Used

- Flask: Web framework
- SQLAlchemy: Database ORM
- Flask-Login: User authentication
- spaCy: Natural Language Processing
- PyMuPDF: PDF text extraction
- Bootstrap: Frontend framework

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
