#!/usr/bin/env python3

from database import get_db

def test_token_assignment():
    """Test token assignment functionality"""
    print("=== Testing Token Assignment ===")
    
    db = get_db()
    print(f"Database connected: {db.is_connected()}")
    
    if db.is_connected():
        # Test getting next token for different hospitals
        hospitals = ["Hospital 1", "Hospital 2", "Central Medical Center"]
        
        for hospital in hospitals:
            token = db.get_next_token_for_hospital(hospital)
            print(f"Next token for '{hospital}': {token}")
        
        # Check existing patients count
        patients = db.get_patients()
        print(f"Total patients in database: {len(patients)}")
        
        # Check patients by hospital
        for hospital in hospitals:
            hospital_patients = db.get_patients(hospital)
            print(f"Patients in '{hospital}': {len(hospital_patients)}")
            
            # Show token numbers for this hospital
            tokens = [p.get('token_number') for p in hospital_patients if p.get('token_number')]
            if tokens:
                print(f"  Token numbers: {sorted(tokens)}")
                print(f"  Highest token: {max(tokens)}")
            else:
                print(f"  No tokens found for {hospital}")
    else:
        print("❌ Database not connected - this is why tokens are always 1!")

if __name__ == "__main__":
    test_token_assignment()
