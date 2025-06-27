from database import get_db

def check_patient_data():
    db = get_db()
    patients = db.get_patients()
    print(f"Total patients in MongoDB: {len(patients)}")
    
    if patients:
        print("First 5 patients:")
        for i, patient in enumerate(patients[:5]):
            name = f"{patient.get('firstName', 'Unknown')} {patient.get('lastName', '')}"
            hospital = patient.get('selected_hospital', 'Unknown')
            timestamp = patient.get('timestamp', 'Unknown')
            print(f"{i+1}. {name} at {hospital} ({timestamp})")
    else:
        print("No patients found in MongoDB")

if __name__ == "__main__":
    check_patient_data()
