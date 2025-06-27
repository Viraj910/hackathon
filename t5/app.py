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

# Import MongoDB database manager
from database import DatabaseManager, get_db, init_db

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Initialize MongoDB
db = init_db(app)

# Simple user database (in production, use a proper database)
USERS = {
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

@app.route('/favicon.ico')
def favicon():
    """Serve favicon - fallback to SVG"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.svg', mimetype='image/svg+xml')

def require_login(role=None):
    """Decorator to require login for certain routes"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login_choice'))
            
            if role:
                if isinstance(role, list):
                    # Multiple roles allowed
                    if session.get('user_role') not in role:
                        flash('Access denied. Insufficient permissions.', 'error')
                        return redirect(url_for('login_choice'))
                else:
                    # Single role
                    if session.get('user_role') != role:
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
    
    # List of available hospitals
    hospitals = [
        {'id': 'hospital1', 'name': 'Hospital 1', 'description': 'General Medicine & Emergency Care'},
        {'id': 'hospital2', 'name': 'Hospital 2', 'description': 'Specialized Cardiac Care'},
        {'id': 'hospital3', 'name': 'Hospital 3', 'description': 'Pediatric & Family Medicine'},
        {'id': 'hospital4', 'name': 'Hospital 4', 'description': 'Orthopedic & Sports Medicine'},
        {'id': 'hospital5', 'name': 'Hospital 5', 'description': 'Cancer Treatment & Oncology'},
        {'id': 'hospital6', 'name': 'Central Medical Center', 'description': 'Comprehensive Healthcare Services'},
        {'id': 'hospital7', 'name': 'City General Hospital', 'description': 'Emergency & Trauma Center'},
        {'id': 'hospital8', 'name': 'Women\'s Health Clinic', 'description': 'Gynecology & Maternity Care'},
        {'id': 'hospital9', 'name': 'Mental Health Institute', 'description': 'Psychiatry & Behavioral Health'},
        {'id': 'hospital10', 'name': 'Rehabilitation Center', 'description': 'Physical Therapy & Recovery'}
    ]
    
    return render_template('hospital_selection.html', hospitals=hospitals)

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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS['admins'] and USERS['admins'][username] == password:
            session['user_id'] = username
            session['user_role'] = 'admin'
            session['user_name'] = username.replace('_', ' ').title()
            flash(f'Welcome back, Admin {session["user_name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
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
    return render_template('doctor_dashboard.html')

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
    
    return render_template('ai_form.html', 
                         selected_hospital=session.get('selected_hospital'),
                         user_role=session.get('user_role'))

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
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to JSON file (optional)
        save_form_data(data)
        
        return render_template('success.html', data=data)
    
    return render_template('form.html')

def get_hospital_data(hospital_name=None):
    """Get patient data for a specific hospital or all hospitals"""
    db = get_db()
    if not db.is_connected():
        print("⚠️ Database not connected, falling back to empty data")
        return []
    
    return db.get_patients(hospital_name)

def get_all_hospital_files():
    """Get list of all hospitals with patient data"""
    db = get_db()
    if not db.is_connected():
        return []
    
    hospitals = db.get_hospitals_list()
    
    # Convert to the format expected by templates
    hospital_files = []
    for hospital in hospitals:
        hospital_files.append({
            'filename': f"mongodb_{hospital['hospital_name'].lower().replace(' ', '_')}.json",
            'hospital_name': hospital['hospital_name'],
            'patient_count': hospital['patient_count']
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
    db = get_db()
    
    if not db.is_connected():
        # Fallback to simple numbering if DB is not connected
        return {
            'token_number': 1,
            'slot_number': 1,
            'time_range': '7:30 AM - 8:30 AM',
            'start_time': '7:30 AM',
            'end_time': '8:30 AM',
            'position_in_slot': 1,
            'estimated_wait_time': '0 minutes'
        }
    
    # Get next token number for this hospital
    token_number = db.get_next_token_for_hospital(hospital_name)
    
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
    """Save form data to MongoDB with token assignment"""
    db = get_db()
    
    # Get the selected hospital from the data
    selected_hospital = data.get('selected_hospital', 'Unknown Hospital')
    
    # Assign token and slot before saving
    token_info = assign_token_and_slot(selected_hospital)
    
    # Add token information to patient data
    data.update(token_info)
    
    if db.is_connected():
        # Save to MongoDB
        result = db.save_patient(data)
        if result:
            print(f"✅ Patient saved to MongoDB: {data.get('firstName', 'Unknown')}")
            return result
        else:
            print("❌ Failed to save to MongoDB, falling back to JSON")
    
    # Fallback to JSON if MongoDB is not available
    save_form_data_json_fallback(data)
    return data

def save_form_data_json_fallback(data):
    """Fallback function to save data to JSON files (backward compatibility)"""
    selected_hospital = data.get('selected_hospital', 'Unknown Hospital')
    
    # Create hospital-specific filename
    hospital_filename = selected_hospital.lower().replace(' ', '_').replace("'", '').replace('&', 'and')
    file_path = f'form_data_{hospital_filename}.json'
    
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
    
    # Save back to hospital-specific file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)
    
    # Also maintain a master list
    master_file_path = 'form_data_master.json'
    if os.path.exists(master_file_path):
        with open(master_file_path, 'r') as f:
            try:
                master_data = json.load(f)
            except json.JSONDecodeError:
                master_data = []
    else:
        master_data = []
    
    master_data.append(data)
    
    with open(master_file_path, 'w') as f:
        json.dump(master_data, f, indent=2)

@app.route('/view_submissions')
@require_login(['doctor', 'admin'])
def view_submissions():
    """View all form submissions (doctor and admin access)"""
    if session.get('user_role') == 'admin':
        # Admin sees all patients from all hospitals
        data = get_hospital_data()
    else:
        # Doctor sees patients from all hospitals (you can modify this to be hospital-specific)
        data = get_hospital_data()
    
    return render_template('admin.html', submissions=data)

@app.route('/doctor/patients')
@require_login(['doctor', 'admin'])
def patient_management():
    """Patient management page for doctors and admins"""
    # Get hospital filter from URL parameter
    selected_hospital = request.args.get('hospital', '')
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
    else:
        # Get data from all hospitals
        data = get_hospital_data()
    
    # Calculate statistics
    db = get_db()
    
    if db.is_connected():
        # Use MongoDB aggregation for better performance
        stats = db.get_hospital_stats(selected_hospital if selected_hospital else None)
        
        # Add today's token count
        today = datetime.now().strftime('%Y-%m-%d')
        today_data = [d for d in data if d.get('timestamp', '').startswith(today)]
        stats['today_tokens'] = len([d for d in today_data if d.get('token_number')])
        
        # Add this month count
        this_month = datetime.now().strftime('%Y-%m')
        stats['this_month'] = len([d for d in data if d.get('timestamp', '').startswith(this_month)])
    else:
        # Fallback to manual calculation
        total_patients = len(data)
        this_month = len([d for d in data if d.get('timestamp', '').startswith('2025-06')])
        male_patients = len([d for d in data if d.get('gender', '').lower() == 'male'])
        female_patients = len([d for d in data if d.get('gender', '').lower() == 'female'])
        
        # Calculate token statistics
        patients_with_tokens = len([d for d in data if d.get('token_number')])
        today_tokens = len([d for d in data if d.get('timestamp', '').startswith('2025-06-27') and d.get('token_number')])
        
        stats = {
            'total_patients': total_patients,
            'this_month': this_month,
            'male_patients': male_patients,
            'female_patients': female_patients,
            'patients_with_tokens': patients_with_tokens,
            'today_tokens': today_tokens
        }
    
    # Get list of hospitals for filter dropdown
    hospital_files = get_all_hospital_files()
    
    return render_template('patient_management.html', 
                         patients=data, 
                         stats=stats, 
                         hospital_files=hospital_files,
                         selected_hospital=selected_hospital)

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
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
    else:
        # Get data from all hospitals
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
                         selected_hospital=selected_hospital)

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
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
    else:
        # Get data from all hospitals
        data = get_hospital_data()
    
    if patient_id < len(data):
        patient = data[patient_id]
        return render_template('patient_detail.html', patient=patient, patient_id=patient_id)
    else:
        flash('Patient not found', 'error')
        return redirect(url_for('patient_management'))

@app.route('/admin/export/csv')
@require_login('admin')
def export_csv():
    """Export patient data as CSV file (Admin only)"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
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
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
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
    
    # Calculate comprehensive statistics
    total_patients = len(patient_data)
    total_doctors = len(USERS['doctors'])
    total_admins = len(USERS['admins'])
    
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
    for doctor_id in USERS['doctors']:
        doctors_info.append({
            'id': doctor_id,
            'name': doctor_id.replace('_', ' ').title(),
            'status': 'Active'  # In a real system, this would come from database
        })
    
    return render_template('admin_doctors.html', doctors=doctors_info)

@app.route('/admin/users')
@require_login('admin')
def manage_users():
    """Admin page to manage all users"""
    all_users = {
        'patients': [{'id': pid, 'name': pid.replace('_', ' ').title(), 'role': 'Patient'} for pid in USERS['patients']],
        'doctors': [{'id': did, 'name': did.replace('_', ' ').title(), 'role': 'Doctor'} for did in USERS['doctors']],
        'admins': [{'id': aid, 'name': aid.replace('_', ' ').title(), 'role': 'Admin'} for aid in USERS['admins']]
    }
    
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
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
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
    
    fieldnames = ['username', 'display_name', 'role', 'status']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write doctors data
    for doctor_id in USERS['doctors']:
        writer.writerow({
            'username': doctor_id,
            'display_name': doctor_id.replace('_', ' ').title(),
            'role': 'Doctor',
            'status': 'Active'
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
    
    fieldnames = ['username', 'display_name', 'role', 'status']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write all users data
    for role, users in USERS.items():
        for user_id in users:
            writer.writerow({
                'username': user_id,
                'display_name': user_id.replace('_', ' ').title(),
                'role': role.capitalize().rstrip('s'),  # Remove trailing 's' from role
                'status': 'Active'
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
    
    if selected_hospital:
        # Get data for specific hospital
        data = get_hospital_data(selected_hospital)
        hospital_name = selected_hospital
    else:
        # Get data from all hospitals for overview
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
                         total_patients=len(data))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)