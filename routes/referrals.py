from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import Optional, List
from datetime import date
from database.database import get_db
from database.models import User, ReferralRequest, Patient
from utils.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/referrals", tags=["referrals"])

class ReferralSummary(BaseModel):
    id: int
    patient_id: str
    referring_location: str
    staff_name: str
    referral_date: Optional[str]
    referral_time: Optional[str]
    created_at: str
    status: str
    urgency_level: Optional[str]
    specialty: Optional[str]
    cases_summary: str
    created_by_username: Optional[str]

class ReferralDetail(BaseModel):
    id: int
    patient_id: str
    referring_location: str
    staff_name: str
    cases_data: str
    prioritization_result: Optional[str]
    context_data: Optional[str]
    referral_date: Optional[str]
    referral_time: Optional[str]
    created_at: str
    updated_at: str
    status: str
    urgency_level: Optional[str]
    specialty: Optional[str]
    created_by_username: Optional[str]

@router.get("/", response_model=dict)
async def get_referrals(
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    filter_date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    filter_date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    filter_urgency: Optional[str] = Query(None, description="Filter by urgency level"),
    filter_specialty: Optional[str] = Query(None, description="Filter by specialty"),
    filter_status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Limit results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get referrals with filtering and sorting"""
    
    try:
        # Base query with joins
        query = db.query(ReferralRequest).join(User, ReferralRequest.created_by == User.id, isouter=True)
        
        # Apply date filters
        if filter_date_from:
            query = query.filter(ReferralRequest.referral_date >= filter_date_from)
        if filter_date_to:
            query = query.filter(ReferralRequest.referral_date <= filter_date_to)
        
        # Apply other filters
        if filter_urgency:
            query = query.filter(ReferralRequest.urgency_level == filter_urgency)
        if filter_specialty:
            query = query.filter(ReferralRequest.specialty == filter_specialty)
        if filter_status:
            query = query.filter(ReferralRequest.status == filter_status)
        
        # Apply sorting
        if sort_by == "created_at":
            order_column = ReferralRequest.created_at
        elif sort_by == "referral_date":
            order_column = ReferralRequest.referral_date
        elif sort_by == "urgency_level":
            order_column = ReferralRequest.urgency_level
        elif sort_by == "patient_id":
            order_column = ReferralRequest.patient_id
        else:
            order_column = ReferralRequest.created_at
        
        if sort_order.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        referrals = query.offset(offset).limit(limit).all()
        
        # Format response
        referral_list = []
        for r in referrals:
            referral_list.append({
                "id": r.id,
                "patient_id": r.patient_id,
                "referring_location": r.referring_location,
                "staff_name": r.staff_name,
                "referral_date": r.referral_date.isoformat() if r.referral_date else None,
                "referral_time": r.referral_time.isoformat() if r.referral_time else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "status": r.status,
                "urgency_level": r.urgency_level,
                "specialty": r.specialty,
                "cases_summary": r.cases_data[:100] + "..." if r.cases_data and len(r.cases_data) > 100 else r.cases_data,
                "created_by_username": r.created_by_user.username if r.created_by_user else None
            })
        
        return {
            "referrals": referral_list,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": total_count > (offset + limit)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving referrals: {str(e)}")


@router.get("/detail/{referral_id}", response_model=ReferralDetail)
async def get_referral_detail(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed referral information"""
    
    referral = db.query(ReferralRequest).filter(ReferralRequest.id == referral_id).first()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    return {
        "id": referral.id,
        "patient_id": referral.patient_id,
        "referring_location": referral.referring_location,
        "staff_name": referral.staff_name,
        "cases_data": referral.cases_data,
        "prioritization_result": referral.prioritization_result,
        "context_data": referral.context_data,
        "referral_date": referral.referral_date.isoformat() if referral.referral_date else None,
        "referral_time": referral.referral_time.isoformat() if referral.referral_time else None,
        "created_at": referral.created_at.isoformat() if referral.created_at else None,
        "updated_at": referral.updated_at.isoformat() if referral.updated_at else None,
        "status": referral.status,
        "urgency_level": referral.urgency_level,
        "specialty": referral.specialty,
        "created_by_username": referral.created_by_user.username if referral.created_by_user else None
    }


@router.put("/detail/{referral_id}/status")
async def update_referral_status(
    referral_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update referral status"""
    
    valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    referral = db.query(ReferralRequest).filter(ReferralRequest.id == referral_id).first()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    referral.status = status
    db.commit()
    
    return {"message": "Referral status updated successfully", "new_status": status}