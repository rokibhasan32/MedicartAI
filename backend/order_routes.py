from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
def create_order(
    order_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Calculate total amount and validate items
    total_amount = 0
    order_items = []
    
    for item in order_data.get("items", []):
        medicine = db.query(models.Medicine).filter(
            models.Medicine.id == item["medicine_id"]
        ).first()
        
        if not medicine:
            raise HTTPException(status_code=404, detail=f"Medicine {item['medicine_id']} not found")
        
        if medicine.stock < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {medicine.name}. Available: {medicine.stock}"
            )
        
        total_amount += medicine.price * item["quantity"]
        
        # Update stock
        medicine.stock -= item["quantity"]
        
        order_items.append({
            "medicine_id": medicine.id,
            "quantity": item["quantity"],
            "price": medicine.price
        })
    
    # Create order
    order = models.Order(
        user_id=current_user.id,
        total_amount=total_amount,
        shipping_address=order_data.get("shipping_address"),
        prescription_id=order_data.get("prescription_id")
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    for item in order_items:
        order_item = models.OrderItem(
            order_id=order.id,
            medicine_id=item["medicine_id"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    return {
        "message": "Order created successfully",
        "order": order
    }

@router.get("/my-orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).all()
    return orders

@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return order

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_data.get("status", order.status)
    db.commit()
    db.refresh(order)
    
    return {
        "message": "Order status updated successfully",
        "order": order
    }