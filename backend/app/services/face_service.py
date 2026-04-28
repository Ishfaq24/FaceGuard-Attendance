"""
Face Recognition and Enrollment Services
"""
import uuid
import numpy as np
import logging
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import Student, FaceEmbedding
from app.ai import (
    FaceEngine,
    FaceValidator,
    decode_base64_image,
    apply_face_detection_preprocessing,
    serialize_embedding,
    deserialize_embedding
)

logger = logging.getLogger(__name__)


class FaceEnrollmentService:
    """Face enrollment and biometric registration service"""
    
    def __init__(self):
        """Initialize face enrollment service"""
        self.face_engine = FaceEngine()
        self.face_validator = FaceValidator()
    
    def validate_enrollment_image(
        self,
        image_base64: str
    ) -> Tuple[bool, str, Optional[np.ndarray], float]:
        """
        Validate image for enrollment
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Tuple of (is_valid, reason, image_array, quality_score)
        """
        # Decode image
        image_array = decode_base64_image(image_base64)
        if image_array is None:
            return False, "Failed to decode image", None, 0.0
        
        # Preprocess image
        image_array = apply_face_detection_preprocessing(image_array)
        
        # Validate quality
        is_valid, reason, quality_score = self.face_validator.validate_image_quality(image_array)
        if not is_valid:
            return False, f"Quality check failed: {reason}", None, quality_score
        
        # Validate single face
        is_single, reason, count = self.face_validator.validate_single_face(image_array)
        if not is_single:
            return False, f"Face validation failed: {reason}", None, quality_score
        
        # Validate face position
        is_centered, reason = self.face_validator.validate_face_position(image_array)
        if not is_centered:
            return False, f"Position validation failed: {reason}", None, quality_score
        
        return True, "Image validation passed", image_array, quality_score
    
    def extract_and_store_embedding(
        self,
        db: Session,
        student_id: str,
        image_array: np.ndarray,
        quality_score: float,
        image_url: Optional[str] = None
    ) -> FaceEmbedding:
        """
        Extract face embedding and store in database
        
        Args:
            db: Database session
            student_id: Student ID
            image_array: RGB image array
            quality_score: Image quality score
            image_url: Optional URL to original image
            
        Returns:
            Created FaceEmbedding record
        """
        # Extract encodings
        encodings = self.face_engine.extract_face_encodings(image_array)
        if not encodings:
            raise ValueError("Failed to extract face encoding")
        
        # Use first encoding
        embedding = encodings[0]
        
        # Create embedding record
        face_embedding = FaceEmbedding(
            id=str(uuid.uuid4()),
            student_id=student_id,
            embedding=serialize_embedding(embedding),
            image_url=image_url,
            quality_score=quality_score,
            is_primary=False  # Will be set after enrollment completion
        )
        
        db.add(face_embedding)
        db.commit()
        db.refresh(face_embedding)
        
        logger.info(f"Face embedding stored for student {student_id}")
        return face_embedding
    
    def complete_enrollment(
        self,
        db: Session,
        student_id: str
    ) -> Student:
        """
        Complete face enrollment process
        
        Args:
            db: Database session
            student_id: Student ID
            
        Returns:
            Updated student record
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("Student not found")
        
        # Get face embeddings
        embeddings = db.query(FaceEmbedding).filter(
            FaceEmbedding.student_id == student_id
        ).all()
        
        if len(embeddings) < 10:
            raise ValueError(f"Minimum 10 face images required, got {len(embeddings)}")
        
        # Set best embedding as primary (highest quality)
        best_embedding = max(embeddings, key=lambda x: x.quality_score)
        for embedding in embeddings:
            embedding.is_primary = (embedding.id == best_embedding.id)
        
        # Mark student as enrolled
        student.face_enrolled = True
        student.face_enrollment_date = __import__('datetime').datetime.utcnow()
        student.biometric_status = "enrolled"
        
        db.commit()
        db.refresh(student)
        
        logger.info(f"Face enrollment completed for student {student_id}")
        return student
    
    def check_duplicate_enrollment(
        self,
        db: Session,
        new_embedding: np.ndarray,
        exclude_student_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if face is already enrolled by another student
        
        Args:
            db: Database session
            new_embedding: New face embedding
            exclude_student_id: Student ID to exclude from check
            
        Returns:
            Tuple of (is_duplicate, matched_student_id)
        """
        # Get all primary embeddings
        query = db.query(FaceEmbedding).filter(FaceEmbedding.is_primary == True)
        
        if exclude_student_id:
            query = query.filter(FaceEmbedding.student_id != exclude_student_id)
        
        existing_embeddings = query.all()
        
        # Check for matches
        existing_embedding_arrays = [
            deserialize_embedding(e.embedding) for e in existing_embeddings
        ]
        
        is_duplicate, confidence, matched_student_id = self.face_engine.verify_face_match(
            new_embedding,
            existing_embedding_arrays
        )
        
        if is_duplicate:
            # Get matched student
            for i, embedding in enumerate(existing_embeddings):
                if i == np.argmin(
                    [
                        np.linalg.norm(new_embedding - deserialize_embedding(e.embedding))
                        for e in existing_embeddings
                    ]
                ):
                    return True, embedding.student_id
        
        return False, None


class FaceVerificationService:
    """Face recognition and verification service for attendance"""
    
    def __init__(self):
        """Initialize face verification service"""
        self.face_engine = FaceEngine()
        self.face_validator = FaceValidator()
    
    def verify_student_face(
        self,
        db: Session,
        student_id: str,
        image_base64: str
    ) -> Tuple[bool, float, str]:
        """
        Verify student face against enrollment
        
        Args:
            db: Database session
            student_id: Student ID
            image_base64: Base64 encoded image
            
        Returns:
            Tuple of (is_verified, confidence, message)
        """
        # Decode and validate image
        image_array = decode_base64_image(image_base64)
        if image_array is None:
            return False, 0.0, "Failed to decode image"
        
        image_array = apply_face_detection_preprocessing(image_array)
        
        # Extract face encoding
        encodings = self.face_engine.extract_face_encodings(image_array)
        if not encodings:
            return False, 0.0, "No face detected in image"
        
        verification_encoding = encodings[0]
        
        # Get student's enrolled embeddings
        embeddings = db.query(FaceEmbedding).filter(
            FaceEmbedding.student_id == student_id
        ).all()
        
        if not embeddings:
            return False, 0.0, "Student has no enrolled face biometrics"
        
        # Convert to numpy arrays
        enrollment_arrays = [
            deserialize_embedding(e.embedding) for e in embeddings
        ]
        
        # Verify match
        is_verified, confidence = self.face_engine.verify_face_match(
            verification_encoding,
            enrollment_arrays
        )
        
        if is_verified:
            return True, confidence, f"Face verified successfully (confidence: {confidence:.2f})"
        else:
            return False, confidence, f"Face verification failed (confidence: {confidence:.2f})"
    
    def verify_face_with_threshold(
        self,
        db: Session,
        student_id: str,
        image_base64: str,
        min_confidence: float = 0.6
    ) -> Tuple[bool, float, str]:
        """
        Verify face with custom confidence threshold
        
        Args:
            db: Database session
            student_id: Student ID
            image_base64: Base64 encoded image
            min_confidence: Minimum confidence threshold
            
        Returns:
            Tuple of (is_verified, confidence, message)
        """
        is_verified, confidence, message = self.verify_student_face(
            db,
            student_id,
            image_base64
        )
        
        if is_verified and confidence >= min_confidence:
            return True, confidence, message
        
        return False, confidence, f"Face verification failed - confidence below threshold ({confidence:.2f} < {min_confidence})"
