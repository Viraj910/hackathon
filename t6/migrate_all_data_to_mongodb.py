"""
Complete Data Migration Script
Migrates all website data from hardcoded values to MongoDB
"""

from database import get_db
from datetime import datetime
import json
import os

def migrate_users_to_mongodb():
    """Migrate hardcoded users to MongoDB"""
    print("🔄 Migrating users to MongoDB...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected. Cannot migrate users.")
        return False
    
    # Hardcoded users from app.py
    USERS = {
        'patients': {
            'patient1': 'pass123',
            'john_doe': 'patient123',
            'jane_smith': 'mypass456',
            'mary_johnson': 'patient456',
            'robert_wilson': 'patient789'
        },
        'doctors': {
            'dr_smith': 'doctor123',
            'dr_johnson': 'medical456',
            'dr_brown': 'doctor789',
            'dr_davis': 'doctor456'
        },
        'admins': {
            'admin': 'admin123',
            'superadmin': 'super456',
            'hospital_admin': 'hospital789'
        }
    }
    
    success_count = 0
    total_count = 0
    
    for role, users in USERS.items():
        for username, password in users.items():
            total_count += 1
            
            # Check if user already exists
            existing_user = db.authenticate_user(username, password, role.rstrip('s'))
            if existing_user:
                print(f"⚠️ User already exists: {username} ({role.rstrip('s')})")
                continue
            
            # Create additional user info based on role
            additional_info = {}
            if role == 'doctors':
                additional_info = {
                    'display_name': username.replace('_', ' ').title(),
                    'department': 'General Medicine',
                    'license_number': f"LIC{username.upper()}123",
                    'specialization': 'General Practice'
                }
            elif role == 'admins':
                additional_info = {
                    'display_name': username.replace('_', ' ').title(),
                    'permissions': ['full_access'],
                    'department': 'Administration'
                }
            elif role == 'patients':
                additional_info = {
                    'display_name': username.replace('_', ' ').title(),
                    'registration_date': datetime.now()
                }
            
            # Create user in MongoDB
            result = db.create_user(username, password, role.rstrip('s'), additional_info)
            if result:
                success_count += 1
                print(f"✅ Migrated user: {username} ({role.rstrip('s')})")
            else:
                print(f"❌ Failed to migrate user: {username}")
    
    print(f"👥 User migration complete: {success_count}/{total_count} users migrated")
    return success_count == total_count

def migrate_hospitals_to_mongodb():
    """Migrate hardcoded hospital list to MongoDB"""
    print("🔄 Migrating hospitals to MongoDB...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected. Cannot migrate hospitals.")
        return False
    
    # Hardcoded hospitals from app.py
    hospitals = [
        {'id': 'hospital1', 'name': 'Hospital 1', 'description': 'General Medicine & Emergency Care'},
        {'id': 'hospital2', 'name': 'Hospital 2', 'description': 'Specialized Cardiac Care'},
        {'id': 'hospital3', 'name': 'Hospital 3', 'description': 'Pediatric & Family Medicine'},
        {'id': 'hospital4', 'name': 'Hospital 4', 'description': 'Orthopedic & Sports Medicine'},
        {'id': 'hospital5', 'name': 'Hospital 5', 'description': 'Cancer Treatment & Oncology'},
        {'id': 'hospital6', 'name': 'Central Medical Center', 'description': 'Comprehensive Healthcare Services'},
        {'id': 'hospital7', 'name': 'City General Hospital', 'description': 'Emergency & Trauma Center'},
        {'id': 'hospital8', 'name': 'Women\'s Health Clinic', 'description': 'Gynecology & Maternity Care'},
        {'id': 'hospital9', 'name': 'Mental Health Institute', 'description': 'Psychiatry & Behavioral Health'},
        {'id': 'hospital10', 'name': 'Rehabilitation Center', 'description': 'Physical Therapy & Recovery'}
    ]
    
    success_count = 0
    
    for hospital in hospitals:
        # Check if hospital already exists
        existing_hospitals = db.get_all_hospitals_config()
        if any(h.get('hospital_id') == hospital['id'] for h in existing_hospitals):
            print(f"⚠️ Hospital already exists: {hospital['name']}")
            continue
        
        # Prepare hospital data
        hospital_data = {
            'hospital_id': hospital['id'],
            'name': hospital['name'],
            'description': hospital['description'],
            'address': f"Address for {hospital['name']}",
            'phone': f"+1-555-{hospital['id'][-3:]}0",
            'email': f"contact@{hospital['id']}.com",
            'departments': ['General Medicine', 'Emergency', 'Pharmacy'],
            'operating_hours': {
                'monday': '7:30 AM - 8:30 PM',
                'tuesday': '7:30 AM - 8:30 PM',
                'wednesday': '7:30 AM - 8:30 PM',
                'thursday': '7:30 AM - 8:30 PM',
                'friday': '7:30 AM - 8:30 PM',
                'saturday': '8:00 AM - 6:00 PM',
                'sunday': '9:00 AM - 5:00 PM'
            },
            'capacity': 100,
            'current_patients': 0
        }
        
        # Create hospital in MongoDB
        result = db.create_hospital(hospital_data)
        if result:
            success_count += 1
            print(f"✅ Migrated hospital: {hospital['name']}")
        else:
            print(f"❌ Failed to migrate hospital: {hospital['name']}")
    
    print(f"🏥 Hospital migration complete: {success_count}/{len(hospitals)} hospitals migrated")
    return success_count == len(hospitals)

def migrate_system_config_to_mongodb():
    """Migrate system configuration to MongoDB"""
    print("🔄 Migrating system configuration to MongoDB...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected. Cannot migrate config.")
        return False
    
    # System configurations
    configs = {
        'app_name': 'Hospital Management System',
        'app_version': '2.0.0',
        'maintenance_mode': False,
        'max_patients_per_slot': 60,
        'slot_duration_minutes': 60,
        'total_slots_per_day': 13,
        'start_time': '7:30 AM',
        'end_time': '8:30 PM',
        'default_wait_time_per_patient': 5,
        'enable_token_system': True,
        'enable_email_notifications': False,
        'enable_sms_notifications': False,
        'max_file_upload_size_mb': 10,
        'allowed_file_types': ['pdf', 'jpg', 'png', 'doc', 'docx'],
        'session_timeout_minutes': 60,
        'backup_frequency_hours': 24,
        'log_level': 'INFO'
    }
    
    success_count = 0
    
    for key, value in configs.items():
        result = db.save_config(key, value)
        if result:
            success_count += 1
            print(f"✅ Saved config: {key} = {value}")
        else:
            print(f"❌ Failed to save config: {key}")
    
    print(f"⚙️ System config migration complete: {success_count}/{len(configs)} configs saved")
    return success_count == len(configs)

def verify_migration():
    """Verify that all data has been migrated successfully"""
    print("\n🔍 Verifying migration...")
    
    db = get_db()
    if not db.is_connected():
        print("❌ MongoDB not connected. Cannot verify migration.")
        return False
    
    # Verify users
    doctors = db.get_all_users('doctor')
    admins = db.get_all_users('admin')
    patients = db.get_all_users('patient')
    
    print(f"👥 Users in MongoDB:")
    print(f"   - Doctors: {len(doctors)}")
    print(f"   - Admins: {len(admins)}")
    print(f"   - Patients: {len(patients)}")
    
    # Verify hospitals
    hospitals = db.get_all_hospitals_config()
    print(f"🏥 Hospitals in MongoDB: {len(hospitals)}")
    
    # Verify configs
    configs = db.get_all_configs()
    print(f"⚙️ System configs in MongoDB: {len(configs)}")
    
    # Verify patient data
    patients_data = db.get_patients()
    print(f"📋 Patient records in MongoDB: {len(patients_data)}")
    
    print("✅ Migration verification complete!")
    return True

def main():
    """Run complete migration"""
    print("🚀 Starting complete data migration to MongoDB...")
    print("=" * 60)
    
    # Step 1: Migrate users
    users_success = migrate_users_to_mongodb()
    print()
    
    # Step 2: Migrate hospitals
    hospitals_success = migrate_hospitals_to_mongodb()
    print()
    
    # Step 3: Migrate system config
    config_success = migrate_system_config_to_mongodb()
    print()
    
    # Step 4: Verify migration
    verify_migration()
    print()
    
    # Summary
    print("=" * 60)
    if users_success and hospitals_success and config_success:
        print("🎉 Complete migration successful!")
        print("📝 All website data is now stored in MongoDB")
        print("💡 You can now update app.py to use MongoDB for all data")
    else:
        print("⚠️ Migration completed with some issues")
        print("📝 Please check the logs above for details")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
