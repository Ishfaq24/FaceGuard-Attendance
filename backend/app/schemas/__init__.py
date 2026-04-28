"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


# ============= Authentication Schemas =============
class SignupRequest(BaseModel):
    """User signup request"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8)
    role: UserRole
    phone_number: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============= User Schemas =============
class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    full_name: str
    role: UserRole
    phone_number: Optional[str]
    profile_picture_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None


# ============= Student Schemas =============
class StudentCreate(BaseModel):
    """Student creation schema"""
    user_id: str
    roll_number: str
    department_id: str
    class_id: str


class StudentUpdate(BaseModel):
    """Student update schema"""
    roll_number: Optional[str] = None
    class_id: Optional[str] = None


class StudentResponse(BaseModel):
    """Student response model"""
    id: str
    user_id: str
    roll_number: str
    department_id: str
    class_id: str
    face_enrolled: bool
    biometric_status: str
    enrollment_date: datetime
    face_enrollment_date: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============= Face Enrollment Schemas =============
class FaceEnrollmentStart(BaseModel):
    """Start face enrollment"""
    pass


class FaceImageCapture(BaseModel):
    """Face image capture during enrollment"""
    image_base64: str = Field(..., description="Base64 encoded image")
    quality_score: float = Field(..., ge=0.0, le=100.0)


class FaceEnrollmentComplete(BaseModel):
    """Complete face enrollment"""
    pass


class FaceEnrollmentResponse(BaseModel):
    """Face enrollment response"""
    enrollment_id: str
    status: str
    images_captured: int
    images_required: int
    message: str


# ============= Face Recognition Schemas =============
class FaceVerificationRequest(BaseModel):
    """Face verification request"""
    image_base64: str
    user_latitude: Optional[float] = None
    user_longitude: Optional[float] = None


class FaceVerificationResponse(BaseModel):
    """Face verification response"""
    verified: bool
    confidence: float
    student_id: Optional[str] = None
    liveness_detected: bool
    liveness_score: float
    spoof_detected: bool
    message: str


class LivenessChallenge(BaseModel):
    """Liveness challenge"""
    challenge_type: str  # blink, head_left, head_right, smile, nod
    instructions: str
    timeout_seconds: int


class LivenessChallengeResponse(BaseModel):
    """Liveness challenge response"""
    challenge_response: str  # base64 encoded video/images


# ============= Attendance Session Schemas =============
class GeofenceConfigCreate(BaseModel):
    """Geofence configuration creation"""
    class_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: float = Field(default=100.0, ge=10.0, le=1000.0)


class GeofenceConfigResponse(BaseModel):
    """Geofence configuration response"""
    id: str
    class_id: str
    latitude: float
    longitude: float
    radius_meters: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceSessionCreate(BaseModel):
    """Attendance session creation"""
    subject_id: str
    class_id: str
    session_name: str
    description: Optional[str] = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime
    require_geofence: bool = True
    require_liveness: bool = True


class AttendanceSessionUpdate(BaseModel):
    """Attendance session update"""
    session_name: Optional[str] = None
    description: Optional[str] = None
    scheduled_end_time: Optional[datetime] = None
    status: Optional[str] = None


class AttendanceSessionResponse(BaseModel):
    """Attendance session response"""
    id: str
    teacher_id: str
    subject_id: str
    class_id: str
    session_name: str
    description: Optional[str]
    status: str
    require_geofence: bool
    require_liveness: bool
    scheduled_start_time: datetime
    scheduled_end_time: datetime
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Attendance Record Schemas =============
class AttendanceMarkRequest(BaseModel):
    """Mark attendance request"""
    session_id: str
    image_base64: str
    user_latitude: float
    user_longitude: float
    challenge_response: Optional[str] = None


class AttendanceRecordResponse(BaseModel):
    """Attendance record response"""
    id: str
    session_id: str
    student_id: str
    status: str
    marked_at: datetime
    face_match_confidence: Optional[float]
    liveness_score: Optional[float]
    geofence_verified: bool
    is_flagged: bool
    flag_reason: Optional[str]
    is_approved: bool
    
    class Config:
        from_attributes = True


class AttendanceHistoryResponse(BaseModel):
    """Attendance history"""
    total_sessions: int
    present: int
    absent: int
    late: int
    percentage: float
    records: List[AttendanceRecordResponse]


# ============= Fraud Log Schemas =============
class FraudLogResponse(BaseModel):
    """Fraud log response"""
    id: str
    student_id: str
    session_id: Optional[str]
    fraud_type: str
    severity: str
    description: str
    evidence_data: Optional[dict]
    is_resolved: bool
    resolution_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============= Analytics Schemas =============
class AttendanceAnalytics(BaseModel):
    """Attendance analytics"""
    total_classes: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float
    average_face_confidence: float
    average_liveness_score: float


class FraudStatistics(BaseModel):
    """Fraud statistics"""
    total_fraud_attempts: int
    by_type: dict
    by_severity: dict
    resolved_count: int
    unresolved_count: int


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_students: int
    face_enrolled: int
    face_not_enrolled: int
    today_attendance: int
    fraud_alerts: int
    sessions_today: int


# ============= Notification Schemas =============
class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Department Schemas =============
class DepartmentCreate(BaseModel):
    """Department creation"""
    name: str
    code: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    """Department response"""
    id: str
    name: str
    code: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Class Schemas =============
class ClassCreate(BaseModel):
    """Class creation"""
    name: str
    code: str
    semester: int
    department_id: str
    teacher_id: str
    capacity: int = 60


class ClassResponse(BaseModel):
    """Class response"""
    id: str
    name: str
    code: str
    semester: int
    department_id: str
    teacher_id: str
    capacity: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Subject Schemas =============
class SubjectCreate(BaseModel):
    """Subject creation"""
    name: str
    code: str
    class_id: str
    credits: int = 3


class SubjectResponse(BaseModel):
    """Subject response"""
    id: str
    name: str
    code: str
    class_id: str
    credits: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Model update to have forward references resolved
LoginResponse.model_rebuild()
