#!/usr/bin/env python3

import requests
import re

def test_form_submission_detailed():
    """Test form submission and extract all data being passed to template"""
    print("=== Detailed Form Submission Test ===")
    
    session = requests.Session()
    
    # Step 1: Hospital selection
    print("1. Selecting hospital...")
    hospital_data = {'hospital': 'Hospital 1'}
    hospital_response = session.post('http://127.0.0.1:5000/patient/hospital-selection', data=hospital_data)
    print(f"Hospital selection status: {hospital_response.status_code}")
    
    # Step 2: Submit patient form
    print("2. Submitting patient form...")
    form_data = {
        'firstName': 'TestToken',
        'lastName': 'Patient',
        'age': '25',
        'gender': 'female',
        'phone': '555-1234',
        'address': '123 Test Ave',
        'symptoms': 'Testing token assignment functionality',
        'allergies': 'None',
        'medications': 'None', 
        'medicalHistory': 'None',
        'emergencyName': 'Test Contact',
        'emergencyPhone': '555-5678',
        'emergencyRelation': 'Spouse'
    }
    
    form_response = session.post('http://127.0.0.1:5000/patient/form', data=form_data)
    print(f"Form submission status: {form_response.status_code}")
    
    # Analyze the response content
    content = form_response.text
    
    # Look for specific data patterns
    print("\n--- Analysis ---")
    
    # Check for token-related content
    token_patterns = [
        r'token_number["\']?\s*:\s*["\']?(\d+)',
        r'Token Number["\']?[^>]*>([^<]+)',
        r'token["\']?\s*[:\=]\s*["\']?(\d+)',
        r'Your Appointment Details'
    ]
    
    found_tokens = []
    for pattern in token_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_tokens.extend(matches)
            print(f"✅ Found pattern '{pattern}': {matches}")
        else:
            print(f"❌ Pattern '{pattern}': No matches")
    
    # Check if the token section is being rendered
    if 'Your Appointment Details' in content:
        print("✅ Token section is being rendered")
    else:
        print("❌ Token section is NOT being rendered")
    
    # Look for hospital information
    if 'Hospital 1' in content:
        print("✅ Hospital information found")
    else:
        print("❌ Hospital information not found")
    
    # Look for patient name
    if 'TestToken' in content:
        print("✅ Patient name found")
    else:
        print("❌ Patient name not found")
    
    print(f"\nFound token numbers: {found_tokens}")
    
    # Print more of the response to see the actual content
    print("\n--- Full Response (first 2000 chars) ---")
    print(content[:2000])
    print("--- End Response ---")

if __name__ == "__main__":
    import time
    print("Waiting 3 seconds for Flask app to be ready...")
    time.sleep(3)
    
    test_form_submission_detailed()
