import re
import spacy
import fitz  # PyMuPDF for PDF text extraction
import os

# Load spaCy NLP model (for general text cleaning)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Define a dictionary of technology stacks (with variations) to extract keywords from the resume
tech_stack_dict = {
    # Frontend Technologies
    'React': ['react', 'reactjs', 'react.js', 'reactjs.js'],
    'Angular': ['angular', 'angularjs', 'angular.js', 'ng'],
    'Vue': ['vue', 'vuejs', 'vue.js'],
    'Svelte': ['svelte', 'sveltejs', 'svelte.js'],
    'Bootstrap': ['bootstrap', 'bootstrap4', 'bootstrap5', 'bootstrap3'],
    'Tailwind': ['tailwind', 'tailwindcss', 'tailwind.css'],
    
    # JavaScript Frameworks and Libraries
    'Node.js': ['node', 'nodejs', 'node.js'],
    'Express': ['express'],
    'jQuery': ['jquery', 'jquery.js'],
    'Ember.js': ['ember', 'emberjs', 'ember.js'],
    'Backbone.js': ['backbone', 'backbonejs', 'backbone.js'],
    'Knockout.js': ['knockout', 'knockoutjs', 'knockout.js'],
    
    # CSS Preprocessors and Tools
    'Sass': ['sass', 'scss'],
    'Less': ['less'],
    'PostCSS': ['postcss'],
    'CSS3': ['css3', 'css3.0'],
    'CSS': ['css', 'css2', 'css3'],
    
    # HTML/CSS/JS Compilers and Bundlers
    'Webpack': ['webpack'],
    'Babel': ['babel'],
    'Parcel': ['parcel'],
    'Rollup': ['rollup'],
    
    # Backend Technologies
    'Python': ['python', 'py'],
    'Django': ['django', 'django1', 'django2'],
    'Flask': ['flask', 'flask.py'],
    'FastAPI': ['fastapi'],
    'Ruby': ['ruby', 'rubyonrails', 'rails'],
    'PHP': ['php', 'php7', 'php8'],
    'Java': ['java', 'jdk', 'jre'],
    'Spring': ['spring', 'springboot', 'spring-framework'],
    'C#': ['csharp', 'c#'],
    'ASP.NET': ['asp.net', 'aspnet'],
    
    # Databases
    'MySQL': ['mysql', 'mysql5', 'mysql8'],
    'PostgreSQL': ['postgresql', 'postgres'],
    'MongoDB': ['mongodb', 'mongo', 'mongod'],
    'SQLite': ['sqlite'],
    'Redis': ['redis'],
    'Cassandra': ['cassandra'],
    'MariaDB': ['mariadb'],
    'Oracle DB': ['oracle', 'oracle db', 'oracle database'],
    
    # Cloud and DevOps
    'AWS': ['aws', 'amazon web services', 'amazon cloud'],
    'Azure': ['azure', 'microsoft azure'],
    'Google Cloud': ['google cloud', 'gcp'],
    'Docker': ['docker'],
    'Kubernetes': ['kubernetes', 'k8s'],
    'Jenkins': ['jenkins'],
    'Terraform': ['terraform'],
    'CI/CD': ['ci/cd', 'continuous integration', 'continuous delivery'],
    'Ansible': ['ansible'],
    'Chef': ['chef'],
    'Puppet': ['puppet'],
    
    # Mobile Development
    'React Native': ['react native', 'reactnative', 'react-native'],
    'Flutter': ['flutter'],
    'Swift': ['swift'],
    'Kotlin': ['kotlin'],
    'Xamarin': ['xamarin'],
    
    # Data Science and Machine Learning
    'TensorFlow': ['tensorflow', 'tf'],
    'PyTorch': ['pytorch', 'torch'],
    'Scikit-learn': ['scikit-learn', 'sklearn'],
    'Pandas': ['pandas'],
    'NumPy': ['numpy'],
    'Matplotlib': ['matplotlib'],
    'Keras': ['keras'],
    'OpenCV': ['opencv'],
    'SciPy': ['scipy'],
    'NLTK': ['nltk'],
    'SpaCy': ['spacy'],
    
    # Testing Frameworks
    'Jest': ['jest'],
    'Mocha': ['mocha'],
    'Chai': ['chai'],
    'JUnit': ['junit'],
    'Selenium': ['selenium'],
    'Cypress': ['cypress'],
    
    # Version Control
    'Git': ['git'],
    'GitHub': ['github'],
    'GitLab': ['gitlab'],
    'Bitbucket': ['bitbucket'],
    
    # Miscellaneous Technologies
    'GraphQL': ['graphql'],
    'REST': ['rest', 'restful'],
    'WebSocket': ['websocket'],
    'gRPC': ['grpc'],
    'Socket.io': ['socket.io', 'socketio'],
    'OAuth': ['oauth', 'oauth2'],
    'JWT': ['jwt'],
    
    # UI/UX Tools
    'Figma': ['figma'],
    'Adobe XD': ['adobe xd', 'xd'],
    'Sketch': ['sketch'],
    'InVision': ['invision'],
    
    # NoSQL Databases
    'Firebase': ['firebase'],
    'CouchDB': ['couchdb'],
    'DynamoDB': ['dynamodb'],
    
    # Big Data and Analytics
    'Hadoop': ['hadoop'],
    'Spark': ['spark'],
    'Kafka': ['kafka'],
    'Elasticsearch': ['elasticsearch'],
    'Solr': ['solr'],
}

def clean_text(text):
    """Clean the extracted text by removing non-ASCII characters and normalizing whitespace."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
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

def extract_social_links(text):
    """Extract social media links (GitHub, LinkedIn, Twitter, etc.) from the text."""
    # Regex patterns for social media links
    github_pattern = r'https?://(www\.)?github\.com/[a-zA-Z0-9_-]+'
    linkedin_pattern = r'https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    twitter_pattern = r'https?://(www\.)?twitter\.com/[a-zA-Z0-9_]+'
    
    # Extract links
    github_links = re.findall(github_pattern, text)
    linkedin_links = re.findall(linkedin_pattern, text)
    twitter_links = re.findall(twitter_pattern, text)
    
    # Return a dictionary of social links
    social_links = {
        'GitHub': github_links,
        'LinkedIn': linkedin_links,
        'Twitter': twitter_links,
    }
    return social_links

def extract_keywords_from_resume(text, tech_stack_dict):
    """Extract keywords from the resume based on the tech stack dictionary."""
    extracted_keywords = set()
    text = text.lower()
    
    # Check for the tech stack terms in the resume text
    for tech, terms in tech_stack_dict.items():
        for term in terms:
            if term.lower() in text:
                extracted_keywords.add(tech)  # Add the tech stack term as a keyword
    return extracted_keywords

def search_terms_in_text(text, terms):
    """Search for terms in the given text (recruiter skills)."""
    text = text.lower()
    found_terms = [term for term in terms if term.lower() in text]
    return found_terms

def calculate_score(found_terms, total_terms):
    """Calculate a score based on the matched recruiter skills."""
    if not total_terms:
        return 0
    matched_count = len(found_terms)
    score = (matched_count / len(total_terms)) * 100 if len(total_terms) > 0 else 0
    return round(score, 2)

def process_resumes(directory, recruiter_skills):
    """Process all resume PDFs in the given directory and rank them based on skills."""
    resume_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    resume_scores = []

    # Process each resume
    for file in resume_files:
        file_path = os.path.join(directory, file)

        # Extract text from the PDF
        resume_text = extract_text_from_pdf(file_path)

        if resume_text.strip():
            # Extract keywords from the resume using the tech stack dictionary
            extracted_keywords = extract_keywords_from_resume(resume_text, tech_stack_dict)

            # Extract social media links
            social_links = extract_social_links(resume_text)

            # Search for recruiter skills in the extracted keywords
            matched_terms = search_terms_in_text(" ".join(extracted_keywords), recruiter_skills)

            # Calculate the score for the resume based on the matched recruiter skills
            score = calculate_score(matched_terms, recruiter_skills)

            resume_scores.append({
                'filename': file, 
                'score': score, 
                'keywords': sorted(list(extracted_keywords)), 
                'matched_skills': matched_terms, 
                'social_links': social_links
            })

    # Sort the resumes by score in descending order
    resume_scores.sort(key=lambda x: x['score'], reverse=True)
    return resume_scores 