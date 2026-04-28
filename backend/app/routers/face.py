"""
Face Recognition and Enrollment API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.schemas import FaceVerificationRequest, FaceVerificationResponse
from app.services import FaceEnrollmentService, FaceVerificationService, FraudDetectionService
from app.models import Student
from app.ai import decode_base64_image
import logging

router = APIRouter(prefix="/face", tags=["face-recognition"])
logger = logging.getLogger(__name__)
settings = get_settings()

face_enrollment_service = FaceEnrollmentService()
face_verification_service = FaceVerificationService()
fraud_service = FraudDetectionService()


@router.post("/enroll/start")
async def start_enrollment(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start face enrollment process"""
    # Verify user is student
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll faces"
        )
    
    # Get student profile
    user_id = current_user["user_id"]
    student = db.query(Student).filter(Student.user_id == user_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    if student.face_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Face already enrolled"
        )
    
    return {
        "enrollment_id": student.id,
        "status": "started",
        "images_required": settings.ENROLLMENT_IMAGES_REQUIRED,
        "message": "Start capturing face images"
    }


@router.post("/enroll/capture")
async def capture_enrollment_image(
    image_base64: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Capture face image during enrollment"""
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll faces"
        )
    
    user_id = current_user["user_id"]
    student = db.query(Student).filter(Student.user_id == user_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    try:
        # Validate image
        is_valid, reason, image_array, quality_score = face_enrollment_service.validate_enrollment_image(
            image_base64
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=reason
            )
        
        # Extract and store embedding
        embedding = face_enrollment_service.extract_and_store_embedding(
            db,
            student.id,
            image_array,
            quality_score
        )
        
        # Check enrollment progress
        embeddings_count = db.query(Student.__table__.c.id).filter(
            Student.id == student.id
        ).count()
        
        from app.models import FaceEmbedding
        embeddings_count = db.query(FaceEmbedding).filter(
            FaceEmbedding.student_id == student.id
        ).count()
        
        progress = {
            "images_captured": embeddings_count,
            "images_required": settings.ENROLLMENT_IMAGES_REQUIRED,
            "quality_score": quality_score,
            "enrollment_complete": embeddings_count >= settings.ENROLLMENT_IMAGES_REQUIRED
        }
        
        return {
            "status": "image_captured",
            "progress": progress,
            "message": f"Image {embeddings_count} captured successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during enrollment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image capture failed"
        )


@router.post("/enroll/complete")
async def complete_enrollment(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete face enrollment"""
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll faces"
        )
    
    user_id = current_user["user_id"]
    student = db.query(Student).filter(Student.user_id == user_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    try:
        updated_student = face_enrollment_service.complete_enrollment(db, student.id)
        
        return {
            "status": "enrollment_complete",
            "student_id": updated_student.id,
            "face_enrolled": updated_student.face_enrolled,
            "biometric_status": updated_student.biometric_status,
            "message": "Face enrollment completed successfully"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing enrollment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Enrollment completion failed"
        )


@router.post("/verify", response_model=FaceVerificationResponse)
async def verify_face(
    request: FaceVerificationRequest,
    student_id: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify student face
    
    Args:
        request: Face verification request
        student_id: Student ID (optional, defaults to current user)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Face verification response
    """
    # Determine student ID
    if not student_id:
        if current_user.get("role") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-students must provide student_id"
            )
        
        user_student = db.query(Student).filter(
            Student.user_id == current_user["user_id"]
        ).first()
        
        if not user_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        student_id = user_student.id
    
    try:
        is_verified, confidence, message = face_verification_service.verify_student_face(
            db,
            student_id,
            request.image_base64
        )
        
        return FaceVerificationResponse(
            verified=is_verified,
            confidence=confidence,
            student_id=student_id if is_verified else None,
            liveness_detected=False,
            liveness_score=0.0,
            spoof_detected=not is_verified,
            message=message
        )
    
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        
        # Log fraud attempt
        fraud_service.log_fraud_attempt(
            db,
            student_id,
            "face_mismatch",
            f"Face verification failed: {str(e)}",
            severity="low"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face verification failed"
        )


@router.get("/enrollment-status")
async def get_enrollment_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's face enrollment status"""
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students have enrollment status"
        )
    
    student = db.query(Student).filter(
        Student.user_id == current_user["user_id"]
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    from app.models import FaceEmbedding
    embeddings_count = db.query(FaceEmbedding).filter(
        FaceEmbedding.student_id == student.id
    ).count()
    
    return {
        "student_id": student.id,
        "face_enrolled": student.face_enrolled,
        "biometric_status": student.biometric_status,
        "face_enrollment_date": student.face_enrollment_date,
        "images_captured": embeddings_count,
        "images_required": settings.ENROLLMENT_IMAGES_REQUIRED,
        "enrollment_progress": min(100, (embeddings_count / settings.ENROLLMENT_IMAGES_REQUIRED) * 100)
    }
