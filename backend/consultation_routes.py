from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/consultations", tags=["consultations"])

@router.post("/")
def create_consultation(
    consultation_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    consultation = models.Consultation(
        user_id=current_user.id,
        question=consultation_data.get("question"),
        category=consultation_data.get("category", "general")
    )
    
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    return {
        "message": "Consultation request submitted successfully",
        "consultation": consultation
    }

@router.get("/my-consultations")
def get_my_consultations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    consultations = db.query(models.Consultation).filter(
        models.Consultation.user_id == current_user.id
    ).all()
    return consultations

@router.get("/")
def get_all_consultations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    consultations = db.query(models.Consultation).all()
    return consultations

@router.put("/{consultation_id}/respond")
def respond_to_consultation(
    consultation_id: int,
    response_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    consultation = db.query(models.Consultation).filter(
        models.Consultation.id == consultation_id
    ).first()
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    consultation.response = response_data.get("response")
    consultation.pharmacist_id = current_user.id
    consultation.status = "answered"
    
    db.commit()
    db.refresh(consultation)
    
    return {
        "message": "Response submitted successfully",
        "consultation": consultation
    }