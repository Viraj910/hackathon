#!/usr/bin/env python3
"""
MongoDB Connection Test and Setup Verification
Tests MongoDB connection and provides setup instructions
"""

import os
from database import DatabaseManager

def test_mongodb_connection():
    """Test MongoDB connection and provide setup instructions"""
    print("🔍 Testing MongoDB Connection...")
    print("=" * 60)
    
    try:
        # Try to connect to MongoDB
        db = DatabaseManager()
        
        if db.is_connected():
            print("✅ MongoDB is connected and ready!")
            
            # Test basic operations
            test_basic_operations(db)
            
            # Show database status
            show_database_status(db)
            
        else:
            print("❌ MongoDB is not connected")
            print("\n📋 MongoDB Installation Required:")
            show_installation_instructions()
            
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("\n📋 MongoDB Installation Required:")
        show_installation_instructions()

def test_basic_operations(db):
    """Test basic MongoDB operations"""
    print("\n🧪 Testing Basic Database Operations...")
    
    # Test data insertion
    test_patient = {
        'firstName': 'Test',
        'lastName': 'Patient',
        'age': '30',
        'gender': 'male',
        'phone': '1234567890',
        'selected_hospital': 'Test Hospital',
        'token_number': 999,
        'slot_number': 1,
        'time_range': '7:30 AM - 8:30 AM'
    }
    
    try:
        # Save test patient
        result = db.save_patient(test_patient.copy())
        if result:
            print("  ✅ Patient data insertion: SUCCESS")
            
            # Test data retrieval
            patients = db.get_patients('Test Hospital')
            if patients:
                print("  ✅ Patient data retrieval: SUCCESS")
                
                # Clean up test data
                db.db.patients.delete_many({'firstName': 'Test', 'lastName': 'Patient'})
                print("  ✅ Test data cleanup: SUCCESS")
            else:
                print("  ⚠️ Patient data retrieval: NO DATA FOUND")
        else:
            print("  ❌ Patient data insertion: FAILED")
            
    except Exception as e:
        print(f"  ❌ Database operations failed: {e}")

def show_database_status(db):
    """Show current database status and statistics"""
    print("\n📊 Database Status:")
    print("-" * 40)
    
    try:
        # Count total patients
        total_patients = len(db.get_patients())
        print(f"  📋 Total Patients: {total_patients}")
        
        # List hospitals
        hospitals = db.get_hospitals_list()
        print(f"  🏥 Hospitals with Data: {len(hospitals)}")
        
        for hospital in hospitals[:5]:  # Show first 5 hospitals
            print(f"    - {hospital['hospital_name']}: {hospital['patient_count']} patients")
        
        if len(hospitals) > 5:
            print(f"    ... and {len(hospitals) - 5} more hospitals")
        
        # Database collections info
        collections = db.db.list_collection_names()
        print(f"  📦 Collections: {collections}")
        
    except Exception as e:
        print(f"  ❌ Error getting database status: {e}")

def show_installation_instructions():
    """Show MongoDB installation instructions"""
    print("\n🚀 MongoDB Installation Instructions:")
    print("-" * 50)
    print("\n1️⃣ OPTION 1: Download MongoDB Community Server")
    print("   - Visit: https://www.mongodb.com/try/download/community")
    print("   - Select: Windows, Version 7.0+, MSI package")
    print("   - Download and run the installer")
    print("   - Choose 'Complete' installation")
    print("   - Install MongoDB as a Windows Service")
    print("   - Install MongoDB Compass (GUI tool)")
    
    print("\n2️⃣ OPTION 2: Use MongoDB Atlas (Cloud)")
    print("   - Visit: https://www.mongodb.com/cloud/atlas")
    print("   - Sign up for free account")
    print("   - Create a new cluster (free tier available)")
    print("   - Get connection string and update .env file")
    
    print("\n3️⃣ OPTION 3: Install with Chocolatey")
    print("   - Install Chocolatey first:")
    print("     Set-ExecutionPolicy Bypass -Scope Process -Force;")
    print("     [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;")
    print("     iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))")
    print("   - Then install MongoDB:")
    print("     choco install mongodb")
    
    print("\n⚙️ After Installation:")
    print("   1. Start MongoDB service:")
    print("      net start MongoDB")
    print("   2. Test connection:")
    print("      python test_mongodb.py")
    print("   3. Run migration:")
    print("      python migrate_to_mongodb.py")

def show_data_storage_locations():
    """Show where data is stored in different scenarios"""
    print("\n📂 DATA STORAGE LOCATIONS:")
    print("=" * 60)
    
    print("\n🗃️ JSON FILES (Current/Fallback):")
    json_files = [f for f in os.listdir('.') if f.startswith('form_data_') and f.endswith('.json')]
    if json_files:
        print("   📄 Hospital-specific files:")
        for file in json_files:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    import json
                    try:
                        data = json.load(f)
                        print(f"     - {file}: {len(data)} patients")
                    except:
                        print(f"     - {file}: Error reading file")
    else:
        print("   ⚠️ No JSON files found")
    
    print("\n🍃 MONGODB DATABASE (When Connected):")
    print("   📍 Database Name: hospital_management")
    print("   📦 Collections:")
    print("     - patients: Main patient records")
    print("     - doctors: Doctor accounts (future)")
    print("     - admins: Admin accounts (future)")
    print("   🔗 Connection: mongodb://localhost:27017/")
    print("   📁 Data Location (Windows): C:\\data\\db\\")
    
    print("\n🌐 MONGODB ATLAS (Cloud Option):")
    print("   📍 Cluster: Your-Cluster-Name")
    print("   🔗 Connection: mongodb+srv://...")
    print("   📁 Data Location: AWS/Azure/GCP Cloud")

if __name__ == "__main__":
    print("🏥 HOSPITAL MANAGEMENT SYSTEM")
    print("📊 MongoDB Connection Test & Setup Guide")
    print("=" * 60)
    
    # Test MongoDB connection
    test_mongodb_connection()
    
    # Show data storage information
    show_data_storage_locations()
    
    print("\n" + "=" * 60)
    print("✅ Test completed! Check the results above.")
    print("📚 See MONGODB_SETUP.md for detailed setup instructions.")
