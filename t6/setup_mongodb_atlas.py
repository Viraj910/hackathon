#!/usr/bin/env python3
"""
MongoDB Atlas (Cloud) Setup
Quick setup with cloud MongoDB - no local installation needed
"""

import os
import sys

def setup_mongodb_atlas():
    """Setup MongoDB Atlas cloud connection"""
    print("🌐 MongoDB Atlas (Cloud) Setup")
    print("=" * 50)
    
    print("\n📋 Step 1: Create MongoDB Atlas Account")
    print("   1. Visit: https://www.mongodb.com/cloud/atlas")
    print("   2. Click 'Try Free'")
    print("   3. Sign up with email")
    print("   4. Verify your email")
    
    print("\n📋 Step 2: Create a Cluster")
    print("   1. Choose 'Shared' (Free tier)")
    print("   2. Select cloud provider (AWS recommended)")
    print("   3. Choose region closest to you")
    print("   4. Cluster Name: 'hospital-management'")
    print("   5. Click 'Create Cluster' (takes 3-5 minutes)")
    
    print("\n📋 Step 3: Create Database User")
    print("   1. Go to 'Database Access' in left menu")
    print("   2. Click 'Add New Database User'")
    print("   3. Username: 'hospital_admin'")
    print("   4. Password: Generate secure password")
    print("   5. Database User Privileges: 'Atlas admin'")
    print("   6. Click 'Add User'")
    
    print("\n📋 Step 4: Configure Network Access")
    print("   1. Go to 'Network Access' in left menu")
    print("   2. Click 'Add IP Address'")
    print("   3. Click 'Allow Access from Anywhere' (for development)")
    print("   4. Click 'Confirm'")
    
    print("\n📋 Step 5: Get Connection String")
    print("   1. Go to 'Clusters' in left menu")
    print("   2. Click 'Connect' on your cluster")
    print("   3. Choose 'Connect your application'")
    print("   4. Driver: Python, Version: 3.6 or later")
    print("   5. Copy the connection string")
    
    print("\n🔧 Step 6: Update Your .env File")
    connection_string = input("\nPaste your MongoDB Atlas connection string here: ").strip()
    
    if connection_string:
        # Update .env file
        env_content = f"""# MongoDB Configuration (Atlas Cloud)
MONGODB_URI={connection_string}
DATABASE_NAME=hospital_management

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production

# Development Settings
FLASK_ENV=development
DEBUG=True"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file updated with Atlas connection")
        
        # Test connection
        print("\n🧪 Testing connection...")
        test_atlas_connection()
    else:
        print("⚠️ No connection string provided")

def test_atlas_connection():
    """Test MongoDB Atlas connection"""
    try:
        from database import DatabaseManager
        
        print("🔗 Connecting to MongoDB Atlas...")
        db = DatabaseManager()
        
        if db.is_connected():
            print("✅ Successfully connected to MongoDB Atlas!")
            
            # Test basic operations
            print("🧪 Testing database operations...")
            
            # Insert test record
            test_patient = {
                'firstName': 'Atlas',
                'lastName': 'Test',
                'age': '25',
                'gender': 'female',
                'phone': '1234567890',
                'selected_hospital': 'Test Hospital Cloud',
                'timestamp': '2025-06-27 12:00:00'
            }
            
            result = db.save_patient(test_patient)
            if result:
                print("✅ Database write test: SUCCESS")
                
                # Test read
                patients = db.get_patients('Test Hospital Cloud')
                if patients:
                    print("✅ Database read test: SUCCESS")
                    print(f"📊 Found {len(patients)} test patient(s)")
                    
                    # Clean up test data
                    db.db.patients.delete_many({'firstName': 'Atlas', 'lastName': 'Test'})
                    print("🧹 Test data cleaned up")
                else:
                    print("⚠️ Database read test: NO DATA")
            else:
                print("❌ Database write test: FAILED")
        else:
            print("❌ Failed to connect to MongoDB Atlas")
            print("💡 Check your connection string and network access settings")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("💡 Make sure you've installed dependencies: pip install -r requirements.txt")

def show_atlas_benefits():
    """Show benefits of using MongoDB Atlas"""
    print("\n🌟 MongoDB Atlas Benefits:")
    print("=" * 50)
    print("✅ No local installation required")
    print("✅ Always accessible from anywhere")
    print("✅ Automatic backups")
    print("✅ Built-in security")
    print("✅ Free tier: 512MB storage")
    print("✅ Easy scaling when needed")
    print("✅ 24/7 monitoring")
    print("✅ Global clusters available")

def main():
    print("🏥 HOSPITAL MANAGEMENT SYSTEM")
    print("🌐 MongoDB Atlas Cloud Setup")
    print("=" * 60)
    
    show_atlas_benefits()
    
    choice = input("\n❓ Do you want to set up MongoDB Atlas? (y/N): ").lower()
    
    if choice == 'y':
        setup_mongodb_atlas()
    else:
        print("\n📚 Alternative Setup Options:")
        print("   1. Local MongoDB: python install_mongodb.ps1")
        print("   2. Docker MongoDB: python easy_mongodb_setup.py")
        print("   3. Manual installation: See MONGODB_SETUP.md")

if __name__ == "__main__":
    main()
