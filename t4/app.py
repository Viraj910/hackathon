from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Default users for demo purposes
DEFAULT_USERS = {
    'patient': {
        'admin': {'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'role': 'patient'},
        'patient1': {'password': hashlib.sha256('patient123'.encode()).hexdigest(), 'role': 'patient'},
        'test': {'password': hashlib.sha256('test'.encode()).hexdigest(), 'role': 'patient'}
    },
    'doctor': {
        'doctor': {'password': hashlib.sha256('doctor123'.encode()).hexdigest(), 'role': 'doctor'},
        'dr.smith': {'password': hashlib.sha256('smith123'.encode()).hexdigest(), 'role': 'doctor'},
        'admin': {'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'role': 'doctor'}
    }
}

def authenticate_user(username, password, user_type):
    """Authenticate user credentials"""
    if user_type not in DEFAULT_USERS:
        return False
    
    if username not in DEFAULT_USERS[user_type]:
        return False
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return DEFAULT_USERS[user_type][username]['password'] == hashed_password

def require_login(user_type=None):
    """Decorator to require login for routes"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'logged_in' not in session:
                if user_type == 'patient':
                    return redirect(url_for('patient_login'))
                elif user_type == 'doctor':
                    return redirect(url_for('doctor_login'))
                else:
                    return redirect(url_for('login_choice'))
            
            if user_type and session.get('user_type') != user_type:
                flash('Access denied. Please login with appropriate credentials.', 'error')
                if user_type == 'patient':
                    return redirect(url_for('patient_login'))
                elif user_type == 'doctor':
                    return redirect(url_for('doctor_login'))
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# Redirect root to login choice
@app.route('/')
def home():
    """Home page that redirects to login choice"""
    return redirect(url_for('login_choice'))

# Login routes
@app.route('/login')
def login_choice():
    """Landing page to choose login type"""
    return render_template('login_choice.html')

@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    """Patient login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate_user(username, password, 'patient'):
            session['logged_in'] = True
            session['username'] = username
            session['user_type'] = 'patient'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('patient_form'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('patient_login.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate_user(username, password, 'doctor'):
            session['logged_in'] = True
            session['username'] = username
            session['user_type'] = 'doctor'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('doctor_login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login_choice'))

@app.route('/doctor/dashboard')
@require_login('doctor')
def doctor_dashboard():
    """Doctor dashboard"""
    return render_template('doctor_dashboard.html', username=session.get('username'))

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

def save_doctor_data(doctor_data):
    """Save doctor data to JSON file"""
    file_path = 'doctors.json'
    
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
    existing_data.append(doctor_data)
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

def load_doctor_data():
    """Load doctor data from JSON file"""
    file_path = 'doctors.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    else:
        return []

def update_doctor_data(doctor_id, updated_data):
    """Update specific doctor data"""
    doctors = load_doctor_data()
    
    for i, doctor in enumerate(doctors):
        if doctor.get('id') == doctor_id:
            doctors[i] = updated_data
            break
    
    # Save updated data
    with open('doctors.json', 'w') as f:
        json.dump(doctors, f, indent=2)

def delete_doctor_data(doctor_id):
    """Delete specific doctor data"""
    doctors = load_doctor_data()
    doctors = [doctor for doctor in doctors if doctor.get('id') != doctor_id]
    
    # Save updated data
    with open('doctors.json', 'w') as f:
        json.dump(doctors, f, indent=2)

@app.route('/admin/doctors')
@require_login('doctor')
def doctor_admin():
    """Doctor profile admin dashboard"""
    doctors = load_doctor_data()
    return render_template('doctor_admin.html', doctors=doctors)

@app.route('/admin/doctors/add', methods=['GET', 'POST'])
@require_login('doctor')
def add_doctor():
    """Add new doctor profile"""
    if request.method == 'POST':
        # Generate unique ID
        doctor_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get form data
        doctor_data = {
            'id': doctor_id,
            'name': request.form.get('name'),
            'specialization': request.form.get('specialization'),
            'qualification': request.form.get('qualification'),
            'experience': request.form.get('experience'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'department': request.form.get('department'),
            'schedule': request.form.get('schedule'),
            'room_number': request.form.get('room_number'),
            'consultation_fee': request.form.get('consultation_fee'),
            'bio': request.form.get('bio'),
            'languages': request.form.get('languages'),
            'status': 'active',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save doctor data
        save_doctor_data(doctor_data)
        
        return redirect(url_for('doctor_admin'))
    
    return render_template('add_doctor.html')

@app.route('/admin/doctors/edit/<doctor_id>', methods=['GET', 'POST'])
@require_login('doctor')
def edit_doctor(doctor_id):
    """Edit doctor profile"""
    doctors = load_doctor_data()
    doctor = next((d for d in doctors if d.get('id') == doctor_id), None)
    
    if not doctor:
        return redirect(url_for('doctor_admin'))
    
    if request.method == 'POST':
        # Update doctor data
        updated_data = {
            'id': doctor_id,
            'name': request.form.get('name'),
            'specialization': request.form.get('specialization'),
            'qualification': request.form.get('qualification'),
            'experience': request.form.get('experience'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'department': request.form.get('department'),
            'schedule': request.form.get('schedule'),
            'room_number': request.form.get('room_number'),
            'consultation_fee': request.form.get('consultation_fee'),
            'bio': request.form.get('bio'),
            'languages': request.form.get('languages'),
            'status': request.form.get('status'),
            'created_at': doctor.get('created_at'),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        update_doctor_data(doctor_id, updated_data)
        return redirect(url_for('doctor_admin'))
    
    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/admin/doctors/delete/<doctor_id>', methods=['POST'])
@require_login('doctor')
def delete_doctor(doctor_id):
    """Delete doctor profile"""
    delete_doctor_data(doctor_id)
    return redirect(url_for('doctor_admin'))

@app.route('/doctors')
def public_doctors():
    """Public doctor profiles page"""
    doctors = [d for d in load_doctor_data() if d.get('status') == 'active']
    return render_template('doctors.html', doctors=doctors)

@app.route('/doctors/<doctor_id>')
def doctor_profile(doctor_id):
    """Individual doctor profile page"""
    doctors = load_doctor_data()
    doctor = next((d for d in doctors if d.get('id') == doctor_id and d.get('status') == 'active'), None)
    
    if not doctor:
        return redirect(url_for('public_doctors'))
    
    return render_template('doctor_profile.html', doctor=doctor)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)