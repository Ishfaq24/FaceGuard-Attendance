"""
Attendance Verification and Recording API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.schemas import (
    AttendanceSessionCreate, AttendanceSessionResponse,
    AttendanceMarkRequest, AttendanceRecordResponse,
    AttendanceHistoryResponse, FraudLogResponse
)
from app.services import (
    AttendanceService, FraudDetectionService,
    FaceVerificationService
)
from app.models import (
    AttendanceSession, Student, AttendanceRecord,
    UserRole
)
from app.ai import LivenessDetector, ChallengeEngine, decode_base64_image

router = APIRouter(prefix="/attendance", tags=["attendance"])
logger = logging.getLogger(__name__)
settings = get_settings()

attendance_service = AttendanceService()
fraud_service = FraudDetectionService()
face_verification_service = FaceVerificationService()
liveness_detector = LivenessDetector()
challenge_engine = ChallengeEngine()


@router.post("/sessions", response_model=AttendanceSessionResponse)
async def create_attendance_session(
    request: AttendanceSessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create attendance session (Teacher only)"""
    if current_user.get("role") != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create attendance sessions"
        )
    
    try:
        session = attendance_service.create_attendance_session(
            db,
            current_user["user_id"],
            request.subject_id,
            request.class_id,
            request.session_name,
            request.description,
            request.scheduled_start_time,
            request.scheduled_end_time,
            request.require_geofence,
            request.require_liveness
        )
        
        return AttendanceSessionResponse.model_validate(session)
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session creation failed"
        )


@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start attendance session"""
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify ownership
    if session.teacher_id != current_user["user_id"] and current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    try:
        session = attendance_service.start_session(db, session_id)
        return {"status": "started", "message": "Attendance session started"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End attendance session"""
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    try:
        session = attendance_service.end_session(db, session_id)
        
        # Get session statistics
        records = attendance_service.get_session_attendance(db, session_id)
        return {
            "status": "ended",
            "total_present": len([r for r in records if r.status == "present"]),
            "total_absent": len([r for r in records if r.status == "absent"]),
            "total_flagged": len([r for r in records if r.is_flagged])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/mark")
async def mark_attendance(
    request: AttendanceMarkRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark attendance with face verification"""
    if current_user.get("role") != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can mark attendance"
        )
    
    # Get student
    student = db.query(Student).filter(
        Student.user_id == current_user["user_id"]
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get session
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    try:
        is_flagged = False
        flag_reason = None
        
        # Verify time window
        is_valid, time_msg = attendance_service.verify_time_window(session)
        if not is_valid:
            is_flagged = True
            flag_reason = time_msg
            logger.warning(f"Attendance outside time window: {time_msg}")
        
        # Verify geofence if required
        geofence_verified = True
        if session.require_geofence:
            geofence_verified, geofence_msg = attendance_service.verify_geofence(
                db,
                session.class_id,
                request.user_latitude,
                request.user_longitude
            )
            if not geofence_verified:
                is_flagged = True
                flag_reason = geofence_msg
                logger.warning(f"Geofence check failed: {geofence_msg}")
        
        # Check duplicate attendance
        is_duplicate, dup_msg = attendance_service.check_duplicate_attendance(
            db,
            request.session_id,
            student.id
        )
        if is_duplicate:
            is_flagged = True
            flag_reason = dup_msg
            
            # Log fraud
            fraud_service.log_fraud_attempt(
                db,
                student.id,
                "duplicate_attendance",
                dup_msg,
                severity="high",
                session_id=session.id
            )
        
        # Verify face
        is_verified, face_confidence, face_msg = face_verification_service.verify_student_face(
            db,
            student.id,
            request.image_base64
        )
        
        if not is_verified:
            is_flagged = True
            flag_reason = face_msg
            
            # Log fraud
            fraud_service.log_fraud_attempt(
                db,
                student.id,
                "face_mismatch",
                face_msg,
                severity="high",
                session_id=session.id,
                evidence_data={"face_confidence": face_confidence}
            )
        
        # Liveness detection if required
        liveness_score = 0.0
        if session.require_liveness and request.challenge_response:
            try:
                image = decode_base64_image(request.challenge_response)
                blink_detected, _ = liveness_detector.detect_blink(image)
                head_pose, _ = liveness_detector.detect_head_movement(image)
                smile_detected, _ = liveness_detector.detect_smile(image)
                
                liveness_score, is_live, _ = liveness_detector.compute_liveness_score(
                    image,
                    blink_detected=blink_detected,
                    head_pose=head_pose,
                    smile_detected=smile_detected
                )
                
                if not is_live:
                    is_flagged = True
                    flag_reason = "Liveness check failed"
                    
                    fraud_service.log_fraud_attempt(
                        db,
                        student.id,
                        "spoof_attempt",
                        "Liveness detection failed",
                        severity="critical",
                        session_id=session.id,
                        evidence_data={"liveness_score": liveness_score}
                    )
            except Exception as e:
                logger.error(f"Liveness check error: {str(e)}")
                liveness_score = 0.0
        
        # Mark attendance
        record = attendance_service.mark_attendance(
            db,
            request.session_id,
            student.id,
            face_confidence if is_verified else 0.0,
            liveness_score,
            geofence_verified,
            is_flagged,
            flag_reason
        )
        
        return {
            "status": "attendance_marked",
            "record_id": record.id,
            "marked_at": record.marked_at,
            "is_flagged": is_flagged,
            "flag_reason": flag_reason,
            "face_confidence": face_confidence if is_verified else 0.0,
            "liveness_score": liveness_score,
            "message": "Attendance marked successfully" if not is_flagged else "Attendance marked but flagged for review"
        }
    
    except Exception as e:
        logger.error(f"Attendance marking error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Attendance marking failed"
        )


@router.get("/history", response_model=AttendanceHistoryResponse)
async def get_attendance_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 30
):
    """Get student attendance history"""
    if current_user.get("role") != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their attendance"
        )
    
    student = db.query(Student).filter(
        Student.user_id == current_user["user_id"]
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    records = attendance_service.get_student_attendance_history(db, student.id, limit)
    
    total_classes = len(records)
    present = len([r for r in records if r.status == "present"])
    absent = len([r for r in records if r.status == "absent"])
    late = len([r for r in records if r.status == "late"])
    
    percentage = (present / total_classes * 100) if total_classes > 0 else 0
    
    return AttendanceHistoryResponse(
        total_sessions=total_classes,
        present=present,
        absent=absent,
        late=late,
        percentage=percentage,
        records=[AttendanceRecordResponse.model_validate(r) for r in records]
    )


@router.get("/sessions/{session_id}/records")
async def get_session_records(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance records for session (Teacher/Admin only)"""
    if current_user.get("role") not in [UserRole.TEACHER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can view session records"
        )
    
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    records = attendance_service.get_session_attendance(db, session_id)
    
    return {
        "session_id": session_id,
        "total_records": len(records),
        "present": len([r for r in records if r.status == "present"]),
        "absent": len([r for r in records if r.status == "absent"]),
        "flagged": len([r for r in records if r.is_flagged]),
        "records": [AttendanceRecordResponse.model_validate(r) for r in records]
    }


@router.get("/fraud-logs")
async def get_fraud_logs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    unresolved_only: bool = True
):
    """Get fraud logs (Admin only)"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view fraud logs"
        )
    
    if unresolved_only:
        logs = fraud_service.get_unresolved_fraud_logs(db)
    else:
        from app.models import FraudLog
        logs = db.query(FraudLog).order_by(FraudLog.created_at.desc()).all()
    
    return {
        "total": len(logs),
        "logs": [FraudLogResponse.model_validate(log) for log in logs]
    }
