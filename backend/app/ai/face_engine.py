"""
Face Detection and Recognition Engine
"""
import cv2
import numpy as np
import face_recognition
from typing import List, Tuple, Optional
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class FaceEngine:
    """Face detection and recognition engine"""
    
    def __init__(self):
        """Initialize face recognition engine"""
        self.model = settings.FACE_RECOGNITION_MODEL  # "hog" or "cnn"
        self.distance_threshold = settings.FACE_DISTANCE_THRESHOLD
        self.min_confidence = settings.MIN_FACE_DETECTION_CONFIDENCE
    
    def extract_face_encodings(
        self,
        image_data: np.ndarray,
        num_jitters: int = 1
    ) -> List[np.ndarray]:
        """
        Extract face encodings from image
        
        Args:
            image_data: RGB image array
            num_jitters: Number of times to jitter face detection
            
        Returns:
            List of face encodings (128-dimensional vectors)
        """
        try:
            # Find faces in image
            face_locations = face_recognition.face_locations(
                image_data,
                model=self.model
            )
            
            if not face_locations:
                logger.warning("No faces detected in image")
                return []
            
            # Encode faces
            encodings = face_recognition.face_encodings(
                image_data,
                face_locations,
                num_jitters=num_jitters
            )
            
            return encodings
        except Exception as e:
            logger.error(f"Error extracting face encodings: {str(e)}")
            raise
    
    def detect_faces(
        self,
        image_data: np.ndarray,
        return_confidence: bool = False
    ) -> Tuple[List[Tuple[int, int, int, int]], Optional[List[float]]]:
        """
        Detect face locations in image
        
        Args:
            image_data: RGB image array
            return_confidence: Whether to return confidence scores
            
        Returns:
            List of face locations (top, right, bottom, left) and optional confidence scores
        """
        try:
            face_locations = face_recognition.face_locations(
                image_data,
                model=self.model
            )
            
            if not face_locations:
                return [], None if return_confidence else []
            
            if return_confidence:
                # Generate dummy confidence scores
                confidences = [0.99] * len(face_locations)
                return face_locations, confidences
            
            return face_locations, None
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            raise
    
    def verify_face_match(
        self,
        face_encoding: np.ndarray,
        known_encodings: List[np.ndarray]
    ) -> Tuple[bool, float]:
        """
        Verify if face matches any known encodings
        
        Args:
            face_encoding: Face encoding to verify
            known_encodings: List of known face encodings
            
        Returns:
            Tuple of (match_found, confidence_score)
        """
        if not known_encodings or len(known_encodings) == 0:
            return False, 0.0
        
        # Compute face distances
        face_distances = face_recognition.face_distance(
            known_encodings,
            face_encoding
        )
        
        # Find best match
        best_distance = np.min(face_distances)
        best_match_index = np.argmin(face_distances)
        
        # Check if best match is within threshold
        match_found = best_distance <= self.distance_threshold
        confidence = 1.0 - best_distance
        
        return match_found, confidence
    
    def compare_faces(
        self,
        face_encoding: np.ndarray,
        known_encodings: List[np.ndarray]
    ) -> List[bool]:
        """
        Compare face against multiple known faces
        
        Args:
            face_encoding: Face encoding to compare
            known_encodings: List of known face encodings
            
        Returns:
            List of boolean matches
        """
        return face_recognition.compare_faces(
            known_encodings,
            face_encoding,
            tolerance=self.distance_threshold
        )
    
    def get_face_distance(
        self,
        face_encoding: np.ndarray,
        known_encodings: List[np.ndarray]
    ) -> List[float]:
        """
        Get distances between face and known encodings
        
        Args:
            face_encoding: Face encoding
            known_encodings: List of known face encodings
            
        Returns:
            List of distances
        """
        if not known_encodings:
            return []
        
        return face_recognition.face_distance(
            known_encodings,
            face_encoding
        ).tolist()


class FaceValidator:
    """Face image quality and validity validator"""
    
    def __init__(self):
        """Initialize face validator"""
        self.face_engine = FaceEngine()
    
    def validate_image_quality(
        self,
        image_data: np.ndarray
    ) -> Tuple[bool, str, float]:
        """
        Validate face image quality
        
        Args:
            image_data: RGB image array
            
        Returns:
            Tuple of (is_valid, reason, quality_score)
        """
        # Check image dimensions
        if image_data.size == 0:
            return False, "Empty image", 0.0
        
        if len(image_data.shape) != 3:
            return False, "Invalid image format", 0.0
        
        # Check for blur
        gray = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:
            return False, "Image too blurry", laplacian_var / 1000.0
        
        # Check lighting
        mean_brightness = np.mean(gray)
        if mean_brightness < 30 or mean_brightness > 225:
            return False, "Poor lighting conditions", mean_brightness / 255.0
        
        quality_score = min(100.0, (laplacian_var / 100.0) * 100.0)
        return True, "Image quality acceptable", quality_score
    
    def validate_single_face(
        self,
        image_data: np.ndarray
    ) -> Tuple[bool, str, int]:
        """
        Validate that exactly one face is present
        
        Args:
            image_data: RGB image array
            
        Returns:
            Tuple of (has_single_face, reason, face_count)
        """
        try:
            face_locations, _ = self.face_engine.detect_faces(image_data)
            face_count = len(face_locations)
            
            if face_count == 0:
                return False, "No face detected", 0
            elif face_count > 1:
                return False, f"Multiple faces detected ({face_count})", face_count
            else:
                return True, "Single face detected", 1
        except Exception as e:
            logger.error(f"Error validating single face: {str(e)}")
            return False, str(e), 0
    
    def validate_face_position(
        self,
        image_data: np.ndarray
    ) -> Tuple[bool, str]:
        """
        Validate face position and framing
        
        Args:
            image_data: RGB image array
            
        Returns:
            Tuple of (is_valid_position, reason)
        """
        try:
            height, width = image_data.shape[:2]
            face_locations, _ = self.face_engine.detect_faces(image_data)
            
            if not face_locations:
                return False, "No face detected"
            
            top, right, bottom, left = face_locations[0]
            face_height = bottom - top
            face_width = right - left
            
            # Face should cover 30-80% of image height
            face_height_ratio = face_height / height
            if face_height_ratio < 0.3:
                return False, "Face too small in frame"
            if face_height_ratio > 0.8:
                return False, "Face too large in frame"
            
            # Face should be centered
            face_center_x = (left + right) / 2
            face_center_y = (top + bottom) / 2
            
            image_center_x = width / 2
            image_center_y = height / 2
            
            center_offset = np.sqrt(
                ((face_center_x - image_center_x) ** 2) +
                ((face_center_y - image_center_y) ** 2)
            )
            
            if center_offset > max(width, height) * 0.2:
                return False, "Face not properly centered"
            
            return True, "Face position valid"
        except Exception as e:
            logger.error(f"Error validating face position: {str(e)}")
            return False, str(e)
    
    def validate_duplicate_faces(
        self,
        new_embedding: np.ndarray,
        existing_embeddings: List[np.ndarray]
    ) -> Tuple[bool, str, float]:
        """
        Check if face is already enrolled (duplicate detection)
        
        Args:
            new_embedding: New face embedding
            existing_embeddings: List of existing enrollments
            
        Returns:
            Tuple of (is_duplicate, reason, best_match_confidence)
        """
        if not existing_embeddings:
            return False, "No existing embeddings to compare", 0.0
        
        is_match, confidence = self.face_engine.verify_face_match(
            new_embedding,
            existing_embeddings
        )
        
        if is_match:
            return True, "Face already enrolled", confidence
        
        return False, "Unique face detected", confidence
