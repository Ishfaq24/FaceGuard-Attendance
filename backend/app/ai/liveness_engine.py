"""
Liveness Detection and Anti-Spoof Engine
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class LivenessDetector:
    """Detects liveness features like blinks, head movement, and smiles"""
    
    def __init__(self):
        """Initialize liveness detector"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=settings.MIN_FACE_DETECTION_CONFIDENCE
        )
        
        self.blink_threshold = settings.BLINK_THRESHOLD
        self.head_pose_threshold = settings.HEAD_POSE_THRESHOLD
    
    def calculate_eye_aspect_ratio(
        self,
        eye_landmarks: np.ndarray
    ) -> float:
        """
        Calculate Eye Aspect Ratio (EAR) for blink detection
        
        Args:
            eye_landmarks: Landmarks for one eye (6 points)
            
        Returns:
            Eye Aspect Ratio value
        """
        # Compute distances between eye landmarks
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # Compute EAR
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(
        self,
        frame: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Detect eye blinks
        
        Args:
            frame: RGB frame
            
        Returns:
            Tuple of (blink_detected, confidence)
        """
        try:
            results = self.face_mesh.process(frame)
            
            if not results.multi_face_landmarks:
                return False, 0.0
            
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = np.array([
                (lm.x, lm.y, lm.z) for lm in face_landmarks.landmark
            ])
            
            # Eye landmark indices
            left_eye = landmarks[[33, 160, 158, 133, 153, 144]]
            right_eye = landmarks[[362, 385, 387, 362, 373, 380]]
            
            left_ear = self.calculate_eye_aspect_ratio(left_eye)
            right_ear = self.calculate_eye_aspect_ratio(right_eye)
            
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Blink occurs when EAR drops below threshold
            blink_detected = avg_ear < self.blink_threshold
            confidence = max(0.0, (self.blink_threshold - avg_ear) / self.blink_threshold)
            
            return blink_detected, confidence
        except Exception as e:
            logger.error(f"Error detecting blink: {str(e)}")
            return False, 0.0
    
    def detect_head_movement(
        self,
        frame: np.ndarray
    ) -> Tuple[str, float]:
        """
        Detect head pose (looking left, right, up, down)
        
        Args:
            frame: RGB frame
            
        Returns:
            Tuple of (head_pose, confidence)
        """
        try:
            results = self.face_mesh.process(frame)
            
            if not results.multi_face_landmarks:
                return "neutral", 0.0
            
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = np.array([
                (lm.x, lm.y) for lm in face_landmarks.landmark
            ])
            
            # Key facial points for pose estimation
            nose = landmarks[1]
            left_eye = landmarks[133]
            right_eye = landmarks[362]
            left_mouth = landmarks[287]
            right_mouth = landmarks[57]
            
            # Calculate head angles
            eye_center = (left_eye + right_eye) / 2
            mouth_center = (left_mouth + right_mouth) / 2
            
            # Horizontal angle (left/right)
            horizontal_angle = np.arctan2(
                left_eye[1] - right_eye[1],
                left_eye[0] - right_eye[0]
            ) * (180 / np.pi)
            
            # Vertical angle (up/down)
            vertical_angle = np.arctan2(
                nose[1] - mouth_center[1],
                nose[0] - mouth_center[0]
            ) * (180 / np.pi)
            
            # Determine head pose
            pose = "neutral"
            confidence = 1.0
            
            if horizontal_angle > self.head_pose_threshold:
                pose = "left"
                confidence = min(1.0, abs(horizontal_angle) / 45.0)
            elif horizontal_angle < -self.head_pose_threshold:
                pose = "right"
                confidence = min(1.0, abs(horizontal_angle) / 45.0)
            elif vertical_angle > self.head_pose_threshold:
                pose = "up"
                confidence = min(1.0, abs(vertical_angle) / 45.0)
            elif vertical_angle < -self.head_pose_threshold:
                pose = "down"
                confidence = min(1.0, abs(vertical_angle) / 45.0)
            
            return pose, confidence
        except Exception as e:
            logger.error(f"Error detecting head movement: {str(e)}")
            return "neutral", 0.0
    
    def detect_smile(
        self,
        frame: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Detect smile expression
        
        Args:
            frame: RGB frame
            
        Returns:
            Tuple of (smile_detected, confidence)
        """
        try:
            results = self.face_mesh.process(frame)
            
            if not results.multi_face_landmarks:
                return False, 0.0
            
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = np.array([
                (lm.x, lm.y) for lm in face_landmarks.landmark
            ])
            
            # Mouth landmarks
            left_mouth = landmarks[61]
            right_mouth = landmarks[291]
            top_mouth = landmarks[13]
            bottom_mouth = landmarks[14]
            
            # Calculate mouth height (vertical distance)
            mouth_height = abs(bottom_mouth[1] - top_mouth[1])
            # Calculate mouth width
            mouth_width = abs(right_mouth[0] - left_mouth[0])
            
            # Smile ratio (higher = more smile)
            smile_ratio = mouth_height / mouth_width if mouth_width > 0 else 0
            
            # Threshold for smile detection
            smile_threshold = settings.SMILE_THRESHOLD
            smile_detected = smile_ratio > smile_threshold
            confidence = min(1.0, smile_ratio / (smile_threshold * 1.5))
            
            return smile_detected, confidence
        except Exception as e:
            logger.error(f"Error detecting smile: {str(e)}")
            return False, 0.0


class AntiSpoofDetector:
    """Anti-spoofing detection using texture analysis"""
    
    def __init__(self):
        """Initialize anti-spoof detector"""
        self.liveness_threshold = settings.LIVENESS_THRESHOLD
    
    def detect_texture_differences(
        self,
        frame: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Detect texture differences between real face and spoofing attacks
        
        Args:
            frame: RGB frame
            
        Returns:
            Tuple of (is_real_face, confidence)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Compute local binary pattern variations
            # More natural skin has different texture than printed photos
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Real face typically has higher texture variance
            # Printed photos or phone screens have lower variance
            is_real = laplacian_var > 100
            confidence = min(1.0, laplacian_var / 500.0)
            
            return is_real, confidence
        except Exception as e:
            logger.error(f"Error in texture analysis: {str(e)}")
            return False, 0.0
    
    def detect_frequency_analysis(
        self,
        frame: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Detect spoof using frequency domain analysis
        
        Args:
            frame: RGB frame
            
        Returns:
            Tuple of (is_real_face, confidence)
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Compute FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Real faces have more balanced frequency distribution
            # Spoofed faces (photos) have peaks at specific frequencies
            spectrum_mean = np.mean(magnitude_spectrum)
            spectrum_std = np.std(magnitude_spectrum)
            
            # Calculate spoof score
            spoof_score = spectrum_std / (spectrum_mean + 1e-10)
            
            is_real = spoof_score > 0.5
            confidence = min(1.0, spoof_score / 2.0)
            
            return is_real, confidence
        except Exception as e:
            logger.error(f"Error in frequency analysis: {str(e)}")
            return False, 0.0
    
    def detect_motion_patterns(
        self,
        frame: np.ndarray,
        previous_frame: Optional[np.ndarray] = None
    ) -> Tuple[bool, float]:
        """
        Detect natural motion patterns
        
        Args:
            frame: Current RGB frame
            previous_frame: Previous RGB frame for comparison
            
        Returns:
            Tuple of (has_natural_motion, confidence)
        """
        try:
            if previous_frame is None:
                return True, 0.5
            
            # Convert to grayscale
            gray_current = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            gray_prev = cv2.cvtColor(previous_frame, cv2.COLOR_RGB2GRAY)
            
            # Compute optical flow
            flow = cv2.calcOpticalFlowFarneback(
                gray_prev, gray_current, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Analyze flow magnitude
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            motion_magnitude = np.mean(magnitude)
            motion_std = np.std(magnitude)
            
            # Natural motion has good distribution
            has_natural_motion = motion_std > 0.5
            confidence = min(1.0, motion_std / 2.0)
            
            return has_natural_motion, confidence
        except Exception as e:
            logger.error(f"Error in motion analysis: {str(e)}")
            return True, 0.0
    
    def compute_liveness_score(
        self,
        frame: np.ndarray,
        previous_frame: Optional[np.ndarray] = None,
        blink_detected: bool = False,
        head_pose: str = "neutral",
        smile_detected: bool = False
    ) -> Tuple[float, bool, str]:
        """
        Compute overall liveness score
        
        Args:
            frame: RGB frame
            previous_frame: Previous frame for motion analysis
            blink_detected: Whether blink was detected
            head_pose: Head pose information
            smile_detected: Whether smile was detected
            
        Returns:
            Tuple of (liveness_score, is_live, message)
        """
        score = 0.0
        reasons = []
        
        # Texture analysis
        is_real_texture, texture_conf = self.detect_texture_differences(frame)
        if is_real_texture:
            score += texture_conf * 0.3
            reasons.append("Natural skin texture detected")
        else:
            reasons.append("Suspicious texture pattern")
        
        # Frequency analysis
        is_real_freq, freq_conf = self.detect_frequency_analysis(frame)
        if is_real_freq:
            score += freq_conf * 0.2
            reasons.append("Natural frequency distribution")
        else:
            reasons.append("Suspicious frequency pattern")
        
        # Motion analysis
        is_natural_motion, motion_conf = self.detect_motion_patterns(frame, previous_frame)
        if is_natural_motion:
            score += motion_conf * 0.2
            reasons.append("Natural motion patterns detected")
        
        # Behavioral cues
        if blink_detected:
            score += 0.15
            reasons.append("Blink detected")
        
        if head_pose != "neutral":
            score += 0.1
            reasons.append(f"Natural head movement detected ({head_pose})")
        
        if smile_detected:
            score += 0.05
            reasons.append("Smile detected")
        
        is_live = score >= self.liveness_threshold
        message = " | ".join(reasons)
        
        return score, is_live, message
