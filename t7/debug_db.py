from database import get_db

db = get_db()
if db.is_connected():
    print('=== HOSPITALS ===')
    hospitals = db.get_all_hospitals_config()
    for h in hospitals:
        print(f'ID: {h.get("hospital_id", "N/A")}, Name: {h.get("name", "N/A")}')
    
    print('\n=== PATIENTS ===')
    patients = db.get_patients()
    print(f'Total patients: {len(patients)}')
    for i, p in enumerate(patients):
        print(f'{i+1}. {p.get("firstName", "N/A")} {p.get("lastName", "N/A")} - Hospital: {p.get("selected_hospital", "N/A")} - Token: {p.get("token_number", "N/A")}')
        print(f'    Timestamp: {p.get("timestamp", "N/A")}')
else:
    print('MongoDB not connected')
