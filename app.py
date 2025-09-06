# app.py - Main Flask Application for ADHD Detection System
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import json
import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate secure secret key
app.config['UPLOAD_FOLDER'] = 'uploads'

# Database initialization
def init_db():
    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER NOT NULL,
            parent_contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Test sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            memory_score INTEGER DEFAULT 0,
            attention_score INTEGER DEFAULT 0,
            perception_score INTEGER DEFAULT 0,
            logic_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            assessment_level TEXT,
            completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Individual test results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            test_type TEXT NOT NULL,
            question_number INTEGER,
            response_time REAL,
            correct_answer BOOLEAN,
            user_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES test_sessions(id)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Helper functions for scoring
def calculate_assessment_level(total_score):
    if total_score >= 85:
        return "Low ADHD indicators", "#4CAF50", "Normal development"
    elif total_score >= 70:
        return "Mild ADHD indicators", "#8BC34A", "Monitor progress"
    elif total_score >= 55:
        return "Moderate ADHD indicators", "#FFC107", "Further evaluation recommended"
    elif total_score >= 40:
        return "High ADHD indicators", "#FF9800", "Professional assessment needed"
    else:
        return "Very High ADHD indicators", "#F44336", "Immediate professional consultation"

# Authentication decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['age'])
        parent_contact = request.form.get('parent_contact', '')

        # Validate age range
        if age < 8 or age > 12:
            flash('This assessment is designed for children aged 8-12 years.', 'error')
            return render_template('register.html')

        # Hash password
        password_hash = generate_password_hash(password)

        conn = sqlite3.connect('adhd_assessment.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, age, parent_contact)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, password_hash, age, parent_contact))
            conn.commit()
            user_id = cursor.lastrowid

            # Log user in automatically
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_age'] = age

            flash(f'Welcome {name}! Your account has been created successfully.', 'success')
            return redirect(url_for('dashboard'))

        except sqlite3.IntegrityError:
            flash('Email address already registered. Please use a different email.', 'error')
            return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('adhd_assessment.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, password_hash, age FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_age'] = user[3]

            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    # Get user's test history
    cursor.execute('''
        SELECT id, session_date, memory_score, attention_score, perception_score, 
               logic_score, total_score, assessment_level, completed
        FROM test_sessions 
        WHERE user_id = ? 
        ORDER BY session_date DESC
    ''', (session['user_id'],))

    test_history = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', test_history=test_history)

@app.route('/adhd_info')
@login_required
def adhd_info():
    info_data = {
        'symptoms': [
            "Difficulty paying attention to details",
            "Trouble staying focused on tasks",
            "Often seems not to listen",
            "Difficulty following instructions",
            "Problems organizing tasks",
            "Loses things frequently",
            "Easily distracted",
            "Forgetful in daily activities",
            "Fidgets or squirms",
            "Difficulty staying seated",
            "Talks excessively",
            "Interrupts or intrudes on others"
        ],
        'fun_facts': [
            "ADHD affects about 1 in 10 children",
            "It's not caused by too much sugar or screen time",
            "Many successful people have ADHD",
            "With proper support, children with ADHD can thrive"
        ]
    }
    return render_template('adhd_info.html', info=info_data)

@app.route('/start_test')
@login_required
def start_test():
    # Create new test session
    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO test_sessions (user_id)
        VALUES (?)
    ''', (session['user_id'],))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session['current_test_session'] = session_id
    return render_template('test_menu.html')

@app.route('/test/<test_type>')
@login_required
def test_page(test_type):
    if test_type not in ['memory', 'attention', 'perception', 'logic']:
        flash('Invalid test type.', 'error')
        return redirect(url_for('dashboard'))

    return render_template(f'test_{test_type}.html', test_type=test_type)

@app.route('/submit_test_result', methods=['POST'])
@login_required
def submit_test_result():
    if 'current_test_session' not in session:
        return jsonify({'error': 'No active test session'}), 400

    data = request.get_json()
    test_type = data.get('test_type')
    score = data.get('score', 0)
    responses = data.get('responses', [])

    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    # Update test session with score
    cursor.execute(f'''
        UPDATE test_sessions 
        SET {test_type}_score = ?
        WHERE id = ?
    ''', (score, session['current_test_session']))

    # Save individual responses
    for i, response in enumerate(responses):
        cursor.execute('''
            INSERT INTO test_results 
            (session_id, test_type, question_number, response_time, correct_answer, user_response)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['current_test_session'], test_type, i+1, 
              response.get('time', 0), response.get('correct', False), 
              str(response.get('answer', ''))))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'score': score})

@app.route('/complete_assessment')
@login_required
def complete_assessment():
    if 'current_test_session' not in session:
        flash('No active test session found.', 'error')
        return redirect(url_for('dashboard'))

    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    # Get current session scores
    cursor.execute('''
        SELECT memory_score, attention_score, perception_score, logic_score
        FROM test_sessions 
        WHERE id = ?
    ''', (session['current_test_session'],))

    scores = cursor.fetchone()
    if not scores:
        flash('Test session not found.', 'error')
        return redirect(url_for('dashboard'))

    total_score = sum(scores)
    assessment_level, color, recommendation = calculate_assessment_level(total_score)

    # Update session with final results
    cursor.execute('''
        UPDATE test_sessions 
        SET total_score = ?, assessment_level = ?, completed = TRUE
        WHERE id = ?
    ''', (total_score, assessment_level, session['current_test_session']))

    conn.commit()
    conn.close()

    # Clear current test session
    session_id = session.pop('current_test_session', None)

    return render_template('results.html', 
                         memory_score=scores[0], 
                         attention_score=scores[1],
                         perception_score=scores[2], 
                         logic_score=scores[3],
                         total_score=total_score,
                         assessment_level=assessment_level,
                         color=color,
                         recommendation=recommendation,
                         session_id=session_id)

@app.route('/download_report/<int:session_id>')
@login_required
def download_report(session_id):
    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    # Verify session belongs to current user
    cursor.execute('''
        SELECT ts.*, u.name, u.email, u.age
        FROM test_sessions ts
        JOIN users u ON ts.user_id = u.id
        WHERE ts.id = ? AND ts.user_id = ?
    ''', (session_id, session['user_id']))

    session_data = cursor.fetchone()
    if not session_data:
        flash('Report not found or access denied.', 'error')
        return redirect(url_for('dashboard'))

    # Generate PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("ADHD Assessment Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # User info
    user_info = f"Name: {session_data[9]}<br/>Age: {session_data[11]}<br/>Date: {session_data[2]}"
    story.append(Paragraph(user_info, styles['Normal']))
    story.append(Spacer(1, 12))

    # Scores table
    data = [
        ['Test Type', 'Score (out of 25)', 'Percentage'],
        ['Memory Test', str(session_data[3]), f"{(session_data[3]/25)*100:.1f}%"],
        ['Attention Test', str(session_data[4]), f"{(session_data[4]/25)*100:.1f}%"],
        ['Perception Test', str(session_data[5]), f"{(session_data[5]/25)*100:.1f}%"],
        ['Logic Test', str(session_data[6]), f"{(session_data[6]/25)*100:.1f}%"],
        ['Total Score', f"{session_data[7]} out of 100", f"{session_data[7]}%"]
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(table)
    story.append(Spacer(1, 12))

    # Assessment level
    level_text = f"Assessment Level: {session_data[8]}"
    story.append(Paragraph(level_text, styles['Heading2']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    conn.close()

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'ADHD_Report_{session_data[9]}_{session_data[2][:10]}.pdf',
        mimetype='application/pdf'
    )

@app.route('/profile')
@login_required
def profile():
    conn = sqlite3.connect('adhd_assessment.db')
    cursor = conn.cursor()

    # Get user info and statistics
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user_info = cursor.fetchone()

    # Get test statistics
    cursor.execute('''
        SELECT COUNT(*) as total_tests,
               AVG(total_score) as avg_score,
               MAX(total_score) as best_score,
               MIN(total_score) as lowest_score
        FROM test_sessions 
        WHERE user_id = ? AND completed = TRUE
    ''', (session['user_id'],))

    stats = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user_info, stats=stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
