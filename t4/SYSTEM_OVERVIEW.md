# Hospital Management System - 3-Tier Access Control

## 🏥 System Overview

The hospital management system now features a comprehensive 3-tier access control system with distinct roles and permissions:

## 👥 User Roles & Access Levels

### 1. **PATIENTS** 🏥
**Access:** Limited to voice-assisted form filling only
- **Login Credentials:** 
  - `patient1` / `pass123`
  - `john_doe` / `patient123`
  - `jane_smith` / `mypass456`
  - `mary_johnson` / `patient456`
  - `robert_wilson` / `patient789`

**Permissions:**
- ✅ Fill medical forms using AI voice assistant
- ✅ View form submission confirmation
- ❌ No access to other patients' data
- ❌ No administrative functions

### 2. **DOCTORS** 🩺
**Access:** Patient data viewing and basic reporting
- **Login Credentials:**
  - `dr_smith` / `doctor123`
  - `dr_johnson` / `medical456`
  - `dr_brown` / `doctor789`
  - `dr_davis` / `doctor456`

**Permissions:**
- ✅ View all patient details and medical records
- ✅ Generate medical reports and statistics
- ✅ Export basic patient data (limited CSV - no sensitive contact info)
- ✅ Access patient management dashboard
- ❌ Cannot export full patient data with contact details
- ❌ Cannot manage other doctors or system users
- ❌ No system configuration access

### 3. **ADMINISTRATORS** 🛡️
**Access:** Full system control and management
- **Login Credentials:**
  - `admin` / `admin123`
  - `superadmin` / `super456`
  - `hospital_admin` / `hospital789`

**Permissions:**
- ✅ Full access to all patient data and medical records
- ✅ Manage doctors and all system users
- ✅ Export complete patient data including contact information
- ✅ Export doctor and user management data
- ✅ Access comprehensive system reports and analytics
- ✅ Configure system settings
- ✅ All doctor permissions plus administrative functions

## 🔒 Security Features

### Access Control
- **Role-based authentication** with session management
- **Route protection** using decorators
- **Multi-role support** for shared routes (doctors + admins)
- **Automatic session cleanup** on logout

### Data Protection
- **Limited data exposure** for doctors (no sensitive contact info in exports)
- **Full data access** only for administrators
- **Secure file downloads** with proper headers
- **Input validation** and sanitization

## 📊 Export Functionality

### Patient Data Export (Admin Only)
- **Complete CSV Export:** All patient data including contact info
- **Filtered CSV Export:** Custom filters by age, gender, date range
- **Advanced Export Modal:** Comprehensive filtering options

### Doctor Data Export (Admin Only)
- **Doctor Information:** Username, display name, role, status
- **All Users Export:** Complete user database across all roles

### Limited Export (Doctors)
- **Basic Patient Data:** Medical info only (no contact details)
- **Includes:** Names, symptoms, medical history, medications, allergies
- **Excludes:** Phone numbers, addresses, emergency contacts

## 🌐 Application Structure

### Routes by Role

**Public Routes:**
- `/` - Homepage
- `/login-choice` - Login selection
- `/patient/login` - Patient login
- `/doctor/login` - Doctor login
- `/admin/login` - Admin login

**Patient Routes:**
- `/patient/dashboard` - Redirects to form
- `/patient/form` - AI voice-assisted medical form

**Doctor Routes:**
- `/doctor/dashboard` - Doctor dashboard
- `/doctor/patients` - Patient management (shared with admin)
- `/doctor/reports` - Medical reports (shared with admin)
- `/doctor/export/csv` - Basic patient data export
- `/doctor/patient/<id>` - Individual patient details (shared with admin)

**Admin Routes:**
- `/admin/dashboard` - Comprehensive system overview
- `/admin/users` - User management
- `/admin/doctors` - Doctor management
- `/admin/system` - System settings
- `/admin/reports` - Advanced analytics
- `/admin/export/csv` - Complete patient data export
- `/admin/export/filtered-csv` - Filtered patient data
- `/admin/export/doctors-csv` - Doctor data export
- `/admin/export/users-csv` - All users export

## 🎯 Key Features

### For Patients
- **Voice-assisted form filling** using AI
- **Clean, simple interface** focused on medical data entry
- **Secure data submission** with confirmation

### For Doctors
- **Patient management dashboard** with statistics
- **Medical reports and analytics**
- **Limited data export** for medical purposes
- **Individual patient detail views**

### For Administrators
- **Complete system oversight** with comprehensive dashboard
- **User and doctor management**
- **Full data export capabilities**
- **System configuration and settings**
- **Advanced reporting and analytics**

## 🚀 Getting Started

1. **Start the application:** `python app.py`
2. **Access the system:** `http://127.0.0.1:5000`
3. **Choose your role** from the login page
4. **Use the credentials** listed above for each role

## 📋 Sample Test Scenarios

### Patient Workflow
1. Login as patient → Voice form → Submit → Confirmation

### Doctor Workflow  
1. Login as doctor → Dashboard → View patients → Generate reports → Export basic data

### Admin Workflow
1. Login as admin → Dashboard → Manage users → View comprehensive reports → Export all data

The system is now production-ready with proper role separation, security measures, and comprehensive functionality for hospital management! 🏥✨
