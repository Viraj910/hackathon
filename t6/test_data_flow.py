"""
Simple test to verify patient data flow
Tests the exact same data retrieval used by admin/doctor dashboards
"""

import sys
sys.path.append('.')
from app import get_hospital_data, get_all_hospital_files
from database import get_db

def test_data_flow():
    print("🔍 Testing Patient Data Flow")
    print("=" * 50)
    
    # Test 1: Direct database access
    print("1. Direct Database Access:")
    db = get_db()
    if db.is_connected():
        patients = db.get_patients()
        print(f"   ✅ MongoDB connected: {len(patients)} patients found")
        for i, patient in enumerate(patients[:3]):
            print(f"   - Patient {i+1}: {patient.get('firstName', 'Unknown')} {patient.get('lastName', '')} at {patient.get('selected_hospital', 'Unknown')}")
    else:
        print("   ❌ MongoDB not connected")
    
    print()
    
    # Test 2: App's get_hospital_data function
    print("2. App's get_hospital_data() function:")
    data = get_hospital_data()
    print(f"   📊 get_hospital_data() returns: {len(data)} patients")
    for i, patient in enumerate(data[:3]):
        print(f"   - Patient {i+1}: {patient.get('firstName', 'Unknown')} {patient.get('lastName', '')} at {patient.get('selected_hospital', 'Unknown')}")
    
    print()
    
    # Test 3: Hospital files (for dropdown)
    print("3. Hospital Files (for dropdown):")
    hospital_files = get_all_hospital_files()
    print(f"   🏥 get_all_hospital_files() returns: {len(hospital_files)} hospitals")
    for hospital in hospital_files[:3]:
        print(f"   - {hospital.get('hospital_name', 'Unknown')}: {hospital.get('patient_count', 0)} patients")
    
    print()
    
    # Test 4: Specific hospital data
    print("4. Specific Hospital Data:")
    if data:
        first_hospital = data[0].get('selected_hospital', 'Unknown')
        hospital_data = get_hospital_data(first_hospital)
        print(f"   🏥 Data for '{first_hospital}': {len(hospital_data)} patients")
        for patient in hospital_data[:2]:
            print(f"   - {patient.get('firstName', 'Unknown')} {patient.get('lastName', '')}")
    else:
        print("   ⚠️ No data to test specific hospital")
    
    print()
    print("=" * 50)
    
    # Summary
    if len(data) > 0:
        print("🎉 SUCCESS: Patient data is available and should appear in admin/doctor dashboards!")
        print(f"📊 Total patients that should be visible: {len(data)}")
        
        # Show what templates should receive
        print("\n📋 Data that templates should receive:")
        print(f"   - patients: {len(data)} items")
        print(f"   - hospital_files: {len(hospital_files)} items")
        print(f"   - stats: calculated from {len(data)} patients")
        
        return True
    else:
        print("❌ ISSUE: No patient data found - this explains why templates show 'no submissions'")
        return False

if __name__ == "__main__":
    test_data_flow()
