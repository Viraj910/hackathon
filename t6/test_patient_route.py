#!/usr/bin/env python3

import requests
import json

def test_patient_management_route():
    """Test the patient management route directly"""
    print("=== Testing Patient Management Route ===")
    
    # Test with doctor credentials
    session = requests.Session()
    
    # Login as doctor first
    login_data = {
        'username': 'dr_johnson',
        'password': 'doctor123'
    }
    
    print("1. Logging in as doctor...")
    login_response = session.post('http://127.0.0.1:5000/doctor/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("2. Accessing patient management...")
        patient_mgmt_response = session.get('http://127.0.0.1:5000/doctor/patients')
        print(f"Patient management status: {patient_mgmt_response.status_code}")
        
        # Check if we can find patient data in the response
        content = patient_mgmt_response.text
        if "no patient records" in content.lower():
            print("❌ Found 'no patient records' message")
        else:
            print("✅ Did not find 'no patient records' message")
            
        # Look for patient data
        if "patient_data" in content or "John Doe" in content:
            print("✅ Found patient data in response")
        else:
            print("❌ No patient data found in response")
            
        # Print a snippet of the response
        print("\n--- Response snippet (first 500 chars) ---")
        print(content[:500])
        print("--- End snippet ---\n")
    else:
        print("❌ Failed to login")

def test_admin_reports_route():
    """Test the admin reports route directly"""
    print("=== Testing Admin Reports Route ===")
    
    session = requests.Session()
    
    # Login as admin first
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("1. Logging in as admin...")
    login_response = session.post('http://127.0.0.1:5000/admin/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("2. Accessing admin reports...")
        reports_response = session.get('http://127.0.0.1:5000/admin/patients')
        print(f"Reports status: {reports_response.status_code}")
        
        # Check content
        content = reports_response.text
        if "no patient records" in content.lower():
            print("❌ Found 'no patient records' message")
        else:
            print("✅ Did not find 'no patient records' message")
            
        # Look for patient data
        if "patient_data" in content or "John Doe" in content:
            print("✅ Found patient data in response")
        else:
            print("❌ No patient data found in response")
            
        print("\n--- Response snippet (first 500 chars) ---")
        print(content[:500])
        print("--- End snippet ---\n")
    else:
        print("❌ Failed to login")

if __name__ == "__main__":
    import time
    print("Waiting 3 seconds for Flask app to start...")
    time.sleep(3)
    
    test_patient_management_route()
    print()
    test_admin_reports_route()
