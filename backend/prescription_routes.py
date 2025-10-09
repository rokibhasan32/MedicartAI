from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_current_user
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

UPLOAD_DIR = "uploads/prescriptions"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_prescription(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create prescription record
    prescription = models.Prescription(
        user_id=current_user.id,
        image_url=f"/{file_path}",
        status="pending"
    )
    
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    
    return {
        "message": "Prescription uploaded successfully",
        "prescription": prescription
    }

@router.get("/my-prescriptions")
def get_my_prescriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    prescriptions = db.query(models.Prescription).filter(
        models.Prescription.user_id == current_user.id
    ).all()
    return prescriptions

@router.get("/{prescription_id}")
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    prescription = db.query(models.Prescription).filter(
        models.Prescription.id == prescription_id
    ).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if prescription.user_id != current_user.id and current_user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return prescription

@router.put("/{prescription_id}/verify")
def verify_prescription(
    prescription_id: int,
    verification_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "pharmacist"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    prescription = db.query(models.Prescription).filter(
        models.Prescription.id == prescription_id
    ).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    prescription.status = verification_data.get("status", prescription.status)
    prescription.verification_notes = verification_data.get("verification_notes")
    prescription.verified_by = current_user.id
    
    db.commit()
    db.refresh(prescription)
    
    return {
        "message": "Prescription verified successfully",
        "prescription": prescription
    }