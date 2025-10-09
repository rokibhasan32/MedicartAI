from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from auth import router as auth_router, get_password_hash
from medicine_routes import router as medicine_router
from prescription_routes import router as prescription_router
from order_routes import router as order_router
from consultation_routes import router as consultation_router
from ai_routes import router as ai_router
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MediCart Pharmacy API",
    description="Backend API for MediCart Pharmacy",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded prescriptions
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(medicine_router, prefix="/api")
app.include_router(prescription_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(consultation_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "MediCart Pharmacy API is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MediCart Pharmacy API",
        "version": "1.0.0"
    }

# Initialize with sample data
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    try:
        # Create sample medicines if none exist
        if db.query(models.Medicine).count() == 0:
            sample_medicines = [
                models.Medicine(
                    name="Napa",
                    description="Pain reliever and fever reducer",
                    price=200.00,
                    category="tablet",
                    manufacturer="Beximco",
                    stock=100,
                    requires_prescription=False,
                    is_featured=True
                ),
                models.Medicine(
                    name="Disprin",
                    description="Pain reliever tablet",
                    price=250.00,
                    category="tablet",
                    manufacturer="Square",
                    stock=50,
                    requires_prescription=False,
                    is_featured=True
                ),
                models.Medicine(
                    name="Levofox",
                    description="Antibiotic medication",
                    price=500.00,
                    category="tablet",
                    manufacturer="Incepta",
                    stock=30,
                    requires_prescription=True,
                    is_featured=True
                )
            ]
            db.add_all(sample_medicines)
            db.commit()
        
        # Create admin user if none exists
        if db.query(models.User).filter(models.User.email == "admin@medicart.com").first() is None:
            from auth import get_password_hash
            admin_user = models.User(
                name="Admin User",
                email="admin@medicart.com",
                password=get_password_hash("admin123"),
                phone="+8801000000000",
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            
    except Exception as e:
        print(f"Startup error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )