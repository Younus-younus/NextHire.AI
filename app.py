from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import joblib
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
import PyPDF2
import docx
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# File paths
MODEL_FILE = "logistic_model.pkl"
VECTORIZER_FILE = "tfidf_vectorizer.pkl"
ENCODER_FILE = "label_encoder.pkl"
UPLOAD_FOLDER = "uploads"

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load models
model = None
tfidf_vectorizer = None
label_encoder = None
STOP_WORDS = None

# Job role skill sets for skill matching
JOB_SKILLS = {
    'Data Science': ['python', 'machine learning', 'ml', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'data analysis', 'statistics', 'sql'],
    'Python Developer': ['python', 'django', 'flask', 'fastapi', 'rest api', 'postgresql', 'mongodb', 'git', 'docker'],
    'Java Developer': ['java', 'spring', 'hibernate', 'maven', 'junit', 'sql', 'rest api', 'microservices'],
    'Web Designing': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'ui', 'ux', 'figma', 'photoshop'],
    'Machine Learning Engineer': ['python', 'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'nlp', 'computer vision', 'ml ops'],
    'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'ci cd', 'terraform', 'ansible', 'linux'],
    'Full Stack Developer': ['javascript', 'react', 'node', 'express', 'mongodb', 'sql', 'html', 'css', 'git', 'rest api'],
    'Data Scientist': ['python', 'r', 'machine learning', 'statistics', 'pandas', 'numpy', 'visualization', 'sql', 'deep learning'],
    'Frontend Developer': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'typescript', 'webpack', 'sass'],
    'Backend Developer': ['python', 'java', 'node', 'sql', 'mongodb', 'rest api', 'microservices', 'redis', 'docker'],
    'Business Analyst': ['sql', 'excel', 'power bi', 'tableau', 'data analysis', 'requirements', 'agile', 'jira'],
    'Cloud Engineer': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'cloud architecture', 'networking'],
    'Mobile App Developer (iOS/Android)': ['swift', 'kotlin', 'java', 'react native', 'flutter', 'ios', 'android', 'firebase'],
    'Database': ['sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'database design', 'indexing', 'optimization'],
    'Testing': ['selenium', 'junit', 'testng', 'automation', 'manual testing', 'jira', 'api testing', 'performance testing'],
    'Network Security Engineer': ['networking', 'firewall', 'vpn', 'security', 'penetration testing', 'linux', 'wireshark'],
    'Mechanical Engineer': ['autocad', 'solidworks', 'cad', 'design', 'manufacturing', 'analysis', 'mechanics'],
    'Civil Engineer': ['autocad', 'civil 3d', 'design', 'construction', 'project management', 'structural analysis'],
    'Electrical Engineering': ['circuit design', 'plc', 'matlab', 'power systems', 'control systems', 'embedded systems'],
    'SAP Developer': ['sap', 'abap', 'fiori', 'hana', 'erp', 'integration', 'modules'],
    'Hadoop': ['hadoop', 'spark', 'hive', 'pig', 'mapreduce', 'big data', 'scala', 'kafka'],
    'ETL Developer': ['etl', 'sql', 'data warehouse', 'informatica', 'talend', 'ssis', 'data integration'],
    'Blockchain': ['blockchain', 'solidity', 'ethereum', 'smart contracts', 'web3', 'cryptocurrency'],
    'HR': ['recruitment', 'hrms', 'talent acquisition', 'employee relations', 'payroll', 'compliance'],
    'Sales': ['sales', 'crm', 'salesforce', 'negotiation', 'lead generation', 'client management'],
    'BANKING': ['banking', 'finance', 'accounting', 'risk management', 'compliance', 'financial analysis'],
    'FINANCE': ['finance', 'accounting', 'financial modeling', 'excel', 'sap', 'taxation', 'audit'],
    'ACCOUNTANT': ['accounting', 'tally', 'gst', 'taxation', 'audit', 'financial reporting', 'excel'],
    'HEALTHCARE': ['healthcare', 'medical', 'patient care', 'clinical', 'nursing', 'hospital management'],
    'TEACHER': ['teaching', 'education', 'curriculum', 'lesson planning', 'classroom management'],
    'INFORMATION-TECHNOLOGY': ['it', 'technical support', 'networking', 'troubleshooting', 'windows', 'linux'],
    'DIGITAL-MEDIA': ['digital marketing', 'seo', 'social media', 'content', 'google analytics', 'advertising'],
    'DESIGNER': ['design', 'photoshop', 'illustrator', 'figma', 'ui ux', 'creative', 'branding'],
    'CONSULTANT': ['consulting', 'business analysis', 'strategy', 'project management', 'client management'],
}

# Interview questions database by role
INTERVIEW_QUESTIONS = {
    'Data Science': [
        'Explain the difference between supervised and unsupervised learning.',
        'What is overfitting and how do you prevent it?',
        'Describe a data science project you worked on from start to finish.',
        'How do you handle missing data in a dataset?',
        'What machine learning algorithms are you most familiar with?',
        'Explain the bias-variance tradeoff.',
        'How would you evaluate the performance of a classification model?',
        'What is regularization and why is it important?',
    ],
    'Python Developer': [
        'Explain the difference between list and tuple in Python.',
        'What are decorators in Python and how do you use them?',
        'Describe your experience with Django/Flask frameworks.',
        'How do you handle exceptions in Python?',
        'What is the difference between @staticmethod and @classmethod?',
        'Explain Python\'s GIL (Global Interpreter Lock).',
        'How do you optimize Python code for performance?',
        'What are Python generators and why would you use them?',
    ],
    'Java Developer': [
        'Explain the principles of Object-Oriented Programming.',
        'What is the difference between abstract class and interface in Java?',
        'Describe your experience with Spring framework.',
        'How does garbage collection work in Java?',
        'What are Java streams and lambda expressions?',
        'Explain the concept of multithreading in Java.',
        'What design patterns have you used in your projects?',
        'How do you handle exceptions in Java?',
    ],
    'Web Designing': [
        'How do you ensure your designs are responsive across devices?',
        'Explain your design process from concept to final product.',
        'What tools do you use for UI/UX design?',
        'How do you approach accessibility in web design?',
        'Describe a challenging design problem you solved.',
        'How do you balance aesthetics with usability?',
        'What are your thoughts on current web design trends?',
        'How do you collaborate with developers to implement your designs?',
    ],
    'Machine Learning Engineer': [
        'Explain the architecture of a neural network you have implemented.',
        'What is backpropagation and how does it work?',
        'Describe your experience with TensorFlow or PyTorch.',
        'How do you deploy machine learning models in production?',
        'What is transfer learning and when would you use it?',
        'Explain the difference between CNN and RNN.',
        'How do you handle imbalanced datasets?',
        'What is your approach to hyperparameter tuning?',
    ],
    'DevOps Engineer': [
        'Explain the CI/CD pipeline you have implemented.',
        'What is containerization and how does Docker work?',
        'Describe your experience with Kubernetes.',
        'How do you monitor application performance in production?',
        'What is Infrastructure as Code (IaC)?',
        'Explain the difference between horizontal and vertical scaling.',
        'How do you handle security in a DevOps environment?',
        'Describe your experience with cloud platforms (AWS/Azure/GCP).',
    ],
    'Full Stack Developer': [
        'Describe a full-stack application you built from scratch.',
        'How do you ensure communication between frontend and backend?',
        'What is RESTful API design?',
        'Explain your experience with databases (SQL/NoSQL).',
        'How do you handle authentication and authorization?',
        'What frontend frameworks are you proficient in?',
        'How do you optimize application performance?',
        'Describe your version control workflow.',
    ],
    'Frontend Developer': [
        'Explain the Virtual DOM and how React uses it.',
        'What is the difference between state and props in React?',
        'How do you ensure cross-browser compatibility?',
        'Describe your experience with responsive design.',
        'What is webpack and why is it used?',
        'How do you optimize frontend performance?',
        'Explain the concept of hooks in React.',
        'What CSS preprocessors have you worked with?',
    ],
    'Backend Developer': [
        'Explain RESTful API design principles.',
        'How do you design a scalable database schema?',
        'What is the difference between SQL and NoSQL databases?',
        'Describe your experience with microservices architecture.',
        'How do you handle API authentication and security?',
        'What caching strategies have you implemented?',
        'Explain database indexing and optimization.',
        'How do you handle concurrent requests in your applications?',
    ],
    'Data Scientist': [
        'Walk me through your approach to a new data science problem.',
        'How do you communicate complex findings to non-technical stakeholders?',
        'What statistical methods do you use most frequently?',
        'Describe a time when your analysis led to business impact.',
        'How do you validate your models?',
        'What is A/B testing and how have you used it?',
        'Explain dimensionality reduction techniques.',
        'How do you stay updated with latest developments in data science?',
    ],
    'Business Analyst': [
        'How do you gather and document business requirements?',
        'Describe your experience with data visualization tools.',
        'How do you prioritize competing stakeholder demands?',
        'What methodologies (Agile/Scrum) have you worked with?',
        'How do you measure the success of a project?',
        'Describe a time you identified a business improvement opportunity.',
        'How do you create effective business process models?',
        'What SQL queries are you comfortable writing?',
    ],
    'Cloud Engineer': [
        'Explain the shared responsibility model in cloud computing.',
        'Describe your experience with AWS/Azure/GCP services.',
        'How do you design for high availability and disaster recovery?',
        'What is serverless computing and when would you use it?',
        'How do you optimize cloud costs?',
        'Explain VPC and network security in cloud environments.',
        'What infrastructure automation tools have you used?',
        'How do you implement cloud security best practices?',
    ],
    'Testing': [
        'What is the difference between manual and automation testing?',
        'Describe your experience with Selenium or other automation tools.',
        'How do you write effective test cases?',
        'What is the testing pyramid?',
        'Explain the difference between functional and non-functional testing.',
        'How do you prioritize testing efforts?',
        'Describe your experience with API testing.',
        'What metrics do you use to measure testing effectiveness?',
    ],
    'default': [
        'Tell me about yourself and your professional background.',
        'Why are you interested in this position?',
        'Describe a challenging project you worked on.',
        'How do you stay updated with industry trends?',
        'What are your greatest strengths and weaknesses?',
        'Where do you see yourself in 5 years?',
        'How do you handle deadlines and pressure?',
        'Describe a time you worked effectively in a team.',
    ]
}


def download_nltk_data():
    """Download required NLTK data"""
    global STOP_WORDS
    try:
        STOP_WORDS = set(stopwords.words('english'))
    except LookupError:
        print("Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)
        STOP_WORDS = set(stopwords.words('english'))


def extract_skills(text):
    """Extract skills from resume text"""
    text_lower = text.lower()
    all_skills = set()
    for skills_list in JOB_SKILLS.values():
        all_skills.update(skills_list)
    
    found_skills = []
    for skill in all_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
    
    return found_skills


def calculate_skill_match(resume_skills, job_category):
    """Calculate skill match percentage between resume and job role"""
    if job_category not in JOB_SKILLS:
        return 0.0, [], []
    
    required_skills = set(JOB_SKILLS[job_category])
    resume_skills_set = set(resume_skills)
    
    matched_skills = resume_skills_set.intersection(required_skills)
    missing_skills = required_skills - resume_skills_set
    
    if len(required_skills) == 0:
        return 0.0, [], []
    
    match_percentage = (len(matched_skills) / len(required_skills)) * 100
    
    return match_percentage, list(matched_skills), list(missing_skills)


def get_job_links(role):
    """Get job application links for a specific role"""
    role_encoded = role.replace(' ', '+')
    role_underscore = role.replace(' ', '-').lower()
    
    links = []
    links.append({
        'name': 'LinkedIn',
        'url': f'https://www.linkedin.com/jobs/search/?keywords={role_encoded}',
        'icon': '💼'
    })
    links.append({
        'name': 'Indeed',
        'url': f'https://www.indeed.com/jobs?q={role_encoded}',
        'icon': '🔍'
    })
    links.append({
        'name': 'Glassdoor',
        'url': f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={role_encoded}',
        'icon': '🏢'
    })
    links.append({
        'name': 'Naukri',
        'url': f'https://www.naukri.com/{role_underscore}-jobs',
        'icon': '🇮🇳'
    })
    links.append({
        'name': 'Monster',
        'url': f'https://www.monster.com/jobs/search?q={role_encoded}',
        'icon': '👹'
    })
    links.append({
        'name': 'SimplyHired',
        'url': f'https://www.simplyhired.com/search?q={role_encoded}',
        'icon': '🎯'
    })
    
    return links


def get_interview_questions(role, resume_skills):
    """Generate interview questions based on role and resume skills"""
    questions = INTERVIEW_QUESTIONS.get(role, INTERVIEW_QUESTIONS['default']).copy()
    
    # Add skill-based questions
    skill_questions = []
    for skill in resume_skills[:5]:
        skill_lower = skill.lower()
        if 'python' in skill_lower:
            skill_questions.append(f'How would you use Python to solve {role.lower()} problems?')
        elif 'machine learning' in skill_lower or 'ml' in skill_lower:
            skill_questions.append('Describe a machine learning project you have worked on.')
        elif 'sql' in skill_lower:
            skill_questions.append('Write a complex SQL query you have used in your work.')
        elif any(fw in skill_lower for fw in ['react', 'vue', 'angular']):
            skill_questions.append(f'Explain your experience with {skill} in detail.')
        elif 'docker' in skill_lower or 'kubernetes' in skill_lower:
            skill_questions.append(f'How have you used {skill} in your projects?')
    
    all_questions = questions[:5] + skill_questions[:3]
    return all_questions[:8]


def select_best_fit_role(recommendations):
    """Select the best fit role based on combined confidence and skill match"""
    best_score = 0
    best_role = recommendations[0]
    
    for rec in recommendations:
        # Combined score: 70% confidence + 30% skill match
        combined_score = (rec['confidence'] * 0.7) + (rec['skill_match'] / 100 * 0.3)
        if combined_score > best_score:
            best_score = combined_score
            best_role = rec
    
    return best_role, best_score


def clean_text(text):
    """Clean and preprocess resume text"""
    global STOP_WORDS
    if STOP_WORDS is None:
        download_nltk_data()
    
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    words = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(words)


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def load_models():
    """Load trained models"""
    global model, tfidf_vectorizer, label_encoder
    
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"Model file '{MODEL_FILE}' not found. Please train the model first by running main.py")
    
    if not os.path.exists(VECTORIZER_FILE):
        raise FileNotFoundError(f"Vectorizer file '{VECTORIZER_FILE}' not found. Please train the model first by running main.py")
    
    if not os.path.exists(ENCODER_FILE):
        raise FileNotFoundError(f"Encoder file '{ENCODER_FILE}' not found. Please train the model first by running main.py")
    
    print("Loading trained models...")
    model = joblib.load(MODEL_FILE)
    tfidf_vectorizer = joblib.load(VECTORIZER_FILE)
    label_encoder = joblib.load(ENCODER_FILE)
    
    print("✓ Models loaded successfully")
    print(f"  - Model: Logistic Regression")
    print(f"  - Categories: {len(label_encoder.classes_)}")
    print(f"  - Features: {len(tfidf_vectorizer.vocabulary_)}")


@app.route('/')
def home():
    """Serve the home page"""
    return render_template('homePage.html')


@app.route('/screening')
def screening():
    """Serve the resume screening page"""
    return render_template('index.html')


@app.route('/resume-builder')
def resume_builder():
    """Serve the resume builder page"""
    return render_template('resume_builder.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Handle resume upload and prediction"""
    try:
        # Verify models are loaded
        if model is None or tfidf_vectorizer is None or label_encoder is None:
            return jsonify({'error': 'Models not loaded. Please restart the server.'}), 500
        
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save the uploaded file with a unique name for serving
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"resume_{int(time.time())}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Extract text based on file type
        if file_extension == 'pdf':
            resume_text = extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            resume_text = extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            resume_text = extract_text_from_txt(file_path)
        else:
            os.remove(file_path)
            return jsonify({'error': 'Unsupported file format. Please upload PDF, DOCX, or TXT'}), 400
        
        # Check if text was extracted
        if not resume_text or len(resume_text.strip()) < 50:
            os.remove(file_path)
            return jsonify({'error': 'Could not extract sufficient text from resume'}), 400
        
        # Extract skills from resume
        resume_skills = extract_skills(resume_text)
        
        # Clean and transform text
        cleaned_text = clean_text(resume_text)
        features = tfidf_vectorizer.transform([cleaned_text])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get top 3 predictions
        top_3_idx = np.argsort(probabilities)[-3:][::-1]
        top_3_categories = label_encoder.inverse_transform(top_3_idx)
        top_3_probabilities = probabilities[top_3_idx]
        
        # Prepare top 3 recommendations with skill matching
        recommendations = []
        for cat, prob in zip(top_3_categories, top_3_probabilities):
            match_pct, matched_skills, missing_skills = calculate_skill_match(resume_skills, cat)
            
            recommendations.append({
                'role': cat,
                'confidence': float(prob),
                'skill_match': float(match_pct),
                'matched_skills': matched_skills[:5],  # Top 5 matched skills
                'missing_skills': missing_skills[:5] if len(recommendations) == 0 else []  # Only for top role
            })
        
        # Select best fit role based on stats
        best_fit, best_score = select_best_fit_role(recommendations)
        
        # Get job links for top 3 roles
        job_opportunities = []
        for rec in recommendations:
            job_opportunities.append({
                'role': rec['role'],
                'links': get_job_links(rec['role'])
            })
        
        # Generate interview questions for all top 3 roles
        interview_questions_all = []
        for rec in recommendations:
            questions = get_interview_questions(rec['role'], resume_skills)
            interview_questions_all.append({
                'role': rec['role'],
                'questions': questions
            })
        
        # Prepare response with file URL for viewing
        response = {
            'primary_role': recommendations[0]['role'],
            'primary_confidence': recommendations[0]['confidence'],
            'recommendations': recommendations,
            'extracted_skills': resume_skills[:10],
            'best_fit_role': {
                'role': best_fit['role'],
                'combined_score': float(best_score * 100),
                'reason': f"Best match based on {int(best_fit['confidence']*100)}% confidence and {int(best_fit['skill_match'])}% skill match"
            },
            'job_opportunities': job_opportunities,
            'interview_prep': interview_questions_all,
            'resume_file_url': f'/uploads/{unique_filename}',  # URL to serve the file
            'resume_filename': file.filename
        }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        print(f"\n❌ Error occurred during prediction:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/uploads/<filename>')
def download_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'models_loaded': model is not None})


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Resume Screening AI Web App")
    print("=" * 60)
    
    # Download NLTK data first
    print("\nInitializing NLTK data...")
    download_nltk_data()
    print("✓ NLTK data ready")
    
    # Load models
    try:
        load_models()
        print("\n" + "=" * 60)
        print("🚀 Starting server...")
        
        # Get port from environment variable (for deployment) or use 5000 for local
        port = int(os.environ.get('PORT', 5000))
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        
        if debug_mode:
            print("📱 Open your browser and go to: http://localhost:5000")
        
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease run 'python main.py' first to train the model!")
else:
    # For production (gunicorn)
    download_nltk_data()
    load_models()
