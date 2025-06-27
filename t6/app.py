from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, make_response
import json
import os
import csv
from datetime import datetime, timedelta
from functools import wraps
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def convert_to_json_serializable(obj):
    """Convert objects to JSON serializable format"""
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# JSON Files Configuration
USERS_FILE = 'users_data.json'
PATIENTS_FILE = 'patients_data.json'
HOSPITALS_FILE = 'hospitals_data.json'
CONFIG_FILE = 'system_config.json'
SYSTEM_CONFIG_FILE = 'system_config.json'  # Added for clarity

# Initialize JSON storage
def ensure_json_files():
    """Ensure all JSON files exist with default data"""
    
    # Default users data
    default_users = {
        'patients': {
            'patient1': {'password': 'pass123', 'display_name': 'Patient One', 'status': 'active'},
            'john_doe': {'password': 'patient123', 'display_name': 'John Doe', 'status': 'active'},
            'jane_smith': {'password': 'mypass456', 'display_name': 'Jane Smith', 'status': 'active'},
            'mary_johnson': {'password': 'patient456', 'display_name': 'Mary Johnson', 'status': 'active'},
            'robert_wilson': {'password': 'patient789', 'display_name': 'Robert Wilson', 'status': 'active'}
        },
        'doctors': {
            'dr_smith': {'password': 'doctor123', 'display_name': 'Dr. Smith', 'status': 'active', 'department': 'General Medicine'},
            'dr_johnson': {'password': 'medical456', 'display_name': 'Dr. Johnson', 'status': 'active', 'department': 'Cardiology'},
            'dr_brown': {'password': 'doctor789', 'display_name': 'Dr. Brown', 'status': 'active', 'department': 'MBBS,MD'},
            'dr_davis': {'password': 'doctor456', 'display_name': 'Dr. Davis', 'status': 'active', 'department': 'Gynecologist'}
        },
        'admins': {
            'admin': {'password': 'admin123', 'display_name': 'System Admin', 'status': 'active'},
            'superadmin': {'password': 'super456', 'display_name': 'Super Admin', 'status': 'active'},
            'hospital_admin': {'password': 'hospital789', 'display_name': 'Hospital Admin', 'status': 'active'}
        }
    }
    
    # Default hospitals data (limited to 5 hospitals)
    default_hospitals = [
        {'id': 'hospital1', 'name': 'City General Hospital', 'description': 'Emergency & Trauma Center'},
        {'id': 'hospital2', 'name': 'Central Medical Center', 'description': 'Comprehensive Healthcare Services'},
        {'id': 'hospital3', 'name': 'Specialized Cardiac Care', 'description': 'Heart & Cardiovascular Treatment'},
        {'id': 'hospital4', 'name': 'Women\'s Health Clinic', 'description': 'Gynecology & Maternity Care'},
        {'id': 'hospital5', 'name': 'Pediatric Medical Center', 'description': 'Children\'s Healthcare & Family Medicine'}
    ]
    
    # Create files if they don't exist
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)
        print(f"✅ Created {USERS_FILE} with default users")
    
    if not os.path.exists(PATIENTS_FILE):
        with open(PATIENTS_FILE, 'w') as f:
            json.dump([], f, indent=2)
        print(f"✅ Created {PATIENTS_FILE}")
    
    if not os.path.exists(HOSPITALS_FILE):
        with open(HOSPITALS_FILE, 'w') as f:
            json.dump(default_hospitals, f, indent=2)
        print(f"✅ Created {HOSPITALS_FILE}")
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'last_token_number': {}}, f, indent=2)
        print(f"✅ Created {CONFIG_FILE}")

# Initialize JSON files
ensure_json_files()

# JSON Helper Functions
def save_json_file(filename, data):
    """Save data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False

def load_json_file(filename, default=None):
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return default or {}

def get_users_from_json():
    """Get all users from JSON files"""
    print("🔍 get_users_from_json() called")
    
    try:
        users_data = load_json_file(USERS_FILE, {})
        
        # Convert to the expected format for backward compatibility
        users = {'patients': {}, 'doctors': {}, 'admins': {}}
        
        for role in ['patients', 'doctors', 'admins']:
            for username, user_info in users_data.get(role, {}).items():
                if isinstance(user_info, dict):
                    users[role][username] = user_info.get('password', '')
                else:
                    users[role][username] = user_info
        
        print(f"✅ Loaded users from JSON: {sum(len(users[role]) for role in users)} total users")
        return users
        
    except Exception as e:
        print(f"❌ Error loading users from JSON: {e}")
        # Return default users
        return {
            'patients': {
                'patient1': 'pass123',
                'john_doe': 'patient123',
                'jane_smith': 'mypass456',
                'mary_johnson': 'patient456',
                'robert_wilson': 'patient789'
            },
            'doctors': {
                'dr_smith': 'doctor123',
                'dr_johnson': 'medical456',
                'dr_brown': 'doctor789',
                'dr_davis': 'doctor456'
            },
            'admins': {
                'admin': 'admin123',
                'superadmin': 'super456',
                'hospital_admin': 'hospital789'
            }
        }

def get_hospitals_from_json():
    """Get hospitals list from JSON"""
    return load_json_file(HOSPITALS_FILE, [])

def get_patients_from_json(hospital_name=None):
    """Get patients from JSON, optionally filtered by hospital"""
    all_patients = load_json_file(PATIENTS_FILE, [])
    if hospital_name:
        return [p for p in all_patients if p.get('selected_hospital') == hospital_name]
    return all_patients

def save_patient_to_json(patient_data):
    """Save patient data to JSON file"""
    try:
        patients = load_json_file(PATIENTS_FILE, [])
        
        # Add timestamp and unique ID
        patient_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        patient_data['id'] = f"patient_{len(patients) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        patients.append(patient_data)
        
        if save_json_file(PATIENTS_FILE, patients):
            return {'success': True, 'patient_id': patient_data['id']}
        else:
            return {'success': False, 'error': 'Failed to save patient data'}
    except Exception as e:
        print(f"❌ Error saving patient: {e}")
        return {'success': False, 'error': str(e)}

def get_next_token_number(hospital_name):
    """Get next token number for hospital"""
    config = load_json_file(CONFIG_FILE, {'last_token_number': {}})
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    key = f"{hospital_name}_{current_date}"
    
    # Get last token for this hospital today
    last_token = config['last_token_number'].get(key, 0)
    next_token = last_token + 1
    
    # Update config
    config['last_token_number'][key] = next_token
    save_json_file(CONFIG_FILE, config)
    
    return next_token

def authenticate_user_json(username, password, role):
    """Authenticate user using JSON files"""
    users_data = load_json_file(USERS_FILE, {})
    
    role_key = f"{role}s" if role != 'admin' else 'admins'
    if role == 'doctor':
        role_key = 'doctors'
    elif role == 'patient':
        role_key = 'patients'
    
    user_info = users_data.get(role_key, {}).get(username)
    if not user_info:
        return None
    
    # Handle both dict and string password formats
    stored_password = user_info.get('password') if isinstance(user_info, dict) else user_info
    
    if stored_password == password:
        display_name = user_info.get('display_name', username) if isinstance(user_info, dict) else username
        assigned_hospital = user_info.get('assigned_hospital') if isinstance(user_info, dict) else None
        return {
            'username': username,
            'display_name': display_name,
            'role': role,
            'status': user_info.get('status', 'active') if isinstance(user_info, dict) else 'active',
            'assigned_hospital': assigned_hospital
        }
    
    return None

def get_all_users_json(role):
    """Get all users of a specific role from JSON"""
    users_data = load_json_file(USERS_FILE, {})
    
    role_key = f"{role}s"
    if role == 'doctor':
        role_key = 'doctors'
    elif role == 'admin':
        role_key = 'admins'
    elif role == 'patient':
        role_key = 'patients'
    
    return users_data.get(role_key, {})

def get_hospital_stats_json(selected_hospital=None):
    """Get hospital statistics from JSON files"""
    patients = get_patients_from_json(selected_hospital)
    
    total_patients = len(patients)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Count today's patients
    today_patients = [p for p in patients if p.get('timestamp', '').startswith(today)]
    patients_today = len(today_patients)
    
    # Get unique hospitals from patients
    hospitals = set(p.get('selected_hospital', 'Unknown') for p in patients)
    total_hospitals = len(hospitals) if not selected_hospital else 1
    
    return {
        'total_patients': total_patients,
        'patients_today': patients_today,
        'total_hospitals': total_hospitals,
        'selected_hospital': selected_hospital
    }

# Get users (from JSON files)
print("🔍 Loading users at app startup...")
USERS = get_users_from_json()
print(f"🔍 Loaded USERS: {sum(len(users) for users in USERS.values())} total users")

@app.route('/favicon.ico')
def favicon():
    """Serve favicon - fallback to SVG"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.svg', mimetype='image/svg+xml')

def require_login(role=None):
    """Decorator to require login for certain routes"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(f"🔍 DEBUG require_login: Checking session for {f.__name__}")
            print(f"🔍 DEBUG require_login: Session contents: {dict(session)}")
            
            if 'user_id' not in session:
                print(f"🔍 DEBUG require_login: No user_id in session, redirecting to login")
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login_choice'))
            
            if role:
                print(f"🔍 DEBUG require_login: Required role: {role}, Current role: {session.get('user_role')}")
                if isinstance(role, list):
                    # Multiple roles allowed
                    if session.get('user_role') not in role:
                        print(f"🔍 DEBUG require_login: Role not in allowed list, access denied")
                        flash('Access denied. Insufficient permissions.', 'error')
                        return redirect(url_for('login_choice'))
                else:
                    # Single role
                    if session.get('user_role') != role:
                        print(f"🔍 DEBUG require_login: Role mismatch, access denied")
                        flash('Access denied. Insufficient permissions.', 'error')
                        return redirect(url_for('login_choice'))
            
            print(f"🔍 DEBUG require_login: Authentication successful for {f.__name__}")
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

@app.route('/patient/login')
def patient_login():
    """Patient login - redirect to hospital selection"""
    return redirect(url_for('hospital_selection'))

@app.route('/patient/hospital-selection', methods=['GET', 'POST'])
def hospital_selection():
    """Hospital selection page for patients"""
    if request.method == 'POST':
        selected_hospital = request.form.get('hospital')
        if selected_hospital:
            # Set patient session with selected hospital
            session['user_id'] = 'patient_user'
            session['user_role'] = 'patient'
            session['user_name'] = 'Patient'
            session['selected_hospital'] = selected_hospital
            flash(f'Welcome to {selected_hospital}! Please fill out the form below.', 'success')
            return redirect(url_for('patient_form'))
        else:
            flash('Please select a hospital.', 'error')
    
    # Get hospitals from JSON file
    hospitals = get_hospitals_from_json()
    
    # Get doctors assigned to each hospital
    doctors_by_hospital = get_doctors_by_hospital()
    
    # Add doctor information to hospitals
    for hospital in hospitals:
        hospital_name = hospital.get('name')
        hospital['doctors'] = doctors_by_hospital.get(hospital_name, [])
    
    print(f"✅ Loaded {len(hospitals)} hospitals from JSON with doctor assignments")
    
    return render_template('hospital_selection.html', hospitals=hospitals)

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"🔍 DEBUG doctor_login: Attempting login for '{username}'")
        
        # Use JSON authentication
        user = authenticate_user_json(username, password, 'doctor')
        if user:
            print(f"🔍 DEBUG doctor_login: JSON auth successful for {username}")
            session['user_id'] = username
            session['user_role'] = 'doctor'
            session['user_name'] = user.get('display_name', username.replace('_', ' ').title())
            session['assigned_hospital'] = user.get('assigned_hospital')
            
            hospital_info = f" at {user.get('assigned_hospital')}" if user.get('assigned_hospital') else ""
            flash(f'Welcome back, Dr. {session["user_name"]}{hospital_info}!', 'success')
            return redirect(url_for('doctor_dashboard'))
        else:
            print(f"🔍 DEBUG doctor_login: JSON auth failed for {username}")
            flash('Invalid username or password', 'error')
    
    return render_template('doctor_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"🔍 DEBUG admin_login: Attempting login for '{username}'")
        
        # Use JSON authentication
        user = authenticate_user_json(username, password, 'admin')
        if user:
            print(f"🔍 DEBUG admin_login: JSON auth successful for {username}")
            session['user_id'] = username
            session['user_role'] = 'admin'
            session['user_name'] = user.get('display_name', username.replace('_', ' ').title())
            flash(f'Welcome back, Admin {session["user_name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"🔍 DEBUG admin_login: JSON auth failed for {username}")
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/patient/dashboard')
def patient_dashboard():
    """Patient dashboard - redirects to form"""
    # Set default patient session if not already set
    if 'user_id' not in session:
        session['user_id'] = 'patient_user'
        session['user_role'] = 'patient'
        session['user_name'] = 'Patient'
    return redirect(url_for('patient_form'))

@app.route('/doctor/dashboard')
@require_login('doctor')
def doctor_dashboard():
    """Doctor dashboard"""
    assigned_hospital = session.get('assigned_hospital', 'No Hospital Assigned')
    
    # Get statistics for doctor's assigned hospital
    if assigned_hospital and assigned_hospital != 'No Hospital Assigned':
        hospital_data = get_hospital_data(assigned_hospital)
        stats = get_hospital_stats_json(assigned_hospital)
        
        # Add additional statistics
        total_patients = len(hospital_data)
        today = datetime.now().strftime('%Y-%m-%d')
        today_patients = len([p for p in hospital_data if p.get('timestamp', '').startswith(today)])
        
        # Recent patients (last 5)
        recent_patients = hospital_data[-5:] if hospital_data else []
        
        dashboard_stats = {
            'total_patients': total_patients,
            'patients_today': today_patients,
            'recent_patients': recent_patients,
            'hospital_name': assigned_hospital
        }
    else:
        dashboard_stats = {
            'total_patients': 0,
            'patients_today': 0,
            'recent_patients': [],
            'hospital_name': 'No Hospital Assigned'
        }
    
    return render_template('doctor_dashboard.html', 
                         assigned_hospital=assigned_hospital,
                         stats=dashboard_stats)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye, {user_name}! You have been logged out.', 'info')
    return redirect(url_for('login_choice'))

@app.route('/patient/form', methods=['GET', 'POST'])
def patient_form():
    # Set default patient session if not already set
    if 'user_id' not in session:
        session['user_id'] = 'patient_user'
        session['user_role'] = 'patient'
        session['user_name'] = 'Patient'
    
    # Redirect to hospital selection if no hospital is selected
    if 'selected_hospital' not in session:
        return redirect(url_for('hospital_selection'))
    
    if request.method == 'POST':
        # Get form data
        data = request.form.to_dict()
        
        # Process date of birth and calculate age
        if 'dateOfBirth' in data and data['dateOfBirth']:
            try:
                dob = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d')
                today = datetime.now()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                data['age'] = age
                data['dateOfBirth'] = data['dateOfBirth']  # Keep the original date
            except ValueError:
                # If date parsing fails, use age if provided
                if 'age' not in data:
                    data['age'] = 0
        
        # Combine country code and phone number
        if 'countryCode' in data and 'phone' in data:
            data['fullPhone'] = data['countryCode'] + data['phone']
            data['phone'] = data['fullPhone']  # Update phone to include country code
        
        # Add hospital information
        data['selected_hospital'] = session.get('selected_hospital', 'Unknown Hospital')
        
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
    
    # Pass today's date for date picker max value
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('ai_form.html', 
                         selected_hospital=session.get('selected_hospital'),
                         user_role=session.get('user_role'),
                         today=today)

@app.route('/legacy', methods=['GET', 'POST'])
def legacy_form():
    """Legacy form for comparison"""
    # Set default patient session if not already set
    if 'user_id' not in session:
        session['user_id'] = 'patient_user'
        session['user_role'] = 'patient'
        session['user_name'] = 'Patient'
    
    if request.method == 'POST':
        # Get form data
        data = request.form.to_dict()
        
        # Process date of birth and calculate age
        if 'dateOfBirth' in data and data['dateOfBirth']:
            from datetime import datetime
            try:
                dob = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d')
                today = datetime.now()
                
                age = today.year - dob.year
                if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                    age -= 1
                
                # Store both date of birth and calculated age
                data['age'] = str(age)
                data['dateOfBirth'] = data['dateOfBirth']
                print(f"🔍 Calculated age from DOB {data['dateOfBirth']}: {age} years")
                
            except ValueError:
                print(f"❌ Invalid date of birth format: {data['dateOfBirth']}")
                data['age'] = 'Unknown'
        
        # Process phone number with country code
        country_code = data.get('countryCode', '+91')
        phone_number = data.get('phone', '')
        
        if country_code and phone_number:
            # Combine country code and phone number
            full_phone = f"{country_code} {phone_number}"
            data['phone'] = full_phone
            print(f"🔍 Combined phone: {full_phone}")
        
        # Process full phone if provided (from JavaScript)
        if 'fullPhone' in data and data['fullPhone']:
            data['phone'] = data['fullPhone']
        
        # Use calculated age if provided by JavaScript
        if 'calculatedAge' in data and data['calculatedAge']:
            data['age'] = data['calculatedAge']
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add default hospital if not set
        if 'selected_hospital' not in data:
            data['selected_hospital'] = 'General Hospital'
        
        print(f"🔍 Final form data: {data}")
        
        # Save to JSON file (optional)
        save_form_data(data)
        
        return render_template('success.html', data=data)
    
    # For GET request, pass today's date to template
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('form.html', today=today)

def get_hospital_data(hospital_name=None):
    """Get patient data for a specific hospital or all hospitals"""
    print(f"🔍 get_hospital_data called with hospital_name: {hospital_name}")
    
    patients = get_patients_from_json(hospital_name)
    print(f"🔍 get_hospital_data returning {len(patients)} patients")
    
    return patients

def get_all_hospital_files():
    """Get list of all hospitals with patient data"""
    hospitals = get_hospitals_from_json()
    all_patients = get_patients_from_json()
    
    # Count patients per hospital
    hospital_patient_count = {}
    for patient in all_patients:
        hospital = patient.get('selected_hospital', 'Unknown')
        hospital_patient_count[hospital] = hospital_patient_count.get(hospital, 0) + 1
    
    # Convert to the format expected by templates
    hospital_files = []
    for hospital in hospitals:
        hospital_name = hospital.get('name', hospital.get('hospital_name', 'Unknown'))
        hospital_files.append({
            'filename': f"json_{hospital_name.lower().replace(' ', '_')}.json",
            'hospital_name': hospital_name,
            'patient_count': hospital_patient_count.get(hospital_name, 0)
        })
    
    return hospital_files

def get_hospital_data_by_filename(filename):
    """Get data from specific hospital (MongoDB compatibility function)"""
    # Extract hospital name from filename
    if filename.startswith('mongodb_'):
        hospital_name = filename.replace('mongodb_', '').replace('.json', '')
        hospital_name = hospital_name.replace('_', ' ').title()
        return get_hospital_data(hospital_name)
    
    # Fallback to JSON if still exists
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def get_time_slots():
    """Generate time slots from 7:30 AM to 8:30 PM (13 slots of 1 hour each)"""
    slots = []
    start_hour = 7
    start_minute = 30
    
    for i in range(13):  # 13 slots
        current_hour = start_hour + i
        if current_hour > 12:
            slot_time = f"{current_hour - 12}:{start_minute:02d} PM"
        elif current_hour == 12:
            slot_time = f"12:{start_minute:02d} PM"
        else:
            slot_time = f"{current_hour}:{start_minute:02d} AM"
        
        # Next slot time
        next_hour = current_hour + 1
        if next_hour > 12:
            next_slot_time = f"{next_hour - 12}:{start_minute:02d} PM"
        elif next_hour == 12:
            next_slot_time = f"12:{start_minute:02d} PM"
        else:
            next_slot_time = f"{next_hour}:{start_minute:02d} AM"
        
        slots.append({
            'slot_number': i + 1,
            'time_range': f"{slot_time} - {next_slot_time}",
            'start_time': slot_time,
            'end_time': next_slot_time
        })
    
    return slots

def assign_token_and_slot(hospital_name):
    """Assign token number and time slot for a hospital"""
    print(f"🔍 DEBUG assign_token_and_slot: Called for hospital '{hospital_name}'")
    
    # Get next token number for this hospital
    token_number = get_next_token_number(hospital_name)
    print(f"🔍 DEBUG assign_token_and_slot: Assigned token number {token_number} for '{hospital_name}'")
    
    # Calculate slot (each slot accommodates 60 patients)
    slot_index = ((token_number - 1) // 60) % 13  # 13 slots available, cycle through them
    
    # Get time slots
    time_slots = get_time_slots()
    assigned_slot = time_slots[slot_index]
    
    # Calculate position in slot (1-60)
    position_in_slot = ((token_number - 1) % 60) + 1
    
    return {
        'token_number': token_number,
        'slot_number': assigned_slot['slot_number'],
        'time_range': assigned_slot['time_range'],
        'start_time': assigned_slot['start_time'],
        'end_time': assigned_slot['end_time'],
        'position_in_slot': position_in_slot,
        'estimated_wait_time': f"{(position_in_slot - 1) * 5} minutes"  # Assuming 5 min per patient
    }

def save_form_data(data):
    """Save form data to JSON files with token assignment"""
    print(f"🔍 DEBUG save_form_data: Starting save process for {data.get('firstName', 'Unknown')}")
    
    # Get the selected hospital from the data
    selected_hospital = data.get('selected_hospital', 'Unknown Hospital')
    print(f"🔍 DEBUG save_form_data: Selected hospital: '{selected_hospital}'")
    
    # Assign token and slot before saving
    token_info = assign_token_and_slot(selected_hospital)
    print(f"🔍 DEBUG save_form_data: Token info received: {token_info}")
    
    # Add token information to patient data
    data.update(token_info)
    print(f"🔍 DEBUG save_form_data: Data updated with token info")
    
    # Save to JSON files
    result = save_patient_to_json(data)
    if result['success']:
        print(f"✅ Patient saved to JSON: {data.get('firstName', 'Unknown')} with token {data.get('token_number')}")
        return data
    else:
        print(f"❌ Failed to save to JSON: {result.get('error', 'Unknown error')}")
        return None

@app.route('/view_submissions')
@require_login(['doctor', 'admin'])
def view_submissions():
    """View all form submissions (doctor and admin access)"""
    if session.get('user_role') == 'admin':
        # Admin sees all patients from all hospitals
        data = get_hospital_data()
    else:
        # Doctor sees only patients from their assigned hospital
        assigned_hospital = session.get('assigned_hospital')
        if assigned_hospital:
            print(f"🔍 DEBUG view_submissions: Doctor restricted to hospital: {assigned_hospital}")
            data = get_hospital_data(assigned_hospital)
        else:
            print(f"🔍 DEBUG view_submissions: Doctor has no assigned hospital")
            data = []
    
    return render_template('admin.html', submissions=data, session=session)

@app.route('/doctor/patients')
@require_login(['doctor', 'admin'])
def patient_management():
    """Patient management page for doctors and admins"""
    # Get hospital filter from URL parameter
    selected_hospital = request.args.get('hospital', '')
    
    # For doctors, filter by their assigned hospital unless they're admin
    if session.get('user_role') == 'doctor' and session.get('assigned_hospital'):
        selected_hospital = session.get('assigned_hospital')
        print(f"🔍 DEBUG patient_management: Doctor restricted to hospital: {selected_hospital}")
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
    else:
        # Get data from all hospitals (admins only)
        data = get_hospital_data()
    
    # DEBUG: Print what data we're getting
    print(f"🔍 DEBUG patient_management: Found {len(data)} patients")
    for i, patient in enumerate(data[:3]):
        print(f"   - Patient {i+1}: {patient.get('firstName', 'Unknown')} at {patient.get('selected_hospital', 'Unknown')}")
    
    # Calculate statistics using JSON data
    stats = get_hospital_stats_json(selected_hospital)
    
    # Add additional statistics
    total_patients = len(data)
    this_month = datetime.now().strftime('%Y-%m')
    this_month_count = len([d for d in data if d.get('timestamp', '').startswith(this_month)])
    male_patients = len([d for d in data if d.get('gender', '').lower() == 'male'])
    female_patients = len([d for d in data if d.get('gender', '').lower() == 'female'])
    
    # Calculate token statistics
    patients_with_tokens = len([d for d in data if d.get('token_number')])
    today = datetime.now().strftime('%Y-%m-%d')
    today_tokens = len([d for d in data if d.get('timestamp', '').startswith(today) and d.get('token_number')])
    
    # Update stats
    stats.update({
        'total_patients': total_patients,
        'this_month': this_month_count,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'patients_with_tokens': patients_with_tokens,
        'today_tokens': today_tokens
    })
    
    # Get list of hospitals for filter dropdown
    hospital_files = get_all_hospital_files()
    
    print(f"🔍 DEBUG: Passing to template - patients: {len(data)}, hospital_files: {len(hospital_files)}")
    
    return render_template('patient_management.html', 
                         patients=data, 
                         stats=stats, 
                         hospital_files=hospital_files,
                         selected_hospital=selected_hospital,
                         session=session)

# Add admin-specific route for patient management
@app.route('/admin/patients')
@require_login('admin')
def admin_patient_management():
    """Admin-specific patient management page"""
    return redirect(url_for('patient_management'))

@app.route('/doctor/reports')
@require_login(['doctor', 'admin'])
def reports():
    """Medical reports page for doctors and admins"""
    # Get hospital filter from URL parameter
    selected_hospital = request.args.get('hospital', '')
    
    # For doctors, filter by their assigned hospital unless they're admin
    if session.get('user_role') == 'doctor' and session.get('assigned_hospital'):
        selected_hospital = session.get('assigned_hospital')
        print(f"🔍 DEBUG reports: Doctor restricted to hospital: {selected_hospital}")
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
    else:
        # Get data from all hospitals (admins only)
        data = get_hospital_data()
    
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
    
    # Get list of hospitals for filter dropdown
    hospital_files = get_all_hospital_files()
    
    return render_template('reports.html', 
                         stats=stats, 
                         patients=data,
                         hospital_files=hospital_files,
                         selected_hospital=selected_hospital,
                         session=session)

@app.route('/doctor/settings')
@require_login('doctor')
def settings():
    """System settings page for doctors"""
    return render_template('settings.html')

@app.route('/doctor/patient/<int:patient_id>')
@require_login(['doctor', 'admin'])
def patient_detail(patient_id):
    """View detailed information for a specific patient (doctor and admin access)"""
    # Get hospital filter from URL parameter
    selected_hospital = request.args.get('hospital', '')
    
    # For doctors, filter by their assigned hospital unless they're admin
    if session.get('user_role') == 'doctor' and session.get('assigned_hospital'):
        selected_hospital = session.get('assigned_hospital')
        print(f"🔍 DEBUG patient_detail: Doctor restricted to hospital: {selected_hospital}")
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
    else:
        # Get data from all hospitals (admins only)
        data = get_hospital_data()
    
    if patient_id < len(data):
        patient = data[patient_id]
        return render_template('patient_detail.html', patient=patient, patient_id=patient_id, session=session)
    else:
        flash('Patient not found', 'error')
        return redirect(url_for('patient_management'))

@app.route('/admin/export/csv')
@require_login('admin')
def export_csv():
    """Export patient data as CSV file (Admin only)"""
    # Get data from MongoDB instead of JSON files
    data = get_hospital_data()
    
    if not data:
        flash('No patient data available to export.', 'warning')
        return redirect(url_for('patient_management'))
    
    # Create CSV in memory
    output = io.StringIO()
    
    # Define CSV headers based on available fields
    fieldnames = [
        'timestamp', 'selected_hospital', 'firstName', 'lastName', 'age', 'gender', 'phone', 
        'address', 'symptoms', 'allergies', 'medications', 'medicalHistory',
        'emergencyName', 'emergencyPhone', 'emergencyRelation', 'emergency_contact'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    # Write patient data
    for patient in data:
        # Ensure all fields exist with default empty values
        row = {field: patient.get(field, '') for field in fieldnames}
        writer.writerow(row)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=patient_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/admin/export/filtered-csv')
@require_login('admin')  
def export_filtered_csv():
    """Export filtered patient data as CSV file (Admin only)"""
    # Get data from MongoDB instead of JSON files
    data = get_hospital_data()
    
    # Get filter parameters from URL
    gender_filter = request.args.get('gender', '').lower()
    date_filter = request.args.get('date', '')
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    
    # Apply filters
    filtered_data = data
    
    if gender_filter and gender_filter != 'all':
        filtered_data = [d for d in filtered_data if d.get('gender', '').lower() == gender_filter]
    
    if date_filter:
        filtered_data = [d for d in filtered_data if d.get('timestamp', '').startswith(date_filter)]
    
    if age_min is not None:
        filtered_data = [d for d in filtered_data if d.get('age') and int(d.get('age', 0)) >= age_min]
    
    if age_max is not None:
        filtered_data = [d for d in filtered_data if d.get('age') and int(d.get('age', 0)) <= age_max]
    
    if not filtered_data:
        flash('No patient data matches the selected filters.', 'warning')
        return redirect(url_for('patient_management'))
    
    # Create CSV in memory
    output = io.StringIO()
    
    # Define CSV headers
    fieldnames = [
        'timestamp', 'selected_hospital', 'firstName', 'lastName', 'age', 'gender', 'phone', 
        'address', 'symptoms', 'allergies', 'medications', 'medicalHistory',
        'emergencyName', 'emergencyPhone', 'emergencyRelation'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    # Write filtered patient data
    for patient in filtered_data:
        row = {field: patient.get(field, '') for field in fieldnames}
        writer.writerow(row)
    
    # Create response with filter info in filename
    filter_info = []
    if gender_filter and gender_filter != 'all':
        filter_info.append(f"gender-{gender_filter}")
    if date_filter:
        filter_info.append(f"date-{date_filter}")
    if age_min is not None or age_max is not None:
        age_range = f"age-{age_min or 0}-{age_max or 999}"
        filter_info.append(age_range)
    
    filter_suffix = "_" + "_".join(filter_info) if filter_info else ""
    filename = f"patient_data_filtered{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@app.route('/admin/dashboard')
@require_login('admin')
def admin_dashboard():
    """Admin dashboard with comprehensive system overview"""
    # Get data from all hospitals
    patient_data = get_hospital_data()
    
    # Get user counts from JSON
    doctors_data = get_all_users_json('doctor')
    admins_data = get_all_users_json('admin')
    patients_users_data = get_all_users_json('patient')
    
    total_doctors = len(doctors_data)
    total_admins = len(admins_data)
    total_patients_users = len(patients_users_data)
    
    # Calculate comprehensive statistics
    total_patients = len(patient_data)
    
    # Recent activity (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    recent_patients = len([d for d in patient_data if d.get('timestamp', '') >= seven_days_ago])
    
    # Gender distribution
    male_patients = len([d for d in patient_data if d.get('gender', '').lower() == 'male'])
    female_patients = len([d for d in patient_data if d.get('gender', '').lower() == 'female'])
    
    # Age distribution
    age_groups = {'0-18': 0, '19-35': 0, '36-60': 0, '60+': 0}
    for patient in patient_data:
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
    
    # Hospital-wise statistics
    hospital_stats = {}
    for patient in patient_data:
        hospital = patient.get('selected_hospital', 'Unknown')
        hospital_stats[hospital] = hospital_stats.get(hospital, 0) + 1
    
    stats = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'total_patients_users': total_patients_users,
        'recent_patients': recent_patients,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'age_groups': age_groups,
        'hospital_stats': hospital_stats
    }
    
    return render_template('admin_dashboard.html', stats=stats, patients=patient_data[:5])  # Show last 5 patients

@app.route('/admin/doctors')
@require_login('admin')
def manage_doctors():
    """Admin page to manage doctors"""
    doctors_info = []
    
    # Get doctors from JSON
    doctors_data = get_all_users_json('doctor')
    for doctor_id, doctor_info in doctors_data.items():
        if isinstance(doctor_info, dict):
            doctors_info.append({
                'id': doctor_id,
                'name': doctor_info.get('display_name', doctor_id.replace('_', ' ').title()),
                'status': doctor_info.get('status', 'Active').title(),
                'department': doctor_info.get('department', 'General Medicine'),
                'specialization': doctor_info.get('specialization', 'General Practice'),
                'last_login': doctor_info.get('last_login', 'Never')
            })
        else:
            # Handle simple string password format
            doctors_info.append({
                'id': doctor_id,
                'name': doctor_id.replace('_', ' ').title(),
                'status': 'Active',
                'department': 'General Medicine',
                'specialization': 'General Practice',
                'last_login': 'Unknown'
            })
    
    return render_template('admin_doctors.html', doctors=doctors_info)

@app.route('/admin/users')
@require_login('admin')
def manage_users():
    """Admin page to manage all users"""
    all_users = {'patients': [], 'doctors': [], 'admins': []}
    
    # Get all users from JSON
    for role in ['patient', 'doctor', 'admin']:
        users_data = get_all_users_json(role)
        role_key = f"{role}s" if role != 'admin' else 'admins'
        
        for user_id, user_info in users_data.items():
            if isinstance(user_info, dict):
                all_users[role_key].append({
                    'id': user_id,
                    'name': user_info.get('display_name', user_id.replace('_', ' ').title()),
                    'role': role.title(),
                    'status': user_info.get('status', 'Active').title(),
                    'created_at': user_info.get('created_at', 'Unknown'),
                    'last_login': user_info.get('last_login', 'Never')
                })
            else:
                # Handle simple string password format
                all_users[role_key].append({
                    'id': user_id,
                    'name': user_id.replace('_', ' ').title(),
                    'role': role.title(),
                    'status': 'Active',
                    'created_at': 'Unknown',
                    'last_login': 'Never'
                })
    
    return render_template('admin_users.html', users=all_users)

@app.route('/admin/system')
@require_login('admin')
def system_settings():
    """Admin system settings and configuration"""
    import sys
    import platform
    
    system_info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'flask_version': '2.3.0',  # You can get this dynamically
        'total_storage': '0 MB',  # In a real system, calculate actual storage
        'uptime': 'N/A'  # In a real system, track server uptime
    }
    
    return render_template('admin_system.html', system_info=system_info)

@app.route('/admin/reports')
@require_login('admin')
def admin_reports():
    """Comprehensive admin reports"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # Generate comprehensive statistics
    total_patients = len(data)
    total_doctors = len(USERS['doctors'])
    
    # Monthly breakdown
    monthly_stats = {}
    for patient in data:
        timestamp = patient.get('timestamp', '')
        if timestamp:
            month = timestamp[:7]  # YYYY-MM format
            monthly_stats[month] = monthly_stats.get(month, 0) + 1
    
    # Most common symptoms
    symptoms_count = {}
    for patient in data:
        symptoms = patient.get('symptoms', '').lower()
        if symptoms:
            symptoms_count[symptoms] = symptoms_count.get(symptoms, 0) + 1
    
    # Sort symptoms by frequency
    top_symptoms = sorted(symptoms_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    stats = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'monthly_stats': monthly_stats,
        'top_symptoms': top_symptoms
    }
    
    return render_template('admin_reports.html', stats=stats, patients=data)

@app.route('/doctor/export/csv')
@require_login('doctor')
def doctor_export_basic():
    """Export basic patient data as CSV file (Doctor - limited access)"""
    # Get data filtered by doctor's assigned hospital
    assigned_hospital = session.get('assigned_hospital')
    if assigned_hospital:
        print(f"🔍 DEBUG doctor_export: Doctor restricted to hospital: {assigned_hospital}")
        data = get_hospital_data(assigned_hospital)
    else:
        print(f"🔍 DEBUG doctor_export: Doctor has no assigned hospital")
        data = []
    
    if not data:
        flash('No patient data available to export.', 'warning')
        return redirect(url_for('patient_management'))
    
    # Create CSV in memory with limited fields for doctors
    output = io.StringIO()
    
    # Limited fieldnames for doctors (no sensitive emergency contact info)
    fieldnames = [
        'timestamp', 'selected_hospital', 'firstName', 'lastName', 'age', 'gender', 
        'symptoms', 'allergies', 'medications', 'medicalHistory'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    # Write patient data
    for patient in data:
        # Ensure all fields exist with default empty values
        row = {field: patient.get(field, '') for field in fieldnames}
        writer.writerow(row)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=patient_basic_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/admin/export/doctors-csv')
@require_login('admin')
def export_doctors_csv():
    """Export doctors data as CSV file (Admin only)"""
    output = io.StringIO()
    
    fieldnames = ['username', 'display_name', 'role', 'status', 'department', 'specialization', 'last_login']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Get doctors from JSON
    doctors_data = get_all_users_json('doctor')
    for doctor_id, doctor_info in doctors_data.items():
        if isinstance(doctor_info, dict):
            writer.writerow({
                'username': doctor_id,
                'display_name': doctor_info.get('display_name', doctor_id.replace('_', ' ').title()),
                'role': 'Doctor',
                'status': doctor_info.get('status', 'Active').title(),
                'department': doctor_info.get('department', 'General Medicine'),
                'specialization': doctor_info.get('specialization', 'General Practice'),
                'last_login': str(doctor_info.get('last_login', 'Never'))
            })
        else:
            # Handle simple string password format
            writer.writerow({
                'username': doctor_id,
                'display_name': doctor_id.replace('_', ' ').title(),
                'role': 'Doctor',
                'status': 'Active',
                'department': 'General Medicine',
                'specialization': 'General Practice',
                'last_login': 'Unknown'
            })
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=doctors_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/admin/export/users-csv')
@require_login('admin')
def export_users_csv():
    """Export all users data as CSV file (Admin only)"""
    output = io.StringIO()
    
    fieldnames = ['username', 'display_name', 'role', 'status', 'created_at', 'last_login']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Get all users from JSON
    for role in ['patient', 'doctor', 'admin']:
        users_data = get_all_users_json(role)
        for user_id, user_info in users_data.items():
            if isinstance(user_info, dict):
                writer.writerow({
                    'username': user_id,
                    'display_name': user_info.get('display_name', user_id.replace('_', ' ').title()),
                    'role': role.title(),
                    'status': user_info.get('status', 'Active').title(),
                    'created_at': str(user_info.get('created_at', 'Unknown')),
                    'last_login': str(user_info.get('last_login', 'Never'))
                })
            else:
                # Handle simple string password format
                writer.writerow({
                    'username': user_id,
                    'display_name': user_id.replace('_', ' ').title(),
                    'role': role.title(),
                    'status': 'Active',
                    'created_at': 'Unknown',
                    'last_login': 'Unknown'
                })
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=all_users_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/admin/tokens')
@require_login(['admin', 'doctor'])
def view_tokens():
    """View token/appointment status for all hospitals"""
    # Get hospital filter from URL parameter
    selected_hospital = request.args.get('hospital', '')
    
    # For doctors, filter by their assigned hospital unless they're admin
    if session.get('user_role') == 'doctor' and session.get('assigned_hospital'):
        selected_hospital = session.get('assigned_hospital')
        print(f"🔍 DEBUG view_tokens: Doctor restricted to hospital: {selected_hospital}")
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
        hospital_name = selected_hospital
    else:
        # Get data from all hospitals for overview (admins only)
        data = get_hospital_data()
        hospital_name = 'All Hospitals'
    
    # Get time slots for reference
    time_slots = get_time_slots()
    
    # Organize data by slots
    slot_data = {}
    for slot in time_slots:
        slot_data[slot['slot_number']] = {
            'time_range': slot['time_range'],
            'patients': [],
            'total_patients': 0
        }
    
    # Group patients by slots
    for patient in data:
        slot_num = patient.get('slot_number', 1)
        if slot_num in slot_data:
            slot_data[slot_num]['patients'].append(patient)
            slot_data[slot_num]['total_patients'] += 1
    
    # Get list of hospitals for filter dropdown
    hospital_files = get_all_hospital_files()
    
    return render_template('token_status.html', 
                         slot_data=slot_data,
                         time_slots=time_slots,
                         hospital_files=hospital_files,
                         selected_hospital=selected_hospital,
                         hospital_name=hospital_name,
                         total_patients=len(data),
                         session=session)

def get_doctors_by_hospital():
    """Get doctors assigned to each hospital"""
    users_data = load_json_file(USERS_FILE, {})
    doctors_data = users_data.get('doctors', {})
    
    doctors_by_hospital = {}
    for doctor_id, doctor_info in doctors_data.items():
        if isinstance(doctor_info, dict):
            hospital = doctor_info.get('assigned_hospital')
            doctor_name = doctor_info.get('display_name', doctor_id.replace('_', ' ').title())
            department = doctor_info.get('department', 'General Medicine')
            
            if hospital:
                if hospital not in doctors_by_hospital:
                    doctors_by_hospital[hospital] = []
                doctors_by_hospital[hospital].append({
                    'name': doctor_name,
                    'department': department,
                    'id': doctor_id
                })
    
    return doctors_by_hospital

# System Management Routes
@app.route('/admin/clear-data', methods=['POST'])
@require_login('admin')
def clear_system_data():
    """Clear all system data (patients, form submissions)"""
    try:
        # Clear patients data
        patients_cleared = 0
        
        # Clear all hospital JSON files
        hospital_files = get_all_hospital_files()
        for hospital_file in hospital_files:
            file_path = f"hospital_data_{hospital_file['hospital_name'].replace(' ', '_').lower()}.json"
            if os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
                patients_cleared += hospital_file['patient_count']
        
        # Clear main form data file
        if os.path.exists('form_data.json'):
            with open('form_data.json', 'w') as f:
                json.dump([], f)
        
        # Clear system config if needed
        system_config = load_json_file(SYSTEM_CONFIG_FILE, {})
        system_config['last_data_clear'] = datetime.now().isoformat()
        save_json_file(SYSTEM_CONFIG_FILE, system_config)
        
        flash(f'System data cleared successfully! Removed {patients_cleared} patient records.', 'success')
        print(f"🧹 SYSTEM: Data cleared by admin. {patients_cleared} records removed.")
        
    except Exception as e:
        flash(f'Error clearing system data: {str(e)}', 'error')
        print(f"❌ ERROR clearing system data: {e}")
    
    return redirect(url_for('system_settings'))

@app.route('/admin/clear-cache', methods=['POST'])
@require_login('admin')
def clear_system_cache():
    """Clear system cache and temporary files"""
    try:
        import tempfile
        import shutil
        
        cache_cleared = 0
        temp_files_cleared = 0
        
        # Clear Python cache files
        for root, dirs, files in os.walk('.'):
            for d in dirs[:]:
                if d == '__pycache__':
                    shutil.rmtree(os.path.join(root, d))
                    cache_cleared += 1
                    dirs.remove(d)
            for f in files:
                if f.endswith('.pyc') or f.endswith('.pyo'):
                    os.remove(os.path.join(root, f))
                    temp_files_cleared += 1
        
        # Update system config
        system_config = load_json_file(SYSTEM_CONFIG_FILE, {})
        system_config['last_cache_clear'] = datetime.now().isoformat()
        save_json_file(SYSTEM_CONFIG_FILE, system_config)
        
        flash(f'System cache cleared successfully! Removed {cache_cleared} cache directories and {temp_files_cleared} temporary files.', 'success')
        print(f"🧹 SYSTEM: Cache cleared by admin. {cache_cleared} directories, {temp_files_cleared} files.")
        
    except Exception as e:
        flash(f'Error clearing system cache: {str(e)}', 'error')
        print(f"❌ ERROR clearing cache: {e}")
    
    return redirect(url_for('system_settings'))

@app.route('/admin/restart-app', methods=['POST'])
@require_login('admin')
def restart_application():
    """Restart the Flask application"""
    try:
        # Update system config with restart request
        system_config = load_json_file(SYSTEM_CONFIG_FILE, {})
        system_config['restart_requested'] = datetime.now().isoformat()
        system_config['restart_by'] = session.get('user_name', 'Unknown Admin')
        save_json_file(SYSTEM_CONFIG_FILE, system_config)
        
        flash('Application restart initiated. The system will be back online shortly.', 'info')
        print(f"🔄 SYSTEM: Application restart requested by admin {session.get('user_name')}")
        
        # In a production environment, you would use a process manager like systemd, supervisor, or pm2
        # For development, we'll simulate a restart by showing a message
        
        def restart_server():
            import time
            time.sleep(2)  # Give time for response to be sent
            os._exit(0)  # Force exit - in production, use proper restart mechanism
        
        import threading
        threading.Thread(target=restart_server).start()
        
        return redirect(url_for('system_settings'))
        
    except Exception as e:
        flash(f'Error restarting application: {str(e)}', 'error')
        print(f"❌ ERROR restarting application: {e}")
        return redirect(url_for('system_settings'))

@app.route('/admin/update-system', methods=['POST'])
@require_login('admin')
def update_system():
    """Update system dependencies and configuration"""
    try:
        # Update system config
        system_config = load_json_file(SYSTEM_CONFIG_FILE, {})
        system_config['last_update_check'] = datetime.now().isoformat()
        system_config['update_by'] = session.get('user_name', 'Unknown Admin')
        
        # Simulate system updates (in real system, you'd check for actual updates)
        updates_available = [
            "Security patches applied",
            "Dependencies updated",
            "Configuration optimized",
            "System performance improved"
        ]
        
        system_config['last_updates'] = updates_available
        save_json_file(SYSTEM_CONFIG_FILE, system_config)
        
        flash('System update completed successfully! All components are up to date.', 'success')
        print(f"🔄 SYSTEM: System updated by admin {session.get('user_name')}")
        
        for update in updates_available:
            print(f"✅ UPDATE: {update}")
        
    except Exception as e:
        flash(f'Error updating system: {str(e)}', 'error')
        print(f"❌ ERROR updating system: {e}")
    
    return redirect(url_for('system_settings'))

@app.route('/doctor/patient/<int:patient_id>/delete', methods=['POST'])
@require_login(['doctor', 'admin'])
def delete_patient(patient_id):
    """Delete a specific patient record"""
    try:
        # Debug session information
        print(f"🔍 DELETE DEBUG: Session contents: {dict(session)}")
        print(f"🔍 DELETE DEBUG: User role: {session.get('user_role')}")
        print(f"🔍 DELETE DEBUG: Assigned hospital: {session.get('assigned_hospital')}")
        print(f"🔍 DELETE DEBUG: Form data: {dict(request.form)}")
        print(f"🔍 DELETE DEBUG: Patient ID: {patient_id}")
        
        # Determine hospital based on user role
        if session.get('user_role') == 'doctor' and session.get('assigned_hospital'):
            # Doctors can only delete from their assigned hospital
            selected_hospital = session.get('assigned_hospital')
            print(f"🔍 DEBUG delete_patient: Doctor restricted to hospital: {selected_hospital}")
        else:
            # Admins can delete from any hospital - get from form or URL
            selected_hospital = request.form.get('hospital', '') or request.args.get('hospital', '')
            print(f"🔍 DEBUG delete_patient: Admin deleting from hospital: {selected_hospital}")
        
        # For doctors, we must have a hospital
        if session.get('user_role') == 'doctor' and not selected_hospital:
            flash('Error: No hospital assigned to your account.', 'error')
            print(f"❌ Delete failed: Doctor has no assigned hospital")
            return redirect(url_for('patient_management'))
        
        # Get data for specific hospital (filtered from main patients file)
        data = get_hospital_data(selected_hospital)
        print(f"🔍 DELETE DEBUG: Data length for hospital '{selected_hospital}': {len(data)}")
        
        # Check if patient exists
        if patient_id >= len(data):
            flash('Patient not found.', 'error')
            print(f"❌ Patient not found: ID {patient_id} >= length {len(data)}")
            return redirect(url_for('patient_management', hospital=selected_hospital))
        
        # Get patient info for logging
        patient_to_delete = data[patient_id]
        patient_name = patient_to_delete.get('name', patient_to_delete.get('firstName', 'Unknown'))
        patient_age = patient_to_delete.get('age', 'Unknown')
        patient_hospital = patient_to_delete.get('selected_hospital', 'Unknown')
        
        print(f"🔍 DELETE DEBUG: Deleting patient: {patient_name} (Age: {patient_age}) from {patient_hospital}")
        
        # For deletion, we need to find this patient in the main patients file and remove it
        all_patients = load_json_file(PATIENTS_FILE, [])
        
        # Find the actual patient in the main list by matching the data
        patient_found = False
        for i, patient in enumerate(all_patients):
            if (patient.get('name', patient.get('firstName')) == patient_name and
                patient.get('age') == patient_age and
                patient.get('selected_hospital') == patient_hospital):
                
                # For doctors, verify this patient is from their hospital
                if session.get('user_role') == 'doctor' and patient.get('selected_hospital') != selected_hospital:
                    flash('Error: You can only delete patients from your assigned hospital.', 'error')
                    print(f"❌ Delete denied: Doctor tried to delete patient from different hospital")
                    return redirect(url_for('patient_management', hospital=selected_hospital))
                
                # Remove the patient
                del all_patients[i]
                patient_found = True
                print(f"🔍 DELETE DEBUG: Found and removed patient at index {i} in main list")
                break
        
        if not patient_found:
            flash('Error: Patient not found in database.', 'error')
            print(f"❌ Patient not found in main database")
            return redirect(url_for('patient_management', hospital=selected_hospital))
        
        # Save updated data back to main file
        save_result = save_json_file(PATIENTS_FILE, all_patients)
        if save_result.get('success'):
            flash(f'Patient "{patient_name}" has been successfully deleted.', 'success')
            print(f"🗑️ Patient deleted: {patient_name} (Age: {patient_age}) from {patient_hospital} by {session.get('user_role')} {session.get('user_name')}")
        else:
            flash(f'Error deleting patient: {save_result.get("error")}', 'error')
            print(f"❌ Failed to delete patient: {save_result.get('error')}")
        
    except Exception as e:
        flash(f'Error deleting patient: {str(e)}', 'error')
        print(f"❌ Exception during patient deletion: {e}")
        import traceback
        traceback.print_exc()
        selected_hospital = session.get('assigned_hospital', '')  # Fallback for redirect
    
    return redirect(url_for('patient_management', hospital=selected_hospital))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)