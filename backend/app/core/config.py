"""
Production-grade configuration management for FaceGuard Attendance System
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Main application settings"""
    
    # Project Info
    PROJECT_NAME: str = "FaceGuard Attendance System"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "*"]
    
    # Database
    DATABASE_URL: str = "postgresql://faceguard:faceguard@localhost:5432/faceguard_attendance"
    SQLALCHEMY_ECHO: bool = False
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-with-32-chars-minimum"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Face Recognition
    FACE_RECOGNITION_MODEL: str = "hog"  # "hog" or "cnn"
    FACE_DISTANCE_THRESHOLD: float = 0.6
    MIN_FACE_DETECTION_CONFIDENCE: float = 0.5
    
    # Anti-Spoof Settings
    LIVENESS_THRESHOLD: float = 0.7
    BLINK_THRESHOLD: float = 0.25
    HEAD_POSE_THRESHOLD: float = 20.0
    SMILE_THRESHOLD: float = 0.5
    
    # Geofencing
    DEFAULT_GEOFENCE_RADIUS_METERS: float = 100.0
    
    # Fraud Prevention
    MAX_DUPLICATE_ATTENDANCE_ATTEMPTS: int = 5
    FRAUD_LOG_RETENTION_DAYS: int = 90
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_IMAGE_FORMATS: list = ["jpg", "jpeg", "png", "gif"]
    ENROLLMENT_IMAGES_REQUIRED: int = 15
    
    # Email
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SENDER_EMAIL: Optional[str] = None
    SENDER_NAME: str = "FaceGuard Attendance"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
