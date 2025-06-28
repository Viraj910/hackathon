from database import get_db

# Fix doctor hospital assignments
db = get_db()
if db.is_connected():
    print('Assigning hospitals to doctors...')
    
    # Assign hospitals to doctors
    assignments = [
        ('dr_smith', 'Hospital 1'),
        ('dr_johnson', 'Hospital 2'),
        ('dr_brown', 'Hospital 1'),
        ('dr_davis', 'Women\'s Health Clinic')
    ]
    
    for username, hospital in assignments:
        result = db.update_user(username, 'doctor', {'assigned_hospital': hospital})
        if result:
            print(f'✅ Assigned {username} to {hospital}')
        else:
            print(f'❌ Failed to assign {username} to {hospital}')
    
    print('\nVerifying assignments:')
    doctors = db.get_all_users('doctor')
    for doctor in doctors:
        hospital = doctor.get('assigned_hospital', 'NOT ASSIGNED')
        print(f'Doctor: {doctor.get("username", "N/A")} - Hospital: {hospital}')

else:
    print('MongoDB not connected')
