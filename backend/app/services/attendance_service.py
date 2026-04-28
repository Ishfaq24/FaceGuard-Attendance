"""
Attendance Verification and Recording Services
"""
import uuid
import logging
import math
from datetime import datetime
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import (
    AttendanceSession, AttendanceRecord, Student, FraudLog,
    GeofenceConfig
)

logger = logging.getLogger(__name__)


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance


class AttendanceService:
    """Attendance marking and verification service"""
    
    @staticmethod
    def create_attendance_session(
        db: Session,
        teacher_id: str,
        subject_id: str,
        class_id: str,
        session_name: str,
        description: Optional[str],
        scheduled_start_time: datetime,
        scheduled_end_time: datetime,
        require_geofence: bool = True,
        require_liveness: bool = True
    ) -> AttendanceSession:
        """
        Create new attendance session
        
        Args:
            db: Database session
            teacher_id: Teacher ID
            subject_id: Subject ID
            class_id: Class ID
            session_name: Session name
            description: Session description
            scheduled_start_time: Start time
            scheduled_end_time: End time
            require_geofence: Whether geofence is required
            require_liveness: Whether liveness detection is required
            
        Returns:
            Created AttendanceSession
        """
        session = AttendanceSession(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            subject_id=subject_id,
            class_id=class_id,
            session_name=session_name,
            description=description,
            scheduled_start_time=scheduled_start_time,
            scheduled_end_time=scheduled_end_time,
            require_geofence=require_geofence,
            require_liveness=require_liveness,
            status="pending"
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Attendance session created: {session.id}")
        return session
    
    @staticmethod
    def start_session(db: Session, session_id: str) -> AttendanceSession:
        """Start attendance session"""
        session = db.query(AttendanceSession).filter(
            AttendanceSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        session.status = "active"
        session.actual_start_time = datetime.utcnow()
        db.commit()
        db.refresh(session)
        
        logger.info(f"Attendance session started: {session_id}")
        return session
    
    @staticmethod
    def end_session(db: Session, session_id: str) -> AttendanceSession:
        """End attendance session"""
        session = db.query(AttendanceSession).filter(
            AttendanceSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        session.status = "closed"
        session.actual_end_time = datetime.utcnow()
        db.commit()
        db.refresh(session)
        
        logger.info(f"Attendance session ended: {session_id}")
        return session
    
    @staticmethod
    def verify_time_window(
        session: AttendanceSession,
        buffer_minutes: int = 5
    ) -> Tuple[bool, str]:
        """
        Verify if current time is within session window
        
        Args:
            session: AttendanceSession
            buffer_minutes: Buffer before start and after end
            
        Returns:
            Tuple of (is_valid, reason)
        """
        from datetime import timedelta
        
        current_time = datetime.utcnow()
        buffer = timedelta(minutes=buffer_minutes)
        
        if current_time < session.scheduled_start_time - buffer:
            return False, "Attendance session not yet started"
        
        if current_time > session.scheduled_end_time + buffer:
            return False, "Attendance session has ended"
        
        return True, "Within time window"
    
    @staticmethod
    def verify_geofence(
        db: Session,
        class_id: str,
        user_latitude: float,
        user_longitude: float
    ) -> Tuple[bool, str]:
        """
        Verify if student is within geofence
        
        Args:
            db: Database session
            class_id: Class ID
            user_latitude: Student's latitude
            user_longitude: Student's longitude
            
        Returns:
            Tuple of (is_within_geofence, reason)
        """
        geofence = db.query(GeofenceConfig).filter(
            and_(
                GeofenceConfig.class_id == class_id,
                GeofenceConfig.is_active == True
            )
        ).first()
        
        if not geofence:
            logger.warning(f"No active geofence found for class {class_id}")
            return False, "Geofence not configured"
        
        distance = haversine_distance(
            geofence.latitude, geofence.longitude,
            user_latitude, user_longitude
        )
        
        if distance <= geofence.radius_meters:
            return True, f"Within geofence (distance: {distance:.0f}m)"
        else:
            return False, f"Outside geofence (distance: {distance:.0f}m, limit: {geofence.radius_meters}m)"
    
    @staticmethod
    def check_duplicate_attendance(
        db: Session,
        session_id: str,
        student_id: str
    ) -> Tuple[bool, str]:
        """
        Check if student already marked attendance for session
        
        Args:
            db: Database session
            session_id: Session ID
            student_id: Student ID
            
        Returns:
            Tuple of (is_duplicate, reason)
        """
        existing = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_id
            )
        ).first()
        
        if existing:
            return True, f"Already marked attendance at {existing.marked_at}"
        
        return False, "First attendance for this session"
    
    @staticmethod
    def mark_attendance(
        db: Session,
        session_id: str,
        student_id: str,
        face_match_confidence: float,
        liveness_score: float,
        geofence_verified: bool,
        is_flagged: bool = False,
        flag_reason: Optional[str] = None
    ) -> AttendanceRecord:
        """
        Mark student attendance
        
        Args:
            db: Database session
            session_id: Session ID
            student_id: Student ID
            face_match_confidence: Face matching confidence
            liveness_score: Liveness detection score
            geofence_verified: Geofence verification status
            is_flagged: Whether to flag for fraud review
            flag_reason: Reason for flagging
            
        Returns:
            Created AttendanceRecord
        """
        record = AttendanceRecord(
            id=str(uuid.uuid4()),
            session_id=session_id,
            student_id=student_id,
            status="present",
            marked_at=datetime.utcnow(),
            face_match_confidence=face_match_confidence,
            liveness_score=liveness_score,
            geofence_verified=geofence_verified,
            is_flagged=is_flagged,
            flag_reason=flag_reason,
            is_approved=not is_flagged
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        logger.info(f"Attendance marked: student={student_id}, session={session_id}")
        return record
    
    @staticmethod
    def get_session_attendance(
        db: Session,
        session_id: str
    ):
        """Get all attendance records for a session"""
        return db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id
        ).all()
    
    @staticmethod
    def get_student_attendance_history(
        db: Session,
        student_id: str,
        limit: int = 30
    ):
        """Get student's recent attendance history"""
        return db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id
        ).order_by(AttendanceRecord.marked_at.desc()).limit(limit).all()


class FraudDetectionService:
    """Fraud detection and logging service"""
    
    @staticmethod
    def log_fraud_attempt(
        db: Session,
        student_id: str,
        fraud_type: str,
        description: str,
        severity: str = "medium",
        session_id: Optional[str] = None,
        evidence_data: Optional[dict] = None
    ) -> FraudLog:
        """
        Log fraud attempt
        
        Args:
            db: Database session
            student_id: Student ID
            fraud_type: Type of fraud
            description: Fraud description
            severity: Severity level (low, medium, high, critical)
            session_id: Optional session ID
            evidence_data: Optional evidence data
            
        Returns:
            Created FraudLog
        """
        fraud_log = FraudLog(
            id=str(uuid.uuid4()),
            student_id=student_id,
            session_id=session_id,
            fraud_type=fraud_type,
            severity=severity,
            description=description,
            evidence_data=evidence_data or {},
            is_resolved=False
        )
        
        db.add(fraud_log)
        db.commit()
        db.refresh(fraud_log)
        
        logger.warning(f"Fraud logged: student={student_id}, type={fraud_type}, severity={severity}")
        return fraud_log
    
    @staticmethod
    def get_unresolved_fraud_logs(
        db: Session,
        severity_filter: Optional[str] = None
    ):
        """Get unresolved fraud logs"""
        query = db.query(FraudLog).filter(FraudLog.is_resolved == False)
        
        if severity_filter:
            query = query.filter(FraudLog.severity == severity_filter)
        
        return query.order_by(FraudLog.created_at.desc()).all()
    
    @staticmethod
    def resolve_fraud_log(
        db: Session,
        fraud_log_id: str,
        resolution_notes: str
    ) -> FraudLog:
        """Resolve fraud log"""
        fraud_log = db.query(FraudLog).filter(FraudLog.id == fraud_log_id).first()
        
        if not fraud_log:
            raise ValueError("Fraud log not found")
        
        fraud_log.is_resolved = True
        fraud_log.resolved_at = datetime.utcnow()
        fraud_log.resolution_notes = resolution_notes
        db.commit()
        db.refresh(fraud_log)
        
        logger.info(f"Fraud log resolved: {fraud_log_id}")
        return fraud_log
    
    @staticmethod
    def get_student_fraud_stats(
        db: Session,
        student_id: str
    ) -> dict:
        """Get fraud statistics for student"""
        logs = db.query(FraudLog).filter(FraudLog.student_id == student_id).all()
        
        fraud_by_type = {}
        fraud_by_severity = {}
        
        for log in logs:
            fraud_by_type[log.fraud_type] = fraud_by_type.get(log.fraud_type, 0) + 1
            fraud_by_severity[log.severity] = fraud_by_severity.get(log.severity, 0) + 1
        
        return {
            "total_attempts": len(logs),
            "by_type": fraud_by_type,
            "by_severity": fraud_by_severity,
            "unresolved": sum(1 for log in logs if not log.is_resolved)
        }
