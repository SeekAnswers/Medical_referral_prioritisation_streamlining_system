import re
from typing import Optional
from database.models import Patient, ReferralRequest, User
from database.database import SessionLocal

def extract_patient_id_from_query(query: str) -> Optional[str]:
    """Extract patient ID from formatted query"""
    pattern = r"Patient ID:\s*([^\n\r]+)"
    match = re.search(pattern, query)
    return match.group(1).strip() if match else None

def extract_referring_location(query: str) -> Optional[str]:
    """Extract referring location from formatted query"""
    pattern = r"Referring from:\s*([^\n\r]+)"
    match = re.search(pattern, query)
    return match.group(1).strip() if match else None

def extract_staff_name(query: str) -> Optional[str]:
    """Extract staff name from formatted query"""
    pattern = r"Team/Staff Name:\s*([^\n\r]+)"
    match = re.search(pattern, query)
    return match.group(1).strip() if match else None

def extract_highest_urgency(prioritization_text: str) -> str:
    """Extract the highest urgency level from prioritization result"""
    text_lower = prioritization_text.lower()
    if "emergent" in text_lower:
        return "emergent"
    elif "urgent" in text_lower:
        return "urgent"
    else:
        return "routine"

def extract_primary_specialty(prioritization_text: str) -> str:
    """Extract primary specialty from prioritization result"""
    text_lower = prioritization_text.lower()
    specialties = {
        "cardiology": "cardiology",
        "oncology": "oncology", 
        "surgery": "surgery",
        "emergency": "emergency",
        "er": "emergency",
        "dermatology": "dermatology",
        "orthopaedic": "orthopaedic",
        "orthopedic": "orthopaedic",
        "obstetrics": "obstetrics",
        "gynaecology": "gynaecology",
        "gynecology": "gynaecology"
    }
    
    for keyword, specialty in specialties.items():
        if keyword in text_lower:
            return specialty
    return "general"

def get_or_create_patient(db: SessionLocal, patient_data: dict) -> Patient:
    """Get existing patient or create new one"""
    if not patient_data.get("patient_id"):
        return None
        
    patient = db.query(Patient).filter(Patient.patient_id == patient_data["patient_id"]).first()
    
    if not patient:
        patient = Patient(
            patient_id=patient_data["patient_id"],
            name=patient_data.get("name"),
            age=int(patient_data.get("age")) if patient_data.get("age") else None,
            sex=patient_data.get("sex"),
            address=patient_data.get("address")
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    return patient

def create_default_admin_user(db: SessionLocal, username: str = "admin", password: str = "hospital123"):
    """Create default admin user for initial setup"""
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"Admin user '{username}' already exists")
        return existing_user
    
    admin_user = User(
        username=username,
        email=f"{username}@hospital.local",
        hashed_password=User.get_password_hash(password),
        full_name="System Administrator",
        department="IT Administration",
        role="admin",
        is_active=True,
        is_verified=True,
        hospital_id="MAIN_HOSPITAL"
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user