import re
import spacy
import fitz  # PyMuPDF for PDF text extraction
import os
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import pdfplumber

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
    """Extract text from a PDF file using pdfplumber for better text extraction."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
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
            if term.lower() in text:  # Convert term to lowercase for case-insensitive matching
                extracted_keywords.add(tech)  # Add the tech stack term as a keyword
    return extracted_keywords

def search_terms_in_text(text, terms):
    """Search for terms in the given text (recruiter skills).
    Both text and terms are converted to lowercase for case-insensitive matching."""
    found_terms = []
    text = text.lower()  # Convert text to lowercase for case-insensitive matching
    for term in terms:
        if term.lower() in text:  # Convert term to lowercase for comparison
            found_terms.append(term)
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

def process_resume_for_qa(resume_text, api_key):
    """
    Process resume text for question answering using LangChain and vector embeddings.
    
    Args:
        resume_text (str): The extracted text from the resume
        api_key (str): Google Gemini API key
        
    Returns:
        tuple: (vector_store, model) for question answering
    """
    try:
        # Validate API key format
        if not api_key or not api_key.startswith('AIza'):
            print("Error: Invalid API key format")
            return None, None

        # Validate resume text
        if not resume_text or not isinstance(resume_text, str):
            print("Error: Invalid resume text")
            return None, None

        print("Initializing Gemini model...")
        # Try the newer Google AI client approach first
        try:
            from google import genai
            
            # Configure the client
            genai.configure(api_key=api_key)
            
            # Test the connection with a simple request
            print("Testing API connection...")
            model = genai.GenerativeModel('gemini-1.0-pro')
            response = model.generate_content("Hello")
            print(f"API connection test successful: {response.text}")
            
            # Since we're using a different client library, we'll still initialize the LangChain model
            # as it's needed for the chain creation later
            model = GoogleGenerativeAI(
                model="gemini-1.0-pro",
                google_api_key=api_key,
                temperature=0.7,
                max_output_tokens=2048,
                top_p=0.8,
                top_k=40,
                convert_system_message_to_human=True
            )
        except Exception as e:
            print(f"Error with new Google AI client: {str(e)}")
            print("Falling back to LangChain GoogleGenerativeAI...")
            model = GoogleGenerativeAI(
                model="gemini-1.0-pro",
                google_api_key=api_key,
                temperature=0.7,
                max_output_tokens=2048,
                top_p=0.8,
                top_k=40,
                convert_system_message_to_human=True
            )
        
        print("Splitting resume text into chunks...")
        # Split the resume text into smaller chunks for better processing
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        documents = text_splitter.create_documents([resume_text])
        print(f"Created {len(documents)} chunks")
        
        # Try using the direct Google AI embeddings API first
        try:
            print("Attempting direct Google AI embeddings...")
            from google import genai
            
            # Create a simple embedding function that uses the Google AI client directly
            class DirectGoogleAIEmbeddings:
                def __init__(self, api_key):
                    self.client = genai.configure(api_key=api_key)
                    self.embedding_model = "models/embedding-001"
                
                def embed_documents(self, texts):
                    results = []
                    for text in texts:
                        result = genai.embed_content(
                            model=self.embedding_model,
                            content=text,
                            task_type="retrieval_document"
                        )
                        results.append(result["embedding"])
                    return results
                
                def embed_query(self, text):
                    result = genai.embed_content(
                        model=self.embedding_model,
                        content=text,
                        task_type="retrieval_query"
                    )
                    return result["embedding"]
            
            embeddings = DirectGoogleAIEmbeddings(api_key)
            # Test the embedding with a simple text
            test_embed = embeddings.embed_query("Test")
            print(f"Direct embeddings test successful")
        except Exception as e:
            print(f"Direct Google AI embeddings failed: {str(e)}")
            print("Falling back to LangChain GoogleGenerativeAIEmbeddings...")
            
            # Create embeddings with enhanced retry logic
            max_retries = 5  # Increased retries
            retry_delay = 5  # Increased delay between retries
            last_error = None
            
            print("Creating embeddings with LangChain...")
            for attempt in range(max_retries):
                try:
                    import socket
                    import time
                    
                    # Try to resolve DNS before creating embeddings
                    print(f"Attempt {attempt + 1}: Checking DNS resolution...")
                    host = "generativelanguage.googleapis.com"
                    try:
                        print(f"Resolving {host}...")
                        ip = socket.gethostbyname(host)
                        print(f"Successfully resolved {host} to {ip}")
                    except socket.gaierror as e:
                        print(f"DNS resolution failed: {str(e)}")
                        if attempt < max_retries - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 1.5  # Exponential backoff
                            continue
                        else:
                            raise Exception(f"DNS resolution failed after {max_retries} attempts")
                    
                    embeddings = GoogleGenerativeAIEmbeddings(
                        model="models/embedding-001",
                        google_api_key=api_key,
                        max_retries=3,
                        timeout=30,
                        request_timeout=30
                    )
                    print("LangChain embeddings created successfully")
                    break
                except Exception as e:
                    last_error = e
                    print(f"Embedding attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 1.5  # Exponential backoff
                    else:
                        raise last_error
        
        print("Creating vector store...")
        # Create vector store with persistence and error handling
        try:
            vector_store = Chroma.from_documents(
                documents,
                embedding=embeddings,
                persist_directory="chroma_db",
                collection_name="resume_qa"
            )
            vector_store.persist()
            print("Vector store created and persisted successfully")
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            raise
        
        return vector_store, model
    except Exception as e:
        print(f"Error processing resume for QA: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

def ask_resume_question(resume_text, question, api_key):
    """
    Ask a question about a resume using LangChain and vector embeddings.
    
    Args:
        resume_text (str): The extracted text from the resume
        question (str): The question to ask about the resume
        api_key (str): Google Gemini API key
        
    Returns:
        str: The response from the model or an error message
    """
    try:
        # Validate inputs
        if not resume_text or not isinstance(resume_text, str):
            return "Error: Invalid resume text provided"
        if not question or not isinstance(question, str):
            return "Error: Invalid question provided"
        if not api_key or not api_key.startswith('AIza'):
            return "Error: Invalid API key format"

        print("Processing resume for QA...")
        # Process the resume for QA
        vector_store, model = process_resume_for_qa(resume_text, api_key)
        if not vector_store or not model:
            return "Error: Failed to process resume for question answering."
        
        print("Creating prompt template...")
        # Create the prompt template with more specific instructions
        prompt = ChatPromptTemplate.from_template("""
        You are an expert HR professional analyzing a candidate's resume.
        Based on the resume content provided, please answer the following question.
        If the information is not available in the resume, please indicate that.
        Be specific and concise in your response.
        Focus only on information that is explicitly mentioned in the resume.
        
        Resume Content:
        {context}
        
        Question: {question}
        
        Answer:
        """)
        
        print("Creating document chain...")
        # Create the document chain with optimized settings
        document_chain = create_stuff_documents_chain(
            model, 
            prompt,
            callbacks=None,
            timeout=60  # Increased timeout
        )
        
        print("Creating retrieval chain...")
        # Create the retrieval chain with optimized settings
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 2,  # Reduced number of chunks
                "score_threshold": 0.5  # Only retrieve relevant chunks
            }
        )
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        print("Getting response...")
        # Get the response with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} of {max_retries}")
                response = retrieval_chain.invoke({
                    'question': question,
                    'context': retriever.invoke(question)
                })
                print("Response received successfully")
                return response['answer']
            except Exception as e:
                print(f"Query attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                print(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in ask_resume_question: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        if "api key" in error_msg.lower():
            return "Error: Invalid or missing API key. Please check your configuration."
        elif "timeout" in error_msg.lower():
            return "Error: The request timed out. Please try again with a more specific question."
        elif "dns" in error_msg.lower():
            return "Error: Network connectivity issue. Please check your internet connection and try again."
        else:
            return f"Error querying resume: {error_msg}" 