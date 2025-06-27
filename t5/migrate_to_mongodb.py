#!/usr/bin/env python3
"""
Data Migration Script: JSON to MongoDB
Migrates existing JSON files to MongoDB database
"""

import json
import os
from datetime import datetime
from database import DatabaseManager

def migrate_json_to_mongodb():
    """Main migration function"""
    print("🚀 Starting JSON to MongoDB migration...")
    
    # Initialize database
    db = DatabaseManager()
    
    if not db.is_connected():
        print("❌ Cannot connect to MongoDB. Make sure MongoDB is running.")
        print("📋 To install MongoDB:")
        print("   1. Download MongoDB Community Server from https://www.mongodb.com/download-center/community")
        print("   2. Install and start MongoDB service")
        print("   3. Run this script again")
        return False
    
    # Find all JSON files to migrate
    json_files = []
    for filename in os.listdir('.'):
        if filename.startswith('form_data_') and filename.endswith('.json'):
            json_files.append(filename)
    
    if not json_files:
        print("⚠️ No JSON data files found to migrate")
        return True
    
    print(f"📂 Found {len(json_files)} JSON files to migrate:")
    for file in json_files:
        print(f"   - {file}")
    
    # Migrate each file
    total_migrated = 0
    for json_file in json_files:
        print(f"\n📄 Migrating {json_file}...")
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if not data:
                print(f"   ⚠️ No data in {json_file}")
                continue
            
            # Migrate each patient record
            migrated_count = 0
            for patient_data in data:
                # Skip if already migrated (check by timestamp and name)
                existing = db.db.patients.find_one({
                    'firstName': patient_data.get('firstName'),
                    'lastName': patient_data.get('lastName'),
                    'timestamp': patient_data.get('timestamp'),
                    'selected_hospital': patient_data.get('selected_hospital')
                })
                
                if existing:
                    print(f"   ⏭️ Skipping duplicate: {patient_data.get('firstName', 'Unknown')} {patient_data.get('lastName', '')}")
                    continue
                
                # Add migration metadata
                patient_data['migrated_from_json'] = True
                patient_data['migrated_at'] = datetime.now()
                patient_data['source_file'] = json_file
                
                # Remove any existing _id field
                if '_id' in patient_data:
                    del patient_data['_id']
                
                # Save to MongoDB
                result = db.save_patient(patient_data)
                if result:
                    migrated_count += 1
                    total_migrated += 1
                else:
                    print(f"   ❌ Failed to migrate: {patient_data.get('firstName', 'Unknown')}")
            
            print(f"   ✅ Migrated {migrated_count} patients from {json_file}")
            
        except Exception as e:
            print(f"   ❌ Error migrating {json_file}: {e}")
    
    print(f"\n🎉 Migration completed! Total patients migrated: {total_migrated}")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    all_patients = db.get_patients()
    migrated_patients = [p for p in all_patients if p.get('migrated_from_json')]
    
    print(f"✅ Total patients in MongoDB: {len(all_patients)}")
    print(f"✅ Migrated patients: {len(migrated_patients)}")
    
    # Show statistics by hospital
    hospitals = db.get_hospitals_list()
    if hospitals:
        print("\n🏥 Hospital Statistics:")
        for hospital in hospitals:
            print(f"   - {hospital['hospital_name']}: {hospital['patient_count']} patients")
    
    # Close connection
    db.close_connection()
    
    return True

def backup_json_files():
    """Create backup of JSON files before migration"""
    backup_dir = f"json_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    json_files = [f for f in os.listdir('.') if f.startswith('form_data_') and f.endswith('.json')]
    
    if not json_files:
        print("⚠️ No JSON files to backup")
        return
    
    os.makedirs(backup_dir, exist_ok=True)
    
    for json_file in json_files:
        import shutil
        shutil.copy2(json_file, os.path.join(backup_dir, json_file))
    
    print(f"💾 JSON files backed up to: {backup_dir}")

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 HOSPITAL MANAGEMENT SYSTEM - DATA MIGRATION")
    print("=" * 60)
    
    # Ask user for confirmation
    response = input("\n⚠️ This will migrate all JSON data to MongoDB. Continue? (y/N): ")
    
    if response.lower() != 'y':
        print("❌ Migration cancelled by user")
        exit(0)
    
    # Create backup
    print("\n💾 Creating backup of JSON files...")
    backup_json_files()
    
    # Run migration
    success = migrate_json_to_mongodb()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📋 Next steps:")
        print("   1. Test the application with MongoDB")
        print("   2. If everything works, you can delete the JSON files")
        print("   3. Update your deployment to use MongoDB")
    else:
        print("\n❌ Migration failed!")
        print("📋 Please check the error messages above and try again")
