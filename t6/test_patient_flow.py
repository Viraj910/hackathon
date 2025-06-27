"""
Test script to verify patient data flow
Tests that patient data appears in doctor and admin spaces
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_patient_submission():
    """Submit a test patient form"""
    print("🧪 Testing patient form submission...")
    
    # First, go to hospital selection
    session = requests.Session()
    
    # Step 1: Select a hospital
    hospital_data = {
        'hospital': 'Hospital 1'
    }
    
    response = session.post(f"{BASE_URL}/patient/hospital-selection", data=hospital_data)
    if response.status_code == 200:
        print("✅ Hospital selected successfully")
    else:
        print(f"❌ Hospital selection failed: {response.status_code}")
        return False
    
    # Step 2: Submit patient form
    patient_data = {
        'firstName': 'Test',
        'lastName': 'Patient',
        'age': '30',
        'gender': 'male',
        'phone': '555-TEST-123',
        'address': '123 Test Street, Test City',
        'symptoms': 'Test symptoms for verification',
        'allergies': 'No known allergies',
        'medications': 'None',
        'medicalHistory': 'Test medical history',
        'emergencyName': 'Test Contact',
        'emergencyPhone': '555-TEST-456',
        'emergencyRelation': 'Friend'
    }
    
    response = session.post(f"{BASE_URL}/patient/form", data=patient_data)
    if response.status_code == 200:
        print("✅ Patient form submitted successfully")
        return True
    else:
        print(f"❌ Patient form submission failed: {response.status_code}")
        print(response.text[:500])  # Print first 500 chars of response
        return False

def test_doctor_login_and_view():
    """Test doctor login and patient data visibility"""
    print("\n👨‍⚕️ Testing doctor login and patient data access...")
    
    session = requests.Session()
    
    # Step 1: Login as doctor
    doctor_data = {
        'username': 'dr_smith',
        'password': 'doctor123'
    }
    
    response = session.post(f"{BASE_URL}/doctor/login", data=doctor_data)
    if response.status_code == 200 and 'Welcome back' in response.text:
        print("✅ Doctor login successful")
    else:
        print(f"❌ Doctor login failed: {response.status_code}")
        return False
    
    # Step 2: Access patient management page
    response = session.get(f"{BASE_URL}/doctor/patients")
    if response.status_code == 200:
        print("✅ Doctor can access patient management page")
        
        # Check if our test patient appears in the response
        if 'Test Patient' in response.text or 'Test symptoms' in response.text:
            print("✅ Test patient data visible to doctor")
            return True
        else:
            print("❌ Test patient data NOT visible to doctor")
            # Check what patients are visible
            if 'fghjk' in response.text or 'viraj' in response.text:
                print("ℹ️ Other patient data is visible, but test patient is missing")
            else:
                print("ℹ️ No patient data visible at all")
            return False
    else:
        print(f"❌ Doctor cannot access patient management: {response.status_code}")
        return False

def test_admin_login_and_view():
    """Test admin login and patient data visibility"""
    print("\n👨‍💼 Testing admin login and patient data access...")
    
    session = requests.Session()
    
    # Step 1: Login as admin
    admin_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = session.post(f"{BASE_URL}/admin/login", data=admin_data)
    if response.status_code == 200 and 'Welcome back' in response.text:
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
    
    # Step 2: Access admin dashboard
    response = session.get(f"{BASE_URL}/admin/dashboard")
    if response.status_code == 200:
        print("✅ Admin can access dashboard")
        
        # Check patient count in dashboard
        if 'total_patients' in response.text or 'Test Patient' in response.text:
            print("✅ Patient data visible in admin dashboard")
        else:
            print("⚠️ Patient data might not be visible in admin dashboard")
    
    # Step 3: Access patient management page
    response = session.get(f"{BASE_URL}/admin/patients")
    if response.status_code == 200:
        print("✅ Admin can access patient management page")
        
        # Check if our test patient appears in the response
        if 'Test Patient' in response.text or 'Test symptoms' in response.text:
            print("✅ Test patient data visible to admin")
            return True
        else:
            print("❌ Test patient data NOT visible to admin")
            # Check what patients are visible
            if 'fghjk' in response.text or 'viraj' in response.text:
                print("ℹ️ Other patient data is visible, but test patient is missing")
            else:
                print("ℹ️ No patient data visible at all")
            return False
    else:
        print(f"❌ Admin cannot access patient management: {response.status_code}")
        return False

def check_mongodb_data():
    """Check MongoDB data directly"""
    print("\n🗄️ Checking MongoDB data directly...")
    try:
        from database import get_db
        db = get_db()
        patients = db.get_patients()
        
        print(f"Total patients in MongoDB: {len(patients)}")
        
        # Look for our test patient
        test_patient = None
        for patient in patients:
            if patient.get('firstName') == 'Test' and patient.get('lastName') == 'Patient':
                test_patient = patient
                break
        
        if test_patient:
            print("✅ Test patient found in MongoDB")
            print(f"   - Name: {test_patient.get('firstName')} {test_patient.get('lastName')}")
            print(f"   - Hospital: {test_patient.get('selected_hospital')}")
            print(f"   - Symptoms: {test_patient.get('symptoms')}")
            print(f"   - Timestamp: {test_patient.get('timestamp')}")
            return True
        else:
            print("❌ Test patient NOT found in MongoDB")
            
            # Show what's in MongoDB
            print("Patients currently in MongoDB:")
            for i, patient in enumerate(patients[:5]):
                name = f"{patient.get('firstName', 'Unknown')} {patient.get('lastName', '')}"
                hospital = patient.get('selected_hospital', 'Unknown')
                print(f"   {i+1}. {name} at {hospital}")
            
            return False
    except Exception as e:
        print(f"❌ Error checking MongoDB: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting patient data flow tests...")
    print("=" * 60)
    
    # Test 1: Submit patient form
    submission_success = test_patient_submission()
    
    # Test 2: Check MongoDB directly
    mongodb_success = check_mongodb_data()
    
    # Test 3: Test doctor access
    doctor_success = test_doctor_login_and_view()
    
    # Test 4: Test admin access
    admin_success = test_admin_login_and_view()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"  Patient Form Submission: {'✅ PASS' if submission_success else '❌ FAIL'}")
    print(f"  MongoDB Data Storage:    {'✅ PASS' if mongodb_success else '❌ FAIL'}")
    print(f"  Doctor Data Access:      {'✅ PASS' if doctor_success else '❌ FAIL'}")
    print(f"  Admin Data Access:       {'✅ PASS' if admin_success else '❌ FAIL'}")
    
    if all([submission_success, mongodb_success, doctor_success, admin_success]):
        print("\n🎉 ALL TESTS PASSED! Patient data flow is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED! There are issues with patient data flow.")
        print("\nPossible issues to investigate:")
        if not submission_success:
            print("  - Patient form submission is not working")
        if not mongodb_success:
            print("  - Data is not being saved to MongoDB properly")
        if not doctor_success:
            print("  - Doctors cannot see patient data")
        if not admin_success:
            print("  - Admins cannot see patient data")
    
    print("=" * 60)

if __name__ == "__main__":
    # Wait a moment for the server to be ready
    import time
    time.sleep(2)
    main()
