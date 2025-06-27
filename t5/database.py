"""
MongoDB Database Helper Module
Handles all database operations for the hospital management system
"""

from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId
import json

class DatabaseManager:
    def __init__(self, connection_string=None, database_name=None):
        """Initialize MongoDB connection"""
        self.connection_string = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = database_name or os.getenv('DATABASE_NAME', 'hospital_management')
        
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.database_name}")
            
            # Create indexes for better performance
            self._create_indexes()
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("📝 Make sure MongoDB is installed and running on your system")
            self.client = None
            self.db = None
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Patients collection indexes
            self.db.patients.create_index("selected_hospital")
            self.db.patients.create_index("timestamp")
            self.db.patients.create_index("token_number")
            self.db.patients.create_index("slot_number")
            self.db.patients.create_index([("firstName", 1), ("lastName", 1)])
            
            # Users collections indexes
            self.db.doctors.create_index("username", unique=True)
            self.db.admins.create_index("username", unique=True)
            
            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    def is_connected(self):
        """Check if database connection is active"""
        return self.client is not None and self.db is not None
    
    # PATIENT OPERATIONS
    def save_patient(self, patient_data):
        """Save patient data to MongoDB"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            # Add timestamp if not present
            if 'timestamp' not in patient_data:
                patient_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add created_at for MongoDB tracking
            patient_data['created_at'] = datetime.now()
            
            # Insert patient data
            result = self.db.patients.insert_one(patient_data)
            patient_data['_id'] = str(result.inserted_id)
            
            print(f"✅ Patient saved: {patient_data.get('firstName', 'Unknown')} {patient_data.get('lastName', '')}")
            return patient_data
            
        except Exception as e:
            print(f"❌ Error saving patient: {e}")
            return None
    
    def get_patients(self, hospital_name=None, limit=None):
        """Get patients from MongoDB"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            # Build query
            query = {}
            if hospital_name:
                query['selected_hospital'] = hospital_name
            
            # Execute query
            cursor = self.db.patients.find(query).sort("timestamp", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            # Convert to list and handle ObjectId
            patients = []
            for patient in cursor:
                patient['_id'] = str(patient['_id'])
                patients.append(patient)
            
            return patients
            
        except Exception as e:
            print(f"❌ Error retrieving patients: {e}")
            return []
    
    def get_patient_by_id(self, patient_id):
        """Get single patient by MongoDB ObjectId"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            patient = self.db.patients.find_one({"_id": ObjectId(patient_id)})
            
            if patient:
                patient['_id'] = str(patient['_id'])
                return patient
            
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving patient by ID: {e}")
            return None
    
    def update_patient(self, patient_id, update_data):
        """Update patient data"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            result = self.db.patients.update_one(
                {"_id": ObjectId(patient_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error updating patient: {e}")
            return False
    
    def delete_patient(self, patient_id):
        """Delete patient by ID"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            result = self.db.patients.delete_one({"_id": ObjectId(patient_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"❌ Error deleting patient: {e}")
            return False
    
    # HOSPITAL STATISTICS
    def get_hospital_stats(self, hospital_name=None):
        """Get statistics for hospitals"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            pipeline = []
            
            # Match stage - filter by hospital if specified
            if hospital_name:
                pipeline.append({"$match": {"selected_hospital": hospital_name}})
            
            # Group and calculate statistics
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_patients": {"$sum": 1},
                        "male_patients": {
                            "$sum": {
                                "$cond": [{"$eq": [{"$toLower": "$gender"}, "male"]}, 1, 0]
                            }
                        },
                        "female_patients": {
                            "$sum": {
                                "$cond": [{"$eq": [{"$toLower": "$gender"}, "female"]}, 1, 0]
                            }
                        },
                        "patients_with_tokens": {
                            "$sum": {
                                "$cond": [{"$gt": ["$token_number", 0]}, 1, 0]
                            }
                        }
                    }
                }
            ])
            
            result = list(self.db.patients.aggregate(pipeline))
            
            if result:
                stats = result[0]
                del stats['_id']  # Remove MongoDB _id field
                return stats
            
            return {
                'total_patients': 0,
                'male_patients': 0,
                'female_patients': 0,
                'patients_with_tokens': 0
            }
            
        except Exception as e:
            print(f"❌ Error getting hospital stats: {e}")
            return {}
    
    def get_hospitals_list(self):
        """Get list of all hospitals with patient counts"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            pipeline = [
                {
                    "$group": {
                        "_id": "$selected_hospital",
                        "patient_count": {"$sum": 1},
                        "latest_patient": {"$max": "$timestamp"}
                    }
                },
                {
                    "$sort": {"patient_count": -1}
                }
            ]
            
            results = list(self.db.patients.aggregate(pipeline))
            
            hospitals = []
            for result in results:
                hospitals.append({
                    'hospital_name': result['_id'],
                    'patient_count': result['patient_count'],
                    'latest_patient': result['latest_patient']
                })
            
            return hospitals
            
        except Exception as e:
            print(f"❌ Error getting hospitals list: {e}")
            return []
    
    # TOKEN AND SLOT MANAGEMENT
    def get_next_token_for_hospital(self, hospital_name):
        """Get next available token number for a hospital"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            # Find the highest token number for this hospital
            result = self.db.patients.find_one(
                {"selected_hospital": hospital_name},
                sort=[("token_number", -1)]
            )
            
            if result and 'token_number' in result:
                return result['token_number'] + 1
            
            return 1  # First token for this hospital
            
        except Exception as e:
            print(f"❌ Error getting next token: {e}")
            return 1
    
    def get_patients_in_slot(self, hospital_name, slot_number):
        """Get all patients in a specific time slot for a hospital"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            patients = list(self.db.patients.find({
                "selected_hospital": hospital_name,
                "slot_number": slot_number
            }).sort("token_number", 1))
            
            # Convert ObjectIds to strings
            for patient in patients:
                patient['_id'] = str(patient['_id'])
            
            return patients
            
        except Exception as e:
            print(f"❌ Error getting patients in slot: {e}")
            return []
    
    # USER MANAGEMENT (for future expansion)
    def save_user(self, user_data, user_type):
        """Save user data (doctors, admins)"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            collection_name = f"{user_type}s"  # doctors, admins
            user_data['created_at'] = datetime.now()
            
            result = self.db[collection_name].insert_one(user_data)
            user_data['_id'] = str(result.inserted_id)
            
            return user_data
            
        except Exception as e:
            print(f"❌ Error saving {user_type}: {e}")
            return None
    
    # DATA MIGRATION FROM JSON
    def migrate_from_json(self, json_file_path):
        """Migrate existing JSON data to MongoDB"""
        try:
            if not self.is_connected():
                raise Exception("Database not connected")
            
            if not os.path.exists(json_file_path):
                print(f"⚠️ JSON file not found: {json_file_path}")
                return False
            
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
            
            if not json_data:
                print(f"⚠️ No data found in {json_file_path}")
                return True
            
            # Insert all data
            for patient_data in json_data:
                # Remove any existing _id field from JSON
                if '_id' in patient_data:
                    del patient_data['_id']
                
                # Add creation timestamp
                patient_data['created_at'] = datetime.now()
                patient_data['migrated_from_json'] = True
            
            # Bulk insert
            result = self.db.patients.insert_many(json_data)
            
            print(f"✅ Migrated {len(result.inserted_ids)} patients from {json_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error migrating from JSON: {e}")
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔐 MongoDB connection closed")

# Global database instance
db_manager = None

def get_db():
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_db(app=None):
    """Initialize database with Flask app"""
    global db_manager
    db_manager = DatabaseManager()
    
    if app:
        @app.teardown_appcontext
        def close_db(error):
            if db_manager:
                db_manager.close_connection()
    
    return db_manager
