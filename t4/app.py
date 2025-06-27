from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Simple user database (in production, use a proper database)
USERS = {
    'patients': {
        'patient1': 'pass123',
        'john_doe': 'patient123',
        'jane_smith': 'mypass456'
    },
    'doctors': {
        'dr_smith': 'doctor123',
        'dr_johnson': 'medical456',
        'admin': 'admin123'
    }
}

def require_login(role=None):
    """Decorator to require login for certain routes"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login_choice'))
            
            if role and session.get('user_role') != role:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('login_choice'))
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/')
def index():
    """Homepage displaying main features"""
    return render_template('homepage.html')

@app.route('/login-choice')
def login_choice():
    """Page to choose between patient and doctor login"""
    return render_template('login_choice.html')

@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    """Patient login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS['patients'] and USERS['patients'][username] == password:
            session['user_id'] = username
            session['user_role'] = 'patient'
            session['user_name'] = username.replace('_', ' ').title()
            flash(f'Welcome back, {session["user_name"]}!', 'success')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('patient_login.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS['doctors'] and USERS['doctors'][username] == password:
            session['user_id'] = username
            session['user_role'] = 'doctor'
            session['user_name'] = username.replace('_', ' ').title()
            flash(f'Welcome back, Dr. {session["user_name"]}!', 'success')
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('doctor_login.html')

@app.route('/patient/dashboard')
@require_login('patient')
def patient_dashboard():
    """Patient dashboard - redirects to form"""
    return redirect(url_for('patient_form'))

@app.route('/doctor/dashboard')
@require_login('doctor')
def doctor_dashboard():
    """Doctor dashboard"""
    return render_template('doctor_dashboard.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye, {user_name}! You have been logged out.', 'info')
    return redirect(url_for('login_choice'))

@app.route('/patient/form', methods=['GET', 'POST'])
@require_login('patient')
def patient_form():
    if request.method == 'POST':
        # Get form data
        data = request.form.to_dict()
        
        # Combine emergency contact fields for compatibility with admin view
        emergency_parts = []
        if data.get('emergencyName'):
            emergency_parts.append(data.get('emergencyName'))
        if data.get('emergencyPhone'):
            emergency_parts.append(data.get('emergencyPhone'))
        if data.get('emergencyRelation'):
            emergency_parts.append(f"({data.get('emergencyRelation')})")
        
        if emergency_parts:
            data['emergency_contact'] = ' '.join(emergency_parts)
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to JSON file (optional)
        save_form_data(data)
        
        return render_template('ai_success.html', data=data)
    
    return render_template('ai_form.html')

@app.route('/legacy', methods=['GET', 'POST'])
@require_login('patient')
def legacy_form():
    """Legacy form for comparison"""
    if request.method == 'POST':
        # Get form data
        data = request.form.to_dict()
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to JSON file (optional)
        save_form_data(data)
        
        return render_template('success.html', data=data)
    
    return render_template('form.html')

def save_form_data(data):
    """Save form data to JSON file"""
    file_path = 'form_data.json'
    
    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    
    # Add new entry
    existing_data.append(data)
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

@app.route('/view_submissions')
@require_login('doctor')
def view_submissions():
    """View all form submissions (admin view)"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    return render_template('admin.html', submissions=data)

@app.route('/doctor/patients')
@require_login('doctor')
def patient_management():
    """Patient management page for doctors"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # Calculate statistics
    total_patients = len(data)
    this_month = len([d for d in data if d.get('timestamp', '').startswith('2025-06')])
    male_patients = len([d for d in data if d.get('gender', '').lower() == 'male'])
    female_patients = len([d for d in data if d.get('gender', '').lower() == 'female'])
    
    stats = {
        'total_patients': total_patients,
        'this_month': this_month,
        'male_patients': male_patients,
        'female_patients': female_patients
    }
    
    return render_template('patient_management.html', patients=data, stats=stats)

@app.route('/doctor/reports')
@require_login('doctor')
def reports():
    """Medical reports page for doctors"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # Generate basic statistics
    total_patients = len(data)
    recent_submissions = len([d for d in data if d.get('timestamp', '').startswith('2025-06')])
    
    # Count by gender
    gender_stats = {}
    for patient in data:
        gender = patient.get('gender', 'unknown')
        gender_stats[gender] = gender_stats.get(gender, 0) + 1
    
    # Count by age groups
    age_groups = {'0-18': 0, '19-35': 0, '36-60': 0, '60+': 0}
    for patient in data:
        age = patient.get('age')
        if age:
            try:
                age = int(age)
                if age <= 18:
                    age_groups['0-18'] += 1
                elif age <= 35:
                    age_groups['19-35'] += 1
                elif age <= 60:
                    age_groups['36-60'] += 1
                else:
                    age_groups['60+'] += 1
            except ValueError:
                pass
    
    stats = {
        'total_patients': total_patients,
        'recent_submissions': recent_submissions,
        'gender_stats': gender_stats,
        'age_groups': age_groups
    }
    
    return render_template('reports.html', stats=stats, patients=data)

@app.route('/doctor/settings')
@require_login('doctor')
def settings():
    """System settings page for doctors"""
    return render_template('settings.html')

@app.route('/doctor/patient/<int:patient_id>')
@require_login('doctor')
def patient_detail(patient_id):
    """View detailed information for a specific patient"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    if patient_id < len(data):
        patient = data[patient_id]
        return render_template('patient_detail.html', patient=patient, patient_id=patient_id)
    else:
        flash('Patient not found', 'error')
        return redirect(url_for('patient_management'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)