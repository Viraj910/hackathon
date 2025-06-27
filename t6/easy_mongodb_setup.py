#!/usr/bin/env python3
"""
Easy MongoDB Setup with Docker
Provides simple MongoDB setup using Docker Desktop
"""

import subprocess
import time
import os

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker found: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def check_docker_running():
    """Check if Docker service is running"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def setup_mongodb_docker():
    """Setup MongoDB using Docker"""
    print("🐳 Setting up MongoDB with Docker...")
    
    # Check if container already exists
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=mongodb-hospital'], 
                               capture_output=True, text=True)
        if 'mongodb-hospital' in result.stdout:
            print("📦 MongoDB container already exists. Starting it...")
            subprocess.run(['docker', 'start', 'mongodb-hospital'])
        else:
            print("📦 Creating new MongoDB container...")
            # Create and run MongoDB container
            cmd = [
                'docker', 'run', '-d',
                '--name', 'mongodb-hospital',
                '-p', '27017:27017',
                '-v', 'mongodb_data:/data/db',
                'mongo:7.0'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ MongoDB container created successfully!")
            else:
                print(f"❌ Failed to create container: {result.stderr}")
                return False
        
        # Wait for MongoDB to start
        print("⏳ Waiting for MongoDB to start...")
        time.sleep(10)
        
        # Test connection
        from database import DatabaseManager
        db = DatabaseManager()
        if db.is_connected():
            print("✅ MongoDB is running and connected!")
            return True
        else:
            print("❌ MongoDB container started but connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        return False

def show_docker_instructions():
    """Show Docker Desktop installation instructions"""
    print("\n🐳 DOCKER DESKTOP INSTALLATION:")
    print("-" * 50)
    print("1️⃣ Download Docker Desktop:")
    print("   - Visit: https://www.docker.com/products/docker-desktop/")
    print("   - Download Docker Desktop for Windows")
    print("   - Run the installer")
    print("   - Restart your computer if prompted")
    print("   - Start Docker Desktop")
    
    print("\n2️⃣ After Docker Desktop is running:")
    print("   - Run this script again: python easy_mongodb_setup.py")
    print("   - Or manually run: docker run -d --name mongodb-hospital -p 27017:27017 mongo:7.0")

def show_manual_mongodb_instructions():
    """Show manual MongoDB installation"""
    print("\n📋 MANUAL MONGODB INSTALLATION:")
    print("-" * 50)
    print("1️⃣ Download MongoDB Community Server:")
    print("   - Visit: https://www.mongodb.com/try/download/community")
    print("   - Select Windows, Version 7.0+, MSI package")
    print("   - Download and install")
    
    print("\n2️⃣ Start MongoDB Service:")
    print("   - Open Command Prompt as Administrator")
    print("   - Run: net start MongoDB")
    
    print("\n3️⃣ Test Connection:")
    print("   - Run: python test_mongodb.py")

def main():
    print("🏥 EASY MONGODB SETUP")
    print("=" * 50)
    
    # Check Docker
    if not check_docker():
        print("❌ Docker not found")
        show_docker_instructions()
        print("\n" + "="*50)
        print("🔄 Alternative: Manual MongoDB Installation")
        show_manual_mongodb_instructions()
        return
    
    if not check_docker_running():
        print("❌ Docker is installed but not running")
        print("💡 Please start Docker Desktop and run this script again")
        return
    
    # Setup MongoDB with Docker
    if setup_mongodb_docker():
        print("\n🎉 MongoDB setup completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Run migration: python migrate_to_mongodb.py")
        print("   2. Test the application: python app.py")
        print("   3. Visit: http://localhost:5000")
        
        print("\n🔧 MongoDB Management:")
        print("   - Stop: docker stop mongodb-hospital")
        print("   - Start: docker start mongodb-hospital")
        print("   - Remove: docker rm mongodb-hospital")
        print("   - View logs: docker logs mongodb-hospital")
    else:
        print("\n❌ MongoDB setup failed")
        print("🔄 Try manual installation instead:")
        show_manual_mongodb_instructions()

if __name__ == "__main__":
    main()
