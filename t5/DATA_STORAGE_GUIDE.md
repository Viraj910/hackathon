# 🏥 Hospital Management System - Data Storage Guide

## 📊 Complete MongoDB Integration Status

### ✅ What's Implemented:
- **Full MongoDB Integration** with fallback to JSON
- **Automatic Data Migration** from JSON to MongoDB
- **Hospital-specific Data Storage** in both systems
- **Token/Slot Management** with MongoDB support
- **Performance Optimizations** with MongoDB aggregation
- **Backward Compatibility** with existing JSON system

### 🗃️ Current Data Storage Locations

#### **JSON Files (Current/Fallback System):**
```
📁 c:\Users\viraj\OneDrive\Desktop\t5\
├── 📄 form_data_master.json (3 patients - ALL hospitals)
├── 📄 form_data_womens_health_clinic.json (3 patients - Women's Health Clinic)
└── 📄 form_data_{hospital_name}.json (Created as patients register)
```

#### **MongoDB Database (When Connected):**
```
🍃 Database: hospital_management
📍 Connection: mongodb://localhost:27017/
📦 Collections:
  ├── patients (Main patient records)
  ├── doctors (Future: Doctor management)
  └── admins (Future: Admin management)

📁 Data Location:
  ├── Windows: C:\data\db\
  ├── Docker: Container volume 'mongodb_data'
  └── Atlas: Cloud storage (AWS/Azure/GCP)
```

## 🚀 MongoDB Setup Options

### **Option 1: Easy Docker Setup (Recommended)**
```powershell
# Install Docker Desktop first, then:
python easy_mongodb_setup.py
```

### **Option 2: Manual Installation**
```powershell
# Download from: https://www.mongodb.com/try/download/community
# After installation:
net start MongoDB
python test_mongodb.py
```

### **Option 3: MongoDB Atlas (Cloud)**
```powershell
# Sign up at: https://www.mongodb.com/cloud/atlas
# Update .env with connection string:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

## 📈 Data Migration Process

### **1. Migrate Existing JSON Data**
```powershell
# Run the migration script:
python migrate_to_mongodb.py
```

### **2. Verify Migration**
```powershell
# Test connection and data:
python test_mongodb.py
```

### **3. Start Application**
```powershell
# Run with MongoDB:
python app.py
```

## 🔍 Data Storage Structure

### **Patient Record Structure:**
```json
{
  "_id": "ObjectId",
  "firstName": "John",
  "lastName": "Doe",
  "age": 30,
  "gender": "male",
  "phone": "1234567890",
  "address": "123 Main St",
  "selected_hospital": "Women's Health Clinic",
  "token_number": 1,
  "slot_number": 1,
  "time_range": "7:30 AM - 8:30 AM",
  "start_time": "7:30 AM",
  "end_time": "8:30 AM",
  "position_in_slot": 1,
  "estimated_wait_time": "0 minutes",
  "symptoms": "Headache",
  "allergies": "None",
  "medications": "Aspirin",
  "medicalHistory": "None",
  "emergencyName": "Jane Doe",
  "emergencyPhone": "0987654321",
  "emergencyRelation": "Wife",
  "emergency_contact": "Jane Doe 0987654321 (Wife)",
  "timestamp": "2025-06-27 19:15:49",
  "created_at": "2025-06-27T19:15:49.000Z",
  "migrated_from_json": true
}
```

### **Hospital Data Organization:**

#### **MongoDB Collections:**
- **patients**: All patient records with hospital field
- **doctors**: Doctor accounts (future expansion)
- **admins**: Admin accounts (future expansion)

#### **Indexes for Performance:**
- `selected_hospital` - Hospital-specific queries
- `timestamp` - Date-based filtering
- `token_number` - Token management
- `slot_number` - Appointment scheduling
- `firstName, lastName` - Patient search

## 🛠️ How the System Works

### **Data Flow:**
1. **Patient Registration** → Assigns token/slot → Saves to MongoDB (or JSON fallback)
2. **Doctor Access** → Retrieves from MongoDB → Shows patient lists and statistics
3. **Admin Access** → Full access to all hospital data → Advanced reporting

### **Fallback Mechanism:**
```python
# The system automatically falls back to JSON if MongoDB is unavailable
if db.is_connected():
    # Use MongoDB for better performance
    result = db.save_patient(data)
else:
    # Fall back to JSON files
    save_form_data_json_fallback(data)
```

## 📊 Data Access Patterns

### **Hospital-Specific Data:**
```python
# Get patients for specific hospital
patients = db.get_patients("Women's Health Clinic")

# Get all patients (admin view)
all_patients = db.get_patients()
```

### **Statistics and Reporting:**
```python
# MongoDB aggregation for better performance
stats = db.get_hospital_stats("Women's Health Clinic")

# Token management
next_token = db.get_next_token_for_hospital("Women's Health Clinic")
```

## 🔧 Management Commands

### **MongoDB Management:**
```powershell
# Start MongoDB service
net start MongoDB

# Stop MongoDB service  
net stop MongoDB

# Connect to MongoDB shell
mongosh

# Show databases
show dbs

# Use hospital database
use hospital_management

# Count patients
db.patients.countDocuments()

# Find patients by hospital
db.patients.find({"selected_hospital": "Women's Health Clinic"})
```

### **Docker Management:**
```powershell
# Start MongoDB container
docker start mongodb-hospital

# Stop MongoDB container
docker stop mongodb-hospital

# View MongoDB logs
docker logs mongodb-hospital

# Remove container (careful!)
docker rm mongodb-hospital
```

## 📁 File Locations Summary

### **Application Files:**
```
📁 c:\Users\viraj\OneDrive\Desktop\t5\
├── 🐍 app.py (Main application with MongoDB integration)
├── 🐍 database.py (MongoDB helper functions)
├── 🐍 migrate_to_mongodb.py (Data migration script)
├── 🐍 test_mongodb.py (Connection test)
├── 🐍 easy_mongodb_setup.py (Docker setup)
├── ⚙️ .env (MongoDB configuration)
├── 📄 requirements.txt (Dependencies with pymongo)
└── 📚 MONGODB_SETUP.md (Detailed setup guide)
```

### **Data Files:**
```
📁 JSON Files (Fallback):
├── 📄 form_data_master.json (All patients)
├── 📄 form_data_womens_health_clinic.json (Hospital-specific)
└── 📄 form_data_{hospital}.json (Auto-created)

🍃 MongoDB (Primary):
├── 📦 hospital_management.patients (All patient records)
├── 📦 hospital_management.doctors (Future)
└── 📦 hospital_management.admins (Future)
```

## 🎯 Next Steps

### **1. Install MongoDB:**
Choose one of the three installation options above

### **2. Run Migration:**
```powershell
python migrate_to_mongodb.py
```

### **3. Test Application:**
```powershell
python app.py
# Visit: http://localhost:5000
```

### **4. Verify Data:**
- Check patient registration works
- Verify token assignment
- Test doctor/admin access
- Confirm hospital-specific filtering

## 🔒 Security Considerations

### **Production Deployment:**
- Enable MongoDB authentication
- Use secure connection strings
- Implement proper user roles
- Regular database backups
- Network security (firewall, VPC)

### **Environment Variables:**
```env
# Production settings
MONGODB_URI=mongodb://production-server:27017/
DATABASE_NAME=hospital_management_prod
SECRET_KEY=very-secure-secret-key
FLASK_ENV=production
DEBUG=False
```

## 📞 Troubleshooting

### **Common Issues:**

1. **"No connection could be made"**
   - MongoDB service not running
   - Check: `net start MongoDB`

2. **"Import pymongo could not be resolved"**
   - Missing dependencies
   - Run: `pip install -r requirements.txt`

3. **"Permission denied"**
   - Run PowerShell as Administrator
   - Check MongoDB service permissions

4. **Data not appearing**
   - Check if migration completed
   - Verify database connection
   - Check fallback to JSON files

### **Get Help:**
- Run: `python test_mongodb.py` for diagnostics
- Check MongoDB logs for errors
- Verify .env configuration
- Test with JSON fallback mode

---

**🎉 Your hospital management system now supports both MongoDB and JSON storage with automatic fallback for maximum reliability!**
