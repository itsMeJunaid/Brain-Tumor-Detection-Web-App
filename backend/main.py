from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import uuid
from typing import Optional

from database import engine, get_db, Base
from models import Doctor, Scan
from auth import (
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_doctor
)
from prediction import predict_brain_tumor, load_model
from pdf_generator import generate_medical_report

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(title="Brain Tumor Detection API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load ML model at startup
@app.on_event("startup")
async def startup_event():
    load_model()
    print("✅ Model loaded successfully!")

# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    license_number: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if doctor already exists
    existing_doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_license = db.query(Doctor).filter(Doctor.license_number == license_number).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="License number already registered")
    
    # Create new doctor
    hashed_password = get_password_hash(password)
    new_doctor = Doctor(
        email=email,
        full_name=full_name,
        license_number=license_number,
        hashed_password=hashed_password
    )
    
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return {"message": "Doctor registered successfully", "doctor_id": new_doctor.id}

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.email == form_data.username).first()
    
    if not doctor or not verify_password(form_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": doctor.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "doctor": {
            "id": doctor.id,
            "email": doctor.email,
            "full_name": doctor.full_name,
            "license_number": doctor.license_number
        }
    }

@app.get("/me")
async def get_current_user(current_doctor: Doctor = Depends(get_current_doctor)):
    return {
        "id": current_doctor.id,
        "email": current_doctor.email,
        "full_name": current_doctor.full_name,
        "license_number": current_doctor.license_number
    }

# ============================================================
# PREDICTION ENDPOINTS
# ============================================================

@app.post("/predict")
async def predict_tumor(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_id: str = Form(...),
    notes: Optional[str] = Form(None),
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filenames
    unique_id = str(uuid.uuid4())
    image_filename = f"{unique_id}_original.jpg"
    gradcam_filename = f"{unique_id}_gradcam.jpg"
    
    image_path = os.path.join("uploads", image_filename)
    gradcam_path = os.path.join("uploads", gradcam_filename)
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Perform prediction
    try:
        prediction, confidence = await predict_brain_tumor(
            image_bytes, image_path, gradcam_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    
    # Save to database
    new_scan = Scan(
        doctor_id=current_doctor.id,
        patient_name=patient_name,
        patient_id=patient_id,
        image_path=image_path,
        prediction=prediction,
        confidence=confidence,
        gradcam_path=gradcam_path,
        notes=notes
    )
    
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    
    return {
        "scan_id": new_scan.id,
        "prediction": prediction,
        "confidence": confidence,
        "image_url": f"/uploads/{image_filename}",
        "gradcam_url": f"/uploads/{gradcam_filename}",
        "patient_name": patient_name,
        "patient_id": patient_id,
        "scan_date": new_scan.scan_date.isoformat()
    }

# ============================================================
# HISTORY & REPORTS ENDPOINTS
# ============================================================

@app.get("/scans")
async def get_scans(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    scans = db.query(Scan).filter(Scan.doctor_id == current_doctor.id).order_by(Scan.scan_date.desc()).all()
    
    return [{
        "id": scan.id,
        "patient_name": scan.patient_name,
        "patient_id": scan.patient_id,
        "prediction": scan.prediction,
        "confidence": scan.confidence,
        "scan_date": scan.scan_date.isoformat(),
        "image_url": f"/{scan.image_path}",
        "gradcam_url": f"/{scan.gradcam_path}",
        "notes": scan.notes
    } for scan in scans]

@app.get("/scan/{scan_id}")
async def get_scan_details(
    scan_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.doctor_id == current_doctor.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "id": scan.id,
        "patient_name": scan.patient_name,
        "patient_id": scan.patient_id,
        "prediction": scan.prediction,
        "confidence": scan.confidence,
        "scan_date": scan.scan_date.isoformat(),
        "image_url": f"/{scan.image_path}",
        "gradcam_url": f"/{scan.gradcam_path}",
        "notes": scan.notes
    }

@app.get("/download-report/{scan_id}")
async def download_report(
    scan_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.doctor_id == current_doctor.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Prepare data for PDF
    scan_data = {
        'patient_name': scan.patient_name,
        'patient_id': scan.patient_id,
        'scan_date': scan.scan_date.strftime('%Y-%m-%d %H:%M'),
        'doctor_name': current_doctor.full_name,
        'prediction': scan.prediction,
        'confidence': scan.confidence,
        'image_path': scan.image_path,
        'gradcam_path': scan.gradcam_path,
        'notes': scan.notes or 'No additional notes provided.'
    }
    
    # Generate PDF
    pdf_filename = f"report_{scan_id}_{uuid.uuid4()}.pdf"
    pdf_path = os.path.join("reports", pdf_filename)
    
    try:
        generate_medical_report(scan_data, pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"Brain_Tumor_Report_{scan.patient_name}_{scan_id}.pdf"
    )

# ============================================================
# DELETE SCAN ENDPOINT
# ============================================================

@app.delete("/scan/{scan_id}")
async def delete_scan(
    scan_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.doctor_id == current_doctor.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Delete image files
    try:
        if os.path.exists(scan.image_path):
            os.remove(scan.image_path)
        if os.path.exists(scan.gradcam_path):
            os.remove(scan.gradcam_path)
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Delete database record
    db.delete(scan)
    db.commit()
    
    return {"message": "Scan deleted successfully"}

# ============================================================
# STATS ENDPOINT
# ============================================================
@app.get("/stats")
async def get_stats(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    total_scans = db.query(Scan).filter(Scan.doctor_id == current_doctor.id).count()
    tumor_detected = db.query(Scan).filter(
        Scan.doctor_id == current_doctor.id,
        Scan.prediction == "Tumor Detected"  # match your prediction label
    ).count()
    no_tumor = total_scans - tumor_detected
    
    return {
        "total_scans": total_scans,
        "tumor_detected": tumor_detected,
        "no_tumor": no_tumor
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)