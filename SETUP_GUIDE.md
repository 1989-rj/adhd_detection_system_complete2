# ADHD Detection System - Complete Setup Guide

## 🎯 Project Overview
This is a comprehensive web-based ADHD detection system designed specifically for children aged 8-12. The system includes:
- User registration and authentication
- Educational content about ADHD
- Four interactive cognitive tests (Memory, Attention, Perception, Logic)
- Automatic scoring using psychological scales
- PDF report generation
- Progress tracking and history

## 🚀 Installation Steps

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser

### 1. Extract Project Files
Extract the `adhd_detection_system` folder to your desired location.

### 2. Install Dependencies
Open a terminal/command prompt in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the System
Open your web browser and go to: `http://localhost:5000`

## 📁 Project Structure
```
adhd_detection_system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project overview
├── SETUP_GUIDE.md        # This setup guide
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── register.html     # User registration
│   ├── login.html        # User login
│   ├── dashboard.html    # Main dashboard
│   ├── adhd_info.html    # ADHD information
│   ├── test_menu.html    # Test selection
│   ├── test_memory.html  # Memory test
│   ├── test_attention.html # Attention test
│   ├── test_perception.html # Perception test
│   ├── test_logic.html   # Logic test
│   ├── results.html      # Test results
│   └── profile.html      # User profile
├── static/               # Static files (created automatically)
└── uploads/              # File uploads (created automatically)
```

## 🎮 How to Use

### 1. Registration
- Visit the homepage
- Click "Start Playing!"
- Fill in your details (name, email, age 8-12, password)
- Add parent's email (optional)

### 2. Learn About ADHD
- Click "Learn About ADHD" on the dashboard
- Read child-friendly information about ADHD
- Learn fun facts and understand symptoms

### 3. Take Tests
- Click "Take Brain Tests" on the dashboard
- Complete all four tests:
  - **Memory Test**: Remember color sequences
  - **Attention Test**: Click only blue circles
  - **Perception Test**: Find patterns and differences
  - **Logic Test**: Solve puzzles and sequences

### 4. View Results
- See your scores for each test
- Get an overall assessment level
- Download PDF report
- Track progress over time

## 🧠 Understanding the Tests

### Memory Test (25 points)
- Tests working memory and sequence recall
- 5 levels of increasing difficulty
- Score: 5 points per correct level

### Attention Test (25 points)
- Tests sustained attention and focus
- 60-second duration
- Score: +5 for correct clicks, -1 for wrong clicks

### Perception Test (25 points)
- Tests visual perception and pattern recognition
- 10 multiple-choice questions
- Score: 2.5 points per correct answer

### Logic Test (25 points)
- Tests logical reasoning and problem-solving
- 10 logic puzzles
- Score: 2.5 points per correct answer

## 📊 Scoring System

| Score Range | Assessment Level | Recommendation |
|-------------|------------------|----------------|
| 85-100 | Low ADHD indicators | Normal development |
| 70-84 | Mild ADHD indicators | Monitor progress |
| 55-69 | Moderate ADHD indicators | Further evaluation recommended |
| 40-54 | High ADHD indicators | Professional assessment needed |
| 0-39 | Very High ADHD indicators | Immediate professional consultation |

## 🔒 Security Features
- Secure password hashing
- Session management
- Age validation (8-12 years only)
- Data stored locally in SQLite database

## 🚨 Troubleshooting

### Common Issues
1. **"Module not found" errors**: Run `pip install -r requirements.txt`
2. **Port already in use**: Stop other Flask applications or change port in app.py
3. **Database errors**: Delete `adhd_assessment.db` file and restart

### Getting Help
- Check the console for error messages
- Ensure Python 3.8+ is installed
- Verify all dependencies are installed
- Make sure you're in the correct directory

## ⚠️ Important Medical Disclaimer
This system is for educational and screening purposes only. It should NOT be used as a replacement for professional medical diagnosis. Results should always be discussed with qualified healthcare professionals.

## 🔄 Updates and Maintenance
- Database is created automatically on first run
- Test scores and user data are stored locally
- Regular backups of the database are recommended

---
**Version**: 1.0.0
**Last Updated**: August 2025
**Support**: Check the README.md for troubleshooting tips