from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models
from database import get_db

router = APIRouter(prefix="/medicines", tags=["medicines"])

@router.get("/")
def get_medicines(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Medicine)
    
    if category:
        query = query.filter(models.Medicine.category == category)
    
    if search:
        query = query.filter(models.Medicine.name.ilike(f"%{search}%"))
    
    medicines = query.offset(skip).limit(limit).all()
    return medicines

@router.get("/featured")
def get_featured_medicines(db: Session = Depends(get_db)):
    medicines = db.query(models.Medicine).filter(models.Medicine.is_featured == True).limit(10).all()
    return medicines

@router.get("/{medicine_id}")
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@router.post("/")
def create_medicine(medicine_data: dict, db: Session = Depends(get_db)):
    db_medicine = models.Medicine(**medicine_data)
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@router.put("/{medicine_id}")
def update_medicine(medicine_id: int, medicine_data: dict, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    for key, value in medicine_data.items():
        setattr(medicine, key, value)
    
    db.commit()
    db.refresh(medicine)
    return medicine

@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    db.delete(medicine)
    db.commit()
    return {"message": "Medicine deleted successfully"}