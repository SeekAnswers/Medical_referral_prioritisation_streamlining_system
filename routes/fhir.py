from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import ReferralRequest  # This aligns with the models defined in database.py, it would be adjusted accordingly based on the location of the database model
from database import get_db  # If import is elsewehere, it would be adjusted accordingly

fhir_router = APIRouter()

@fhir_router.get("/fhir/ReferralRequest/{referral_id}")
async def get_fhir_referral(referral_id: int, db: Session = Depends(get_db)):
    """Return a FHIR ReferralRequest resource for the given referral_id."""
    referral = db.query(ReferralRequest).filter(ReferralRequest.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    # Minimal FHIR ReferralRequest resource
    fhir_resource = {
        "resourceType": "ReferralRequest",
        "id": str(referral.id),
        "status": "active",
        "intent": "order",
        "subject": {
            "reference": f"Patient/{referral.patient_id or 'unknown'}"
        },
        "authoredOn": referral.referral_date.isoformat() if referral.referral_date else None,
        "description": referral.cases_data,
        "priority": referral.urgency_level.lower() if referral.urgency_level else "routine"
    }
    return fhir_resource