from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, make_response
import json
import os
import csv
from datetime import datetime
from functools import wraps
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

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
@require_login(['doctor', 'admin'])
def view_submissions():
    """View all form submissions (doctor and admin access)"""
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
@require_login(['doctor', 'admin'])
def patient_management():
    """Patient management page for doctors and admins"""
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
@require_login(['doctor', 'admin'])
def patient_detail(patient_id):
    """View detailed information for a specific patient (doctor and admin access)"""
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
        'timestamp', 'firstName', 'lastName', 'age', 'gender', 'phone', 
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
        'timestamp', 'firstName', 'lastName', 'age', 'gender', 'phone', 
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
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                patient_data = json.load(f)
            except json.JSONDecodeError:
                patient_data = []
    else:
        patient_data = []
    
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
    
    stats = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'recent_patients': recent_patients,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'age_groups': age_groups
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
        'timestamp', 'firstName', 'lastName', 'age', 'gender', 
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)