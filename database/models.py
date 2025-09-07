from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Time, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from passlib.context import CryptContext
import os

Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    department = Column(String(50))  # e.g., Emergency, Cardiology, Administration
    role = Column(String(30), default="staff")  # staff, admin, doctor, nurse
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    hospital_id = Column(String(20))  # Hospital/Health Board identifier
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationship to referrals
    referral_requests = relationship("ReferralRequest", back_populates="created_by_user")
    query_logs = relationship("QueryLog", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password for storage"""
        return pwd_context.hash(password)

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    age = Column(Integer)
    sex = Column(String(10))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to referrals
    referrals = relationship("ReferralRequest", back_populates="patient")

class ReferralRequest(Base):
    __tablename__ = "referral_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"))
    referring_location = Column(String(100))
    staff_name = Column(String(100))
    cases_data = Column(Text)
    prioritization_result = Column(Text)
    context_data = Column(Text)
    referral_date = Column(Date, default=date.today)
    referral_time = Column(Time, default=lambda: datetime.now().time())
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='pending')
    urgency_level = Column(String(20))
    specialty = Column(String(50))
    
    # Authentication tracking
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    patient = relationship("Patient", back_populates="referrals")
    created_by_user = relationship("User", back_populates="referral_requests")

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    referral_request_id = Column(Integer, ForeignKey("referral_requests.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(Text)
    query_type = Column(String(20))  # general, context_aware, referral
    response_llama = Column(Text)
    response_llava = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    referral = relationship("ReferralRequest")
    user = relationship("User", back_populates="query_logs")

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    ip_address = Column(String(45))  # IPv6 compatible
    success = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(Text)