# MongoDB Setup Guide for Hospital Management System

## 🚀 Quick Start Guide

### Option 1: Local MongoDB Installation (Recommended for Development)

#### Windows Installation:
1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: Windows, Version 7.0+, MSI package
   - Download and run the installer

2. **Install MongoDB**
   - Run the downloaded MSI file
   - Choose "Complete" installation
   - Install MongoDB as a Windows Service (recommended)
   - Install MongoDB Compass (GUI tool) - optional but helpful

3. **Verify Installation**
   ```powershell
   # Check if MongoDB service is running
   Get-Service -Name MongoDB
   
   # Connect to MongoDB
   mongosh
   ```

4. **Start MongoDB (if not running)**
   ```powershell
   # Start MongoDB service
   net start MongoDB
   
   # Or restart if needed
   net stop MongoDB
   net start MongoDB
   ```

### Option 2: MongoDB Atlas (Cloud Database)

1. **Create Account**
   - Visit: https://www.mongodb.com/cloud/atlas
   - Sign up for free account
   - Create a new cluster (free tier available)

2. **Get Connection String**
   - Go to "Connect" → "Connect your application"
   - Copy the connection string
   - Update your `.env` file:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

### Option 3: Docker (For Advanced Users)

```powershell
# Pull and run MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Connect to MongoDB
docker exec -it mongodb mongosh
```

## 🔧 Configuration

### Update Environment Variables

Edit your `.env` file:

```env
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=hospital_management

# Or MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=hospital_management

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
DEBUG=True
```

## 📊 Database Schema

### Collections

1. **patients** - Main patient records
   ```javascript
   {
     "_id": ObjectId,
     "firstName": String,
     "lastName": String,
     "age": Number,
     "gender": String,
     "phone": String,
     "address": String,
     "selected_hospital": String,
     "token_number": Number,
     "slot_number": Number,
     "time_range": String,
     "symptoms": String,
     "allergies": String,
     "medications": String,
     "medicalHistory": String,
     "emergencyName": String,
     "emergencyPhone": String,
     "emergencyRelation": String,
     "timestamp": String,
     "created_at": Date,
     "migrated_from_json": Boolean
   }
   ```

2. **doctors** - Doctor records (future expansion)
3. **admins** - Admin records (future expansion)

### Indexes
- `selected_hospital` - For hospital-specific queries
- `timestamp` - For date-based queries
- `token_number` - For token management
- `slot_number` - For appointment scheduling
- `firstName, lastName` - For patient search

## 🔄 Data Migration

### Migrate from JSON Files

1. **Run Migration Script**
   ```powershell
   cd "c:\Users\viraj\OneDrive\Desktop\t5"
   python migrate_to_mongodb.py
   ```

2. **Verify Migration**
   - Check console output for success messages
   - Use MongoDB Compass to view data
   - Test the application

### Manual Verification

```javascript
// Connect to MongoDB
use hospital_management

// Count total patients
db.patients.countDocuments()

// List hospitals
db.patients.distinct("selected_hospital")

// View recent patients
db.patients.find().sort({timestamp: -1}).limit(5)

// Check migration status
db.patients.countDocuments({migrated_from_json: true})
```

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**
   ```
   Error: Cannot connect to MongoDB
   ```
   **Solution:**
   - Check if MongoDB service is running
   - Verify connection string in `.env`
   - Check firewall settings

2. **Import Errors**
   ```
   Import "pymongo" could not be resolved
   ```
   **Solution:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Permission Denied**
   ```
   Error: Permission denied
   ```
   **Solution:**
   - Run PowerShell as Administrator
   - Check MongoDB service permissions

### MongoDB Commands

```javascript
// Show databases
show dbs

// Use hospital database
use hospital_management

// Show collections
show collections

// Count documents
db.patients.countDocuments()

// Find all patients from specific hospital
db.patients.find({"selected_hospital": "Women's Health Clinic"})

// Create index
db.patients.createIndex({"selected_hospital": 1})

// Drop collection (be careful!)
db.patients.drop()
```

## 📈 Performance Tips

1. **Use Indexes**
   - Indexes are automatically created by the application
   - Add custom indexes for specific queries

2. **Connection Pooling**
   - PyMongo handles connection pooling automatically
   - Adjust pool size if needed

3. **Query Optimization**
   - Use aggregation pipelines for complex queries
   - Limit results when possible

## 🔒 Security Considerations

1. **Authentication**
   - Enable MongoDB authentication in production
   - Use strong passwords
   - Create specific users for the application

2. **Network Security**
   - Bind MongoDB to localhost in development
   - Use VPC/firewall rules in production
   - Enable SSL/TLS for connections

3. **Data Validation**
   - MongoDB schema validation is implemented
   - Application-level validation is also in place

## 🚀 Production Deployment

### Environment Variables for Production
```env
MONGODB_URI=mongodb://production-host:27017/
DATABASE_NAME=hospital_management_prod
SECRET_KEY=very-secure-secret-key-here
FLASK_ENV=production
DEBUG=False
```

### Backup Strategy
```bash
# Backup database
mongodump --db hospital_management --out backup/

# Restore database
mongorestore --db hospital_management backup/hospital_management/
```

## 📞 Support

If you encounter issues:

1. Check MongoDB logs:
   - Windows: `C:\Program Files\MongoDB\Server\7.0\log\mongod.log`
   - Or check Windows Event Viewer

2. Test connection:
   ```python
   from database import DatabaseManager
   db = DatabaseManager()
   print("Connected:", db.is_connected())
   ```

3. Check application logs for detailed error messages

## 🎯 Next Steps

After MongoDB setup:

1. Run the migration script
2. Test the application thoroughly
3. Consider implementing additional features:
   - User authentication with MongoDB
   - Advanced reporting with aggregation
   - Real-time updates with change streams
   - Data archiving strategies
