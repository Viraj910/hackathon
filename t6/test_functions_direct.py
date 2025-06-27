"""
Direct function test to isolate the issue
"""

import sys
import os
sys.path.append('.')

# Import the app and test the functions directly
from app import get_hospital_data, get_all_hospital_files, get_db
from database import DatabaseManager

def test_functions_directly():
    """Test the data functions directly without Flask context"""
    
    print("🧪 Testing Functions Directly")
    print("=" * 40)
    
    print("1. Testing get_db()...")
    db = get_db()
    print(f"   Database connected: {db.is_connected()}")
    
    if db.is_connected():
        patients = db.get_patients()
        print(f"   Direct db.get_patients(): {len(patients)} patients")
        for i, patient in enumerate(patients[:2]):
            print(f"   - {patient.get('firstName', 'Unknown')} at {patient.get('selected_hospital', 'Unknown')}")
    
    print("\n2. Testing get_hospital_data()...")
    data = get_hospital_data()
    print(f"   get_hospital_data() returned: {len(data)} patients")
    for i, patient in enumerate(data[:2]):
        print(f"   - {patient.get('firstName', 'Unknown')} at {patient.get('selected_hospital', 'Unknown')}")
    
    print("\n3. Testing get_all_hospital_files()...")
    hospital_files = get_all_hospital_files()
    print(f"   get_all_hospital_files() returned: {len(hospital_files)} hospitals")
    for hospital in hospital_files:
        print(f"   - {hospital.get('hospital_name', 'Unknown')}: {hospital.get('patient_count', 0)} patients")
    
    print("\n4. Testing get_hospital_data() with specific hospital...")
    if data:
        first_hospital = data[0].get('selected_hospital')
        hospital_data = get_hospital_data(first_hospital)
        print(f"   Data for '{first_hospital}': {len(hospital_data)} patients")
    
    return len(data) > 0

if __name__ == "__main__":
    success = test_functions_directly()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Functions are working correctly!")
        print("📝 The issue must be in the Flask route or template rendering")
    else:
        print("❌ Functions are not returning data")
        print("📝 The issue is in the data retrieval functions")
