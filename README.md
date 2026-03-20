# 🎯 NextHire.AI - Web Application

An AI-powered web application that analyzes resumes and predicts the best-matching job roles with confidence scores.

## 🌟 Features

- **Resume Upload**: Support for PDF, DOCX, and TXT formats
- **AI Predictions**: Machine learning model predicts top 3 job role matches
- **Confidence Scores**: Shows how confident the AI is about each prediction
- **Skill Matching**: Identifies matched skills and suggests skills to learn
- **Beautiful UI**: Modern, responsive design with gradient backgrounds
- **Download Report**: Export your results as a text file
- **Share Results**: Share your career match results

## 📋 Prerequisites

- Python 3.8 or higher
- Trained ML models (run `main.py` first to train)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Model (if not already trained)

```bash
python main.py
```

This will create:
- `logistic_model.pkl`
- `tfidf_vectorizer.pkl`
- `label_encoder.pkl`

### 3. Run the Web Application

```bash
python app.py
```

### 4. Open Your Browser

Navigate to: `http://localhost:5000`

## 📁 Project Structure

```
Resume Screening AI/
│
├── app.py                      # Flask backend server
├── main.py                     # ML model training script
├── requirements.txt            # Python dependencies
│
├── templates/
│   └── index.html             # Frontend HTML
│
├── static/
│   ├── style.css              # CSS styling
│   └── script.js              # JavaScript functionality
│
├── uploads/                   # Temporary file uploads (auto-created)
│
├── logistic_model.pkl         # Trained ML model
├── tfidf_vectorizer.pkl       # Text vectorizer
└── label_encoder.pkl          # Label encoder
```

## 💻 How to Use

1. **Upload Resume**: Click the upload area or drag-and-drop your resume (PDF, DOCX, or TXT)
2. **Analyze**: Click "Analyze Resume" button
3. **View Results**: See your top 3 job role matches with confidence scores
4. **Check Skills**: View matched skills and skills to learn
5. **Download/Share**: Save or share your results

## 🔧 API Endpoints

### `GET /`
Serves the main web application

### `POST /predict`
Analyzes uploaded resume

**Request**: `multipart/form-data` with file

**Response**:
```json
{
  "primary_role": "Data Scientist",
  "primary_confidence": 0.87,
  "recommendations": [
    {
      "role": "Data Scientist",
      "confidence": 0.87,
      "skill_match": 75.5,
      "matched_skills": ["python", "machine learning", "pandas"],
      "missing_skills": ["deep learning", "tensorflow"]
    }
  ],
  "extracted_skills": ["python", "sql", "machine learning"]
}
```

### `GET /health`
Health check endpoint

## 🎨 Supported File Formats

- **PDF** (.pdf)
- **Microsoft Word** (.docx)
- **Text** (.txt)

Max file size: 10MB

## 🛠️ Technologies Used

### Backend
- Flask - Python web framework
- Scikit-learn - Machine learning
- NLTK - Natural language processing
- PyPDF2 - PDF text extraction
- python-docx - Word document extraction

### Frontend
- HTML5
- CSS3 (with gradients and animations)
- Vanilla JavaScript (no frameworks)

## 📊 Model Information

The application uses:
- **Algorithm**: Logistic Regression
- **Feature Extraction**: TF-IDF Vectorization
- **Training Data**: Resume dataset with job categories
- **Outputs**: 
  - Primary job role prediction
  - Top 3 recommendations
  - Confidence scores
  - Skill matching analysis

## 🔒 Security Notes

- Files are temporarily stored and immediately deleted after processing
- No data is stored permanently on the server
- CORS enabled for cross-origin requests

## 🐛 Troubleshooting

### Models not found error
**Solution**: Run `python main.py` to train the model first

### Port already in use
**Solution**: Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### NLTK data not found
**Solution**: The app automatically downloads required NLTK data on startup

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Made with ❤️ using Flask, Machine Learning, and Modern Web Technologies**
