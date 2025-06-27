#!/usr/bin/env python3

import requests
import json

def test_form_submission():
    """Test form submission to see token assignment"""
    print("=== Testing Form Submission ===")
    
    # First, select a hospital
    session = requests.Session()
    
    # Step 1: Go to hospital selection
    print("1. Accessing hospital selection...")
    hospital_response = session.get('http://127.0.0.1:5000/patient/hospital-selection')
    print(f"Hospital selection status: {hospital_response.status_code}")
    
    # Step 2: Select a hospital
    print("2. Selecting hospital...")
    hospital_data = {'hospital': 'Hospital 1'}
    hospital_submit = session.post('http://127.0.0.1:5000/patient/hospital-selection', data=hospital_data)
    print(f"Hospital selection submit status: {hospital_submit.status_code}")
    
    # Step 3: Submit patient form
    print("3. Submitting patient form...")
    form_data = {
        'firstName': 'Test',
        'lastName': 'Patient',
        'age': '30',
        'gender': 'male',
        'phone': '1234567890',
        'address': '123 Test St',
        'symptoms': 'Testing token assignment',
        'allergies': 'None',
        'medications': 'None',
        'medicalHistory': 'None',
        'emergencyName': 'Emergency Contact',
        'emergencyPhone': '0987654321',
        'emergencyRelation': 'Friend'
    }
    
    form_response = session.post('http://127.0.0.1:5000/patient/form', data=form_data)
    print(f"Form submission status: {form_response.status_code}")
    
    # Check if we can find token number in the response
    content = form_response.text
    if "token" in content.lower():
        print("✅ Found token information in response")
        # Try to extract token number
        if "token_number" in content:
            print("✅ Found token_number in response")
        else:
            print("❌ No token_number found in response")
    else:
        print("❌ No token information found in response")
    
    # Print a snippet of the response to see what we got
    print("\n--- Response snippet (first 1000 chars) ---")
    print(content[:1000])
    print("--- End snippet ---\n")

if __name__ == "__main__":
    import time
    print("Waiting 3 seconds for Flask app to be ready...")
    time.sleep(3)
    
    test_form_submission()
