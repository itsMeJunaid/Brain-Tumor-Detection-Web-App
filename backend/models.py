from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    license_number = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scans = relationship("Scan", back_populates="doctor")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_name = Column(String)
    patient_id = Column(String)
    image_path = Column(String)
    prediction = Column(String)  # "Tumor" or "No Tumor"
    confidence = Column(Float)
    gradcam_path = Column(String)
    notes = Column(String, nullable=True)
    scan_date = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("Doctor", back_populates="scans")