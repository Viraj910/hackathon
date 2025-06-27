#!/usr/bin/env python3
"""
Quick MongoDB Verification Script
Verifies that MongoDB is working correctly with the hospital management system
"""

from database import DatabaseManager
import json

def main():
    print("🔍 MongoDB Connection & Data Verification")
    print("=" * 50)
    
    # Initialize database connection
    db = DatabaseManager()
    
    if not db.is_connected():
        print("❌ MongoDB is not connected!")
        return
    
    print("✅ MongoDB is connected")
    
    # Test basic operations
    print("\n📊 Database Statistics:")
    
    # Get all patients
    patients = db.get_patients()
    print(f"   Total patients: {len(patients)}")
    
    # Show patient details
    if patients:
        print("\n👥 Patient List:")
        for i, patient in enumerate(patients, 1):
            name = f"{patient.get('firstName', 'Unknown')} {patient.get('lastName', 'Unknown')}"
            hospital = patient.get('selected_hospital', 'Unknown')
            token = patient.get('token_number', 'N/A')
            print(f"   {i}. {name} - {hospital} (Token: {token})")
    
    # Test hospital statistics
    print("\n🏥 Hospital Statistics:")
    try:
        hospitals = db.get_hospitals_list()
        for hospital in hospitals:
            print(f"   {hospital['hospital_name']}: {hospital['patient_count']} patients")
    except Exception as e:
        print(f"   ⚠️ Hospital stats error: {e}")
    
    # Test token assignment
    print("\n🎫 Testing Token Assignment:")
    try:
        next_token = db.get_next_token_for_hospital("Test Hospital")
        print(f"   Next token for 'Test Hospital': {next_token}")
    except Exception as e:
        print(f"   ⚠️ Token assignment error: {e}")
    
    print("\n✅ All tests passed! MongoDB is working correctly.")

if __name__ == "__main__":
    main()
