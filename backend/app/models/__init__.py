"""
SQLAlchemy ORM Models for FaceGuard Attendance System
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, 
    Text, ForeignKey, Enum as SQLEnum, JSON, Index,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """User model - base class for all users"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    profile_picture_url = Column(String(512), nullable=True)
    
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    admin_profile = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_role_active", "role", "is_active"),
    )


class Student(Base):
    """Student profile model"""
    __tablename__ = "students"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False, index=True)
    
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    face_enrolled = Column(Boolean, default=False, index=True)
    face_enrollment_date = Column(DateTime, nullable=True)
    biometric_status = Column(String(50), default="pending")  # pending, enrolled, flagged
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    department = relationship("Department", back_populates="students")
    class_rel = relationship("Class", back_populates="students")
    face_embeddings = relationship("FaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
    fraud_logs = relationship("FraudLog", back_populates="student", cascade="all, delete-orphan")


class Teacher(Base):
    """Teacher profile model"""
    __tablename__ = "teachers"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    qualification = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    
    join_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    department = relationship("Department", back_populates="teachers")
    classes = relationship("Class", back_populates="teacher")
    attendance_sessions = relationship("AttendanceSession", back_populates="teacher", cascade="all, delete-orphan")


class Admin(Base):
    """Admin profile model"""
    __tablename__ = "admins"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    permissions = Column(JSON, default={})
    
    join_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="admin_profile")


class Department(Base):
    """Department model"""
    __tablename__ = "departments"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    head_teacher_id = Column(String(36), ForeignKey("teachers.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = relationship("Student", back_populates="department")
    teachers = relationship("Teacher", back_populates="department")
    classes = relationship("Class", back_populates="department", cascade="all, delete-orphan")


class Class(Base):
    """Class/Section model"""
    __tablename__ = "classes"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    teacher_id = Column(String(36), ForeignKey("teachers.id"), nullable=False, index=True)
    
    capacity = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="classes")
    teacher = relationship("Teacher", back_populates="classes")
    students = relationship("Student", back_populates="class_rel")
    subjects = relationship("Subject", back_populates="class_rel", cascade="all, delete-orphan")


class Subject(Base):
    """Subject model"""
    __tablename__ = "subjects"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False, index=True)
    credits = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_rel = relationship("Class", back_populates="subjects")
    attendance_sessions = relationship("AttendanceSession", back_populates="subject", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("class_id", "code", name="uq_subject_class_code"),
    )


class FaceEmbedding(Base):
    """Face embedding storage for biometric data"""
    __tablename__ = "face_embeddings"
    
    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    embedding = Column(JSON, nullable=False)  # Serialized numpy array
    image_url = Column(String(512), nullable=True)
    
    quality_score = Column(Float, default=0.0)  # 0-100
    is_primary = Column(Boolean, default=False)
    
    capture_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    student = relationship("Student", back_populates="face_embeddings")
    
    __table_args__ = (
        Index("idx_face_embedding_student_date", "student_id", "created_at"),
    )


class GeofenceConfig(Base):
    """Geofence configuration for attendance verification"""
    __tablename__ = "geofence_configs"
    
    id = Column(String(36), primary_key=True, index=True)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False, index=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, default=100.0)
    
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_geofence_class_active", "class_id", "is_active"),
    )


class AttendanceSession(Base):
    """Attendance session created by teacher"""
    __tablename__ = "attendance_sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    teacher_id = Column(String(36), ForeignKey("teachers.id"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False, index=True)
    
    session_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    status = Column(String(50), default="pending")  # pending, active, closed
    require_geofence = Column(Boolean, default=True)
    require_liveness = Column(Boolean, default=True)
    
    scheduled_start_time = Column(DateTime, nullable=False, index=True)
    scheduled_end_time = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="attendance_sessions")
    subject = relationship("Subject", back_populates="attendance_sessions")
    class_rel = relationship("Class")
    attendance_records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_session_teacher_status", "teacher_id", "status"),
        Index("idx_session_class_status", "class_id", "status"),
        Index("idx_session_datetime", "scheduled_start_time", "scheduled_end_time"),
    )


class AttendanceRecord(Base):
    """Attendance record for each student in a session"""
    __tablename__ = "attendance_records"
    
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("attendance_sessions.id"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    
    status = Column(String(50), default="present")  # present, absent, late
    marked_at = Column(DateTime, default=datetime.utcnow)
    
    face_match_confidence = Column(Float, nullable=True)
    liveness_score = Column(Float, nullable=True)
    geofence_verified = Column(Boolean, default=False)
    
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(500), nullable=True)
    is_approved = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")
    
    __table_args__ = (
        Index("idx_attendance_session_student", "session_id", "student_id"),
        Index("idx_attendance_student_date", "student_id", "marked_at"),
        Index("idx_attendance_flagged_status", "is_flagged", "is_approved"),
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )


class FraudLog(Base):
    """Fraud attempt logging and monitoring"""
    __tablename__ = "fraud_logs"
    
    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("attendance_sessions.id"), nullable=True, index=True)
    
    fraud_type = Column(String(100), nullable=False, index=True)  # face_mismatch, spoof_attempt, duplicate, geofence_violation, etc.
    severity = Column(String(50), default="medium")  # low, medium, high, critical
    description = Column(Text, nullable=False)
    
    evidence_data = Column(JSON, nullable=True)
    is_resolved = Column(Boolean, default=False, index=True)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="fraud_logs")
    
    __table_args__ = (
        Index("idx_fraud_student_type", "student_id", "fraud_type"),
        Index("idx_fraud_severity_resolved", "severity", "is_resolved"),
        Index("idx_fraud_created_date", "created_at"),
    )


class Notification(Base):
    """Notification system"""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # alert, info, warning
    
    is_read = Column(Boolean, default=False, index=True)
    action_url = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_notification_user_read", "user_id", "is_read"),
    )


class AuditLog(Base):
    """System audit trail"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=True)
    
    changes = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )
