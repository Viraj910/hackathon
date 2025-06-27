#!/usr/bin/env python3
"""
MongoDB Data Viewer
Shows exactly what data is stored in your MongoDB database
"""

from database import DatabaseManager
import json

def show_mongodb_data():
    print("📊 MongoDB Data Viewer")
    print("=" * 50)
    
    db = DatabaseManager()
    
    if not db.is_connected():
        print("❌ MongoDB is not connected!")
        return
    
    print("✅ Connected to MongoDB")
    print(f"📍 Database: hospital_management")
    print(f"🔗 Connection: mongodb://localhost:27017/")
    print(f"📁 Physical Location: C:\\Program Files\\MongoDB\\Server\\8.0\\data\\")
    
    # Show all patients
    patients = db.get_patients()
    print(f"\n👥 Total Patients: {len(patients)}")
    
    if patients:
        print("\n📋 Patient Details:")
        print("-" * 80)
        
        for i, patient in enumerate(patients, 1):
            print(f"\n{i}. Patient Record:")
            print(f"   Name: {patient.get('firstName', '')} {patient.get('lastName', '')}")
            print(f"   Hospital: {patient.get('selected_hospital', 'Unknown')}")
            print(f"   Token: {patient.get('token_number', 'N/A')}")
            print(f"   Slot: {patient.get('slot_number', 'N/A')} ({patient.get('time_range', 'N/A')})")
            print(f"   Age: {patient.get('age', 'N/A')}")
            print(f"   Gender: {patient.get('gender', 'N/A')}")
            print(f"   Phone: {patient.get('phone', 'N/A')}")
            print(f"   Symptoms: {patient.get('symptoms', 'N/A')}")
            print(f"   Timestamp: {patient.get('timestamp', 'N/A')}")
            print(f"   MongoDB ID: {patient.get('_id', 'N/A')}")
    
    # Show collection statistics
    print(f"\n📊 Database Statistics:")
    try:
        # Try to get collection stats if available
        stats = db.get_hospital_stats()
        print(f"   Total Patients: {stats.get('total_patients', 0)}")
        print(f"   Male Patients: {stats.get('male_patients', 0)}")
        print(f"   Female Patients: {stats.get('female_patients', 0)}")
    except:
        print(f"   Total Patients: {len(patients)}")
    
    # Show hospitals
    print(f"\n🏥 Hospitals with Data:")
    hospitals = {}
    for patient in patients:
        hospital = patient.get('selected_hospital', 'Unknown')
        hospitals[hospital] = hospitals.get(hospital, 0) + 1
    
    for hospital, count in hospitals.items():
        print(f"   {hospital}: {count} patients")
    
    print(f"\n📁 Data Storage Information:")
    print(f"   Physical Files: C:\\Program Files\\MongoDB\\Server\\8.0\\data\\")
    print(f"   Collection Files: collection-*.wt (binary format)")
    print(f"   Index Files: index-*.wt (for fast queries)")
    print(f"   Logs: C:\\Program Files\\MongoDB\\Server\\8.0\\log\\mongod.log")

if __name__ == "__main__":
    show_mongodb_data()
