"""
Test MongoDB Integration
Verify that all website data is properly stored and retrieved from MongoDB
"""

from database import get_db
from datetime import datetime

def test_user_authentication():
    """Test user authentication from MongoDB"""
    print("🔐 Testing User Authentication...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected")
        return False
    
    # Test each role
    test_users = [
        ('admin', 'admin123', 'admin'),
        ('dr_smith', 'doctor123', 'doctor'),
        ('patient1', 'pass123', 'patient')
    ]
    
    success_count = 0
    for username, password, role in test_users:
        user = db.authenticate_user(username, password, role)
        if user:
            print(f"✅ {role.title()} login successful: {username}")
            success_count += 1
        else:
            print(f"❌ {role.title()} login failed: {username}")
    
    print(f"👤 Authentication test: {success_count}/{len(test_users)} successful")
    return success_count == len(test_users)

def test_hospital_configuration():
    """Test hospital configuration data"""
    print("\n🏥 Testing Hospital Configuration...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected")
        return False
    
    hospitals = db.get_all_hospitals_config()
    print(f"📊 Hospitals in database: {len(hospitals)}")
    
    for hospital in hospitals[:3]:  # Show first 3
        print(f"   - {hospital.get('name', 'Unknown')}: {hospital.get('description', 'No description')}")
    
    return len(hospitals) > 0

def test_system_configuration():
    """Test system configuration"""
    print("\n⚙️ Testing System Configuration...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected")
        return False
    
    # Test getting specific configs
    test_configs = [
        'app_name',
        'app_version',
        'max_patients_per_slot',
        'enable_token_system'
    ]
    
    success_count = 0
    for config_key in test_configs:
        value = db.get_config(config_key)
        if value is not None:
            print(f"✅ {config_key}: {value}")
            success_count += 1
        else:
            print(f"❌ {config_key}: Not found")
    
    print(f"🔧 Configuration test: {success_count}/{len(test_configs)} successful")
    return success_count == len(test_configs)

def test_patient_data():
    """Test patient data storage and retrieval"""
    print("\n📋 Testing Patient Data...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected")
        return False
    
    # Get all patients
    patients = db.get_patients()
    print(f"👥 Total patients in database: {len(patients)}")
    
    if patients:
        recent_patient = patients[0]  # Most recent
        print(f"📝 Most recent patient: {recent_patient.get('firstName', 'Unknown')} {recent_patient.get('lastName', '')}")
        print(f"🏥 Hospital: {recent_patient.get('selected_hospital', 'Unknown')}")
        
        # Test hospital-specific data
        hospital_name = recent_patient.get('selected_hospital')
        if hospital_name:
            hospital_patients = db.get_patients(hospital_name)
            print(f"🏥 Patients at {hospital_name}: {len(hospital_patients)}")
    
    return len(patients) > 0

def test_data_integrity():
    """Test data integrity and relationships"""
    print("\n🔍 Testing Data Integrity...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected")
        return False
    
    # Check collections exist
    collections = db.db.list_collection_names()
    expected_collections = ['patients', 'doctors', 'admins', 'patients_users', 'hospitals', 'system_config']
    
    missing_collections = []
    for collection in expected_collections:
        if collection in collections:
            count = db.db[collection].count_documents({})
            print(f"✅ {collection}: {count} documents")
        else:
            missing_collections.append(collection)
            print(f"❌ {collection}: Missing")
    
    if missing_collections:
        print(f"⚠️ Missing collections: {missing_collections}")
        return False
    
    print("✅ All collections present and populated")
    return True

def performance_test():
    """Test database performance"""
    print("\n⚡ Testing Database Performance...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected")
        return False
    
    # Time patient retrieval
    start_time = datetime.now()
    patients = db.get_patients()
    end_time = datetime.now()
    
    query_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
    print(f"🚀 Patient query time: {query_time:.2f}ms for {len(patients)} records")
    
    # Time user authentication
    start_time = datetime.now()
    user = db.authenticate_user('admin', 'admin123', 'admin')
    end_time = datetime.now()
    
    auth_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
    print(f"🔐 Authentication time: {auth_time:.2f}ms")
    
    return query_time < 1000 and auth_time < 500  # Should be under 1 second and 500ms respectively

def main():
    """Run all tests"""
    print("🧪 MongoDB Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("User Authentication", test_user_authentication),
        ("Hospital Configuration", test_hospital_configuration),
        ("System Configuration", test_system_configuration),
        ("Patient Data", test_patient_data),
        ("Data Integrity", test_data_integrity),
        ("Performance", performance_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MongoDB integration is working perfectly.")
        print("✅ Your website is now fully powered by MongoDB!")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
