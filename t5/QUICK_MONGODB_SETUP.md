# 🍃 MongoDB Setup Guide for Windows

## Quick Installation Methods

### Option 1: Manual Download (Recommended for Windows)

1. **Download MongoDB Community Server**
   - Go to: https://www.mongodb.com/try/download/community
   - Select: `Windows`, `Version 7.0+`, `msi` package
   - Click `Download`

2. **Install MongoDB**
   - Run the downloaded `.msi` file
   - Choose `Complete` installation
   - Check "Install MongoDB as a Service" 
   - Check "Install MongoDB Compass" (GUI tool)
   - Click `Install`

3. **Start MongoDB Service**
   ```powershell
   # Start MongoDB service
   net start MongoDB
   
   # Check if it's running
   Get-Service MongoDB
   ```

4. **Test Installation**
   ```powershell
   # Test MongoDB connection
   python test_mongodb.py
   ```

### Option 2: Using Chocolatey Package Manager

1. **Install Chocolatey** (if not already installed)
   ```powershell
   # Run PowerShell as Administrator
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Install MongoDB with Chocolatey**
   ```powershell
   # Install MongoDB
   choco install mongodb
   
   # Start MongoDB service
   net start MongoDB
   ```

### Option 3: Using Docker (If Docker is installed)

1. **Run MongoDB Container**
   ```powershell
   # Download and run MongoDB in Docker
   docker run -d --name mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
   
   # Check if running
   docker ps
   ```

### Option 4: MongoDB Atlas (Cloud - No Installation Required)

1. **Sign up for MongoDB Atlas**
   - Go to: https://www.mongodb.com/cloud/atlas
   - Create free account
   - Create new cluster (free tier available)

2. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string

3. **Update .env file**
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   DATABASE_NAME=hospital_management
   ```

## After Installation

1. **Test MongoDB Connection**
   ```powershell
   python test_mongodb.py
   ```

2. **Migrate Existing Data**
   ```powershell
   python migrate_to_mongodb.py
   ```

3. **Run Your Application**
   ```powershell
   python app.py
   ```

## Troubleshooting

### MongoDB Service Won't Start
```powershell
# Create data directory
mkdir C:\data\db

# Start MongoDB manually
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db
```

### Connection Issues
- Make sure MongoDB service is running: `Get-Service MongoDB`
- Check if port 27017 is open: `Test-NetConnection localhost -Port 27017`
- Verify firewall settings

### Alternative Ports
If port 27017 is busy, you can run MongoDB on a different port:
```powershell
mongod --port 27018 --dbpath C:\data\db
```

Then update your `.env` file:
```
MONGODB_URI=mongodb://localhost:27018/
```

## Next Steps

Once MongoDB is installed and running:

1. ✅ MongoDB is connected
2. 📊 Migrate existing JSON data to MongoDB
3. 🚀 Run the application with MongoDB backend
4. 🗑️ (Optional) Remove JSON files after successful migration

## Need Help?

If you encounter issues:
1. Check the MongoDB logs: `C:\Program Files\MongoDB\Server\7.0\log\mongod.log`
2. Try running MongoDB manually to see error messages
3. Use MongoDB Compass (GUI) to verify the connection
