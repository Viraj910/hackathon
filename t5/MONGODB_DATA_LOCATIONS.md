# 📁 MongoDB Data Storage Locations Guide

## 🗂️ **Physical File Storage**

### **MongoDB Data Directory:**
📍 **Location**: `C:\Program Files\MongoDB\Server\8.0\data`

### **What's Inside:**
```
C:\Program Files\MongoDB\Server\8.0\data\
├── 📄 collection-*.wt          # Your patient data files
├── 📄 index-*.wt               # Database indexes for fast queries
├── 📄 _mdb_catalog.wt          # Database catalog
├── 📄 WiredTiger*              # Database engine files
├── 📄 sizeStorer.wt            # Storage size tracking
├── 📄 mongod.lock              # Lock file (MongoDB running indicator)
├── 📁 journal/                 # Transaction logs for durability
└── 📁 diagnostic.data/         # MongoDB diagnostic information
```

### **Your Hospital Data Files:**
- **Patient Records**: Stored in `collection-*.wt` files
- **Indexes**: Stored in `index-*.wt` files for fast queries
- **Database**: `hospital_management`
- **Collections**: `patients`, `doctors`, `admins`

---

## 🖥️ **How to View Your Data**

### **Method 1: MongoDB Compass (GUI) - RECOMMENDED**
```powershell
# Start MongoDB Compass (should be in Start Menu)
# Or run from command line:
"C:\Program Files\MongoDB\Server\8.0\bin\mongosh.exe"
```

**Connection Details:**
- **Host**: `localhost`
- **Port**: `27017`
- **Database**: `hospital_management`

### **Method 2: Command Line (MongoDB Shell)**
```powershell
# Connect to MongoDB
mongosh mongodb://localhost:27017/hospital_management

# View all databases
show dbs

# Use your database
use hospital_management

# View collections
show collections

# View all patients
db.patients.find().pretty()

# Count patients
db.patients.countDocuments()
```

### **Method 3: Python Script (Programmatic Access)**
```python
from database import DatabaseManager

db = DatabaseManager()
patients = db.get_patients()
print(f"Total patients: {len(patients)}")
for patient in patients:
    print(f"- {patient['firstName']} {patient['lastName']}")
```

---

## 📊 **Current Data Status**

### **Database Structure:**
```
hospital_management/
├── 📦 patients (3 documents)
│   ├── Viraj Viraj (Token: 1)
│   ├── Vira Viraj (Token: 2)
│   └── c s (Token: 3)
├── 📦 doctors (0 documents - ready for future use)
└── 📦 admins (0 documents - ready for future use)
```

### **Storage Size:**
- **Total Data Size**: ~300 KB
- **Index Size**: ~200 KB
- **Journal Size**: Variable (for transaction safety)

---

## 🔍 **Quick Data Access Commands**

### **View All Patients:**
```powershell
python -c "from database import DatabaseManager; db = DatabaseManager(); [print(f'{p[\"firstName\"]} {p[\"lastName\"]} - {p[\"selected_hospital\"]}') for p in db.get_patients()]"
```

### **Check MongoDB Status:**
```powershell
# Check service status
Get-Service MongoDB

# Test connection
python test_mongodb.py

# Verify data
python verify_mongodb.py
```

---

## 🛠️ **MongoDB Compass Setup (GUI Access)**

1. **Open MongoDB Compass**
   - Look in Start Menu: "MongoDB Compass"
   - Or navigate to: `C:\Program Files\MongoDB\Server\8.0\bin\`

2. **Connect to Database**
   - Connection String: `mongodb://localhost:27017`
   - Click "Connect"

3. **Navigate to Your Data**
   - Database: `hospital_management`
   - Collection: `patients`
   - You'll see all your patient records in a nice GUI

---

## 📂 **File Locations Summary**

| **Type** | **Location** | **Purpose** |
|----------|--------------|-------------|
| **Data Files** | `C:\Program Files\MongoDB\Server\8.0\data\` | Your actual patient data |
| **Log Files** | `C:\Program Files\MongoDB\Server\8.0\log\mongod.log` | MongoDB operation logs |
| **Config File** | `C:\Program Files\MongoDB\Server\8.0\bin\mongod.cfg` | MongoDB configuration |
| **Executables** | `C:\Program Files\MongoDB\Server\8.0\bin\` | MongoDB programs |
| **JSON Backup** | `c:\Users\viraj\OneDrive\Desktop\t5\json_backup_*\` | Your original JSON files |

---

## ⚠️ **Important Notes**

- **Don't manually edit** the `.wt` files - they're binary database files
- **Use MongoDB tools** (Compass, mongosh, or Python) to access data
- **Data is safe** - MongoDB uses journaling for crash recovery
- **Automatic indexing** - Your queries are optimized automatically
- **Backup location** - Your original JSON files are safely backed up

---

## 🎯 **Next Steps**

1. **Install MongoDB Compass** (if not already installed):
   ```powershell
   winget install MongoDB.Compass.Full
   ```

2. **Open MongoDB Compass** and connect to view your data visually

3. **Use the web application** at http://127.0.0.1:5000 to add more patients

4. **Monitor your data** using the verification scripts we created

Your data is now professionally stored in MongoDB with proper indexing, backup, and recovery capabilities! 🎉
