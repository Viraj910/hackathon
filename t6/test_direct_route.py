"""
Direct test of the doctor/patients route to see what's being returned
"""

import requests
import sys

def test_doctor_patients_route():
    """Test the doctor patients route directly"""
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Login as doctor first
        print("1. Logging in as doctor...")
        login_data = {
            'username': 'dr_smith',
            'password': 'doctor123'
        }
        response = session.post(f"{base_url}/doctor/login", data=login_data)
        print(f"   Login response: {response.status_code}")
        
        # Access the patients page
        print("2. Accessing /doctor/patients...")
        response = session.get(f"{base_url}/doctor/patients")
        print(f"   Patients page response: {response.status_code}")
        
        if response.status_code == 200:
            # Check what's in the response
            content = response.text
            
            # Look for key indicators
            if 'No patient records have been submitted yet' in content:
                print("   ❌ Found 'No patient records have been submitted yet'")
            
            # Look for any patient data
            if 'fghjk' in content or 'viraj' in content or 'Test Patient' in content:
                print("   ✅ Found patient data in response!")
            else:
                print("   ❌ No patient data found in response")
            
            # Look for the patients variable in template context
            if 'patients' in content.lower():
                print("   ℹ️ 'patients' mentioned in content")
            
            # Check if template shows statistics
            if 'Total Patients' in content:
                print("   ℹ️ Statistics section found")
            
            # Look for specific error patterns
            if 'error' in content.lower():
                print("   ⚠️ Error mentioned in content")
            
            # Print a relevant snippet
            print("\n   Content analysis:")
            print("   =================")
            
            # Find the patient list section
            if '<div id="patientList">' in content:
                start = content.find('<div id="patientList">')
                end = content.find('</div>', start) + 6
                snippet = content[start:end]
                print(f"   Patient list section: {snippet[:200]}...")
            elif 'No Patients Found' in content:
                start = content.find('No Patients Found') - 50
                end = start + 200
                snippet = content[start:end]
                print(f"   No patients section: {snippet}")
            else:
                print("   Could not find patient list or no patients section")
        
        else:
            print(f"   ❌ Failed to access patients page: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_doctor_patients_route()
