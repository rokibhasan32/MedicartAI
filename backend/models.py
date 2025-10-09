from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime

# Association table for prescription medicines
prescription_medicines = Table(
    'prescription_medicines',
    Base.metadata,
    Column('prescription_id', Integer, ForeignKey('prescriptions.id')),
    Column('medicine_id', Integer, ForeignKey('medicines.id')),
    Column('quantity', Integer, default=1)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text)
    role = Column(String(20), default="customer")  # customer, admin, pharmacist
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    prescriptions = relationship("Prescription", back_populates="user")
    orders = relationship("Order", back_populates="user")
    consultations = relationship("Consultation", back_populates="user")

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))  # tablet, liquid, capsule, etc.
    manufacturer = Column(String(100))
    stock = Column(Integer, default=0)
    requires_prescription = Column(Boolean, default=False)
    image_url = Column(String(500))
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="medicine")
    prescriptions = relationship("Prescription", secondary=prescription_medicines, back_populates="medicines")

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")  # pending, verified, rejected, processing
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="prescriptions")
    medicines = relationship("Medicine", secondary=prescription_medicines, back_populates="prescriptions")
    orders = relationship("Order", back_populates="prescription")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, confirmed, processing, shipped, delivered, cancelled
    shipping_address = Column(Text)
    payment_status = Column(String(20), default="pending")  # pending, paid, failed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    prescription = relationship("Prescription", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    medicine = relationship("Medicine", back_populates="order_items")

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pharmacist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    response = Column(Text)
    status = Column(String(20), default="pending")  # pending, answered, closed
    category = Column(String(50), default="general")  # medication, side-effects, interactions, general, emergency
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="consultations", foreign_keys=[user_id])
    pharmacist = relationship("User", foreign_keys=[pharmacist_id])