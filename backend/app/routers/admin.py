"""
Admin Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import (
    DepartmentCreate, DepartmentResponse,
    ClassCreate, ClassResponse,
    SubjectCreate, SubjectResponse,
    StudentResponse, UserResponse, GeofenceConfigCreate,
    GeofenceConfigResponse
)
from app.models import (
    Department, Class, Subject, Student, User,
    GeofenceConfig, UserRole, AttendanceRecord
)
from app.services import FraudDetectionService

router = APIRouter(prefix="/admin", tags=["admin"])
fraud_service = FraudDetectionService()


@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    request: DepartmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create department (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create departments"
        )
    
    # Check if code already exists
    existing = db.query(Department).filter(
        Department.code == request.code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department code already exists"
        )
    
    department = Department(
        id=str(uuid.uuid4()),
        name=request.name,
        code=request.code,
        description=request.description
    )
    
    db.add(department)
    db.commit()
    db.refresh(department)
    
    return DepartmentResponse.model_validate(department)


@router.get("/departments")
async def list_departments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all departments"""
    departments = db.query(Department).all()
    return {
        "total": len(departments),
        "departments": [DepartmentResponse.model_validate(d) for d in departments]
    }


@router.post("/classes", response_model=ClassResponse)
async def create_class(
    request: ClassCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create class (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create classes"
        )
    
    # Verify department exists
    department = db.query(Department).filter(
        Department.id == request.department_id
    ).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if code already exists
    existing = db.query(Class).filter(
        Class.code == request.code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class code already exists"
        )
    
    class_obj = Class(
        id=str(uuid.uuid4()),
        name=request.name,
        code=request.code,
        semester=request.semester,
        department_id=request.department_id,
        teacher_id=request.teacher_id,
        capacity=request.capacity
    )
    
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    return ClassResponse.model_validate(class_obj)


@router.get("/classes")
async def list_classes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    department_id: str = None
):
    """List classes"""
    query = db.query(Class)
    
    if department_id:
        query = query.filter(Class.department_id == department_id)
    
    classes = query.all()
    
    return {
        "total": len(classes),
        "classes": [ClassResponse.model_validate(c) for c in classes]
    }


@router.post("/subjects", response_model=SubjectResponse)
async def create_subject(
    request: SubjectCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create subject (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create subjects"
        )
    
    subject = Subject(
        id=str(uuid.uuid4()),
        name=request.name,
        code=request.code,
        class_id=request.class_id,
        credits=request.credits
    )
    
    db.add(subject)
    db.commit()
    db.refresh(subject)
    
    return SubjectResponse.model_validate(subject)


@router.post("/geofence", response_model=GeofenceConfigResponse)
async def create_geofence(
    request: GeofenceConfigCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create geofence configuration (Teacher only)"""
    if current_user.get("role") != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create geofences"
        )
    
    geofence = GeofenceConfig(
        id=str(uuid.uuid4()),
        class_id=request.class_id,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_meters=request.radius_meters,
        is_active=True
    )
    
    db.add(geofence)
    db.commit()
    db.refresh(geofence)
    
    return GeofenceConfigResponse.model_validate(geofence)


@router.get("/analytics/attendance")
async def get_attendance_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    class_id: str = None,
    days: int = 30
):
    """Get attendance analytics (Teacher/Admin only)"""
    if current_user.get("role") not in [UserRole.TEACHER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.marked_at >= start_date
    )
    
    if class_id:
        query = query.filter(
            AttendanceRecord.session.class_id == class_id
        )
    
    records = query.all()
    
    total = len(records)
    present = len([r for r in records if r.status == "present"])
    absent = len([r for r in records if r.status == "absent"])
    flagged = len([r for r in records if r.is_flagged])
    
    return {
        "period_days": days,
        "total_records": total,
        "present": present,
        "absent": absent,
        "flagged": flagged,
        "attendance_percentage": (present / total * 100) if total > 0 else 0,
        "fraud_percentage": (flagged / total * 100) if total > 0 else 0
    }


@router.get("/analytics/fraud")
async def get_fraud_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 90
):
    """Get fraud analytics (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view fraud analytics"
        )
    
    from datetime import datetime, timedelta
    from app.models import FraudLog
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(FraudLog).filter(
        FraudLog.created_at >= start_date
    ).all()
    
    fraud_by_type = {}
    fraud_by_severity = {}
    
    for log in logs:
        fraud_by_type[log.fraud_type] = fraud_by_type.get(log.fraud_type, 0) + 1
        fraud_by_severity[log.severity] = fraud_by_severity.get(log.severity, 0) + 1
    
    return {
        "period_days": days,
        "total_attempts": len(logs),
        "unresolved": len([l for l in logs if not l.is_resolved]),
        "by_type": fraud_by_type,
        "by_severity": fraud_by_severity,
        "critical_count": fraud_by_severity.get("critical", 0)
    }


@router.get("/users")
async def list_users(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    role: str = None
):
    """List users (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list users"
        )
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    
    return {
        "total": len(users),
        "users": [UserResponse.model_validate(u) for u in users]
    }


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate user (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage users"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user.email} deactivated"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate user (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage users"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": f"User {user.email} activated"}
