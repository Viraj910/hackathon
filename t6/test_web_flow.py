"""
Test form submission and admin/doctor viewing
This script will test the complete flow from form submission to viewing in admin panel
"""

import requests
import json
from datetime import datetime

def test_complete_flow():
    """Test the complete flow from patient submission to admin viewing"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Complete Patient Data Flow")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Step 1: Test if server is running
        print("1. Testing if server is running...")
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server not accessible: {response.status_code}")
            return False
        
        # Step 2: Submit a patient form
        print("\n2. Submitting a test patient form...")
        
        # First, select a hospital (simulate the patient flow)
        hospital_data = {
            'hospital': 'Hospital 1'
        }
        response = session.post(f"{base_url}/patient/hospital-selection", data=hospital_data)
        print(f"   Hospital selection: {response.status_code}")
        
        # Now submit patient data
        patient_data = {
            'firstName': 'Test',
            'lastName': 'Patient',
            'age': '30',
            'gender': 'male',
            'phone': '1234567890',
            'address': '123 Test St',
            'symptoms': 'Test symptoms for automated test',
            'allergies': 'None',
            'medications': 'None',
            'medicalHistory': 'None',
            'emergencyName': 'Emergency Contact',
            'emergencyPhone': '0987654321',
            'emergencyRelation': 'Friend'
        }
        
        response = session.post(f"{base_url}/patient/form", data=patient_data)
        if response.status_code == 200:
            print("   ✅ Patient form submitted successfully")
        else:
            print(f"   ❌ Patient form submission failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        # Step 3: Try to access doctor login
        print("\n3. Testing doctor login...")
        login_data = {
            'username': 'dr_smith',
            'password': 'doctor123'
        }
        response = session.post(f"{base_url}/doctor/login", data=login_data)
        if response.status_code == 200 or response.status_code == 302:  # 302 is redirect after successful login
            print("   ✅ Doctor login successful")
        else:
            print(f"   ❌ Doctor login failed: {response.status_code}")
        
        # Step 4: Access patient management page
        print("\n4. Accessing patient management page...")
        response = session.get(f"{base_url}/doctor/patients")
        if response.status_code == 200:
            print("   ✅ Patient management page accessible")
            
            # Check if patient data appears in the response
            response_text = response.text.lower()
            if 'no patient records have been submitted yet' in response_text:
                print("   ❌ Page shows 'no patient records have been submitted yet'")
                return False
            elif 'test patient' in response_text or 'test' in response_text:
                print("   ✅ Patient data appears on the page!")
                return True
            else:
                print("   ⚠️ Page loaded but patient data status unclear")
                # Print a snippet of the response to debug
                print(f"   Response snippet: {response_text[response_text.find('<body'):response_text.find('<body')+500]}...")
        else:
            print(f"   ❌ Patient management page not accessible: {response.status_code}")
        
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_mongodb_data_directly():
    """Test MongoDB data directly to ensure it's there"""
    print("\n🔍 Testing MongoDB Data Directly")
    print("=" * 30)
    
    try:
        from database import get_db
        db = get_db()
        
        if db.is_connected():
            patients = db.get_patients()
            print(f"📊 MongoDB has {len(patients)} patients")
            
            if patients:
                latest_patient = patients[0]
                print(f"   Latest: {latest_patient.get('firstName', 'Unknown')} {latest_patient.get('lastName', '')}")
                print(f"   Hospital: {latest_patient.get('selected_hospital', 'Unknown')}")
                print(f"   Timestamp: {latest_patient.get('timestamp', 'Unknown')}")
                return True
            else:
                print("   No patients found in MongoDB")
                return False
        else:
            print("❌ MongoDB not connected")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing MongoDB: {e}")
        return False

if __name__ == "__main__":
    # Test MongoDB first
    mongo_success = test_mongodb_data_directly()
    
    # Test web flow
    web_success = test_complete_flow()
    
    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS:")
    print(f"   MongoDB Data: {'✅ Available' if mongo_success else '❌ Not Available'}")
    print(f"   Web Interface: {'✅ Working' if web_success else '❌ Not Working'}")
    
    if mongo_success and not web_success:
        print("\n🔧 DIAGNOSIS: Data is in MongoDB but not showing in web interface")
        print("   This suggests an issue with the Flask app's data retrieval or template rendering")
    elif not mongo_success:
        print("\n🔧 DIAGNOSIS: No data in MongoDB")
        print("   Need to submit patient forms first")
    else:
        print("\n🎉 Everything is working correctly!")
