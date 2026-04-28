"""
Image processing utilities for the AI module
"""
import cv2
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def decode_base64_image(image_base64: str) -> Optional[np.ndarray]:
    """
    Decode base64 encoded image to numpy array
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        RGB numpy array or None if decoding fails
    """
    try:
        # Remove data URI prefix if present
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # Decode base64
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Convert to numpy array
        image_array = np.array(image)
        
        return image_array
    except Exception as e:
        logger.error(f"Error decoding base64 image: {str(e)}")
        return None


def encode_image_to_base64(image_array: np.ndarray) -> Optional[str]:
    """
    Encode numpy array to base64 string
    
    Args:
        image_array: RGB numpy array
        
    Returns:
        Base64 encoded image string
    """
    try:
        # Convert numpy array to Image
        image = Image.fromarray(image_array.astype("uint8"))
        
        # Save to bytes
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        
        # Encode to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return image_base64
    except Exception as e:
        logger.error(f"Error encoding image to base64: {str(e)}")
        return None


def resize_image(
    image_array: np.ndarray,
    target_width: int = 640,
    target_height: int = 480
) -> np.ndarray:
    """
    Resize image to target dimensions
    
    Args:
        image_array: RGB numpy array
        target_width: Target width
        target_height: Target height
        
    Returns:
        Resized image array
    """
    try:
        return cv2.resize(image_array, (target_width, target_height))
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        return image_array


def crop_face_region(
    image_array: np.ndarray,
    face_location: Tuple[int, int, int, int],
    padding: float = 0.1
) -> Optional[np.ndarray]:
    """
    Crop face region from image with padding
    
    Args:
        image_array: RGB numpy array
        face_location: (top, right, bottom, left)
        padding: Padding as percentage of face size
        
    Returns:
        Cropped face region
    """
    try:
        height, width = image_array.shape[:2]
        top, right, bottom, left = face_location
        
        face_height = bottom - top
        face_width = right - left
        
        # Add padding
        pad_h = int(face_height * padding)
        pad_w = int(face_width * padding)
        
        top = max(0, top - pad_h)
        left = max(0, left - pad_w)
        bottom = min(height, bottom + pad_h)
        right = min(width, right + pad_w)
        
        cropped = image_array[top:bottom, left:right]
        return cropped
    except Exception as e:
        logger.error(f"Error cropping face region: {str(e)}")
        return None


def normalize_image(image_array: np.ndarray) -> np.ndarray:
    """
    Normalize image values to [0, 1]
    
    Args:
        image_array: Image array
        
    Returns:
        Normalized image
    """
    return image_array.astype(np.float32) / 255.0


def standardize_image_format(image_array: np.ndarray) -> np.ndarray:
    """
    Standardize image to RGB format
    
    Args:
        image_array: Image array (may be BGR or RGB)
        
    Returns:
        RGB image array
    """
    # Assume input is BGR (OpenCV default)
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        # Convert BGR to RGB
        return cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    
    return image_array


def apply_histogram_equalization(image_array: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization to improve image contrast
    
    Args:
        image_array: RGB image array
        
    Returns:
        Enhanced image array
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
        
        return enhanced
    except Exception as e:
        logger.error(f"Error applying histogram equalization: {str(e)}")
        return image_array


def apply_face_detection_preprocessing(image_array: np.ndarray) -> np.ndarray:
    """
    Apply preprocessing for better face detection
    
    Args:
        image_array: RGB image array
        
    Returns:
        Preprocessed image array
    """
    # Resize if too large
    height, width = image_array.shape[:2]
    if max(height, width) > 1280:
        scale = 1280 / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image_array = resize_image(image_array, new_width, new_height)
    
    # Apply histogram equalization
    image_array = apply_histogram_equalization(image_array)
    
    return image_array


def serialize_embedding(embedding: np.ndarray) -> list:
    """
    Serialize numpy array embedding to list
    
    Args:
        embedding: Numpy array
        
    Returns:
        Serialized list
    """
    return embedding.tolist() if isinstance(embedding, np.ndarray) else embedding


def deserialize_embedding(embedding_data: list) -> np.ndarray:
    """
    Deserialize list embedding to numpy array
    
    Args:
        embedding_data: Serialized embedding list
        
    Returns:
        Numpy array
    """
    return np.array(embedding_data, dtype=np.float64)
