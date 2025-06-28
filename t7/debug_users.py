from database import get_db

db = get_db()
if db.is_connected():
    print('=== DOCTORS AND THEIR HOSPITAL ASSIGNMENTS ===')
    doctors = db.get_all_users('doctor')
    for doctor in doctors:
        hospital = doctor.get('assigned_hospital', 'NOT ASSIGNED')
        print(f'Doctor: {doctor.get("username", "N/A")} - Hospital: {hospital}')
    
    print('\n=== ADMINS ===')
    admins = db.get_all_users('admin')
    for admin in admins:
        hospital = admin.get('assigned_hospital', 'ALL HOSPITALS')
        print(f'Admin: {admin.get("username", "N/A")} - Hospital: {hospital}')
else:
    print('MongoDB not connected')
