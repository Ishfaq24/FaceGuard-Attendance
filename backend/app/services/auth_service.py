"""
Authentication and User Services
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import User, Student, Teacher, Admin, UserRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.schemas import SignupRequest, LoginRequest
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def signup(db: Session, request: SignupRequest) -> Tuple[User, str, str]:
        """
        Register new user
        
        Args:
            db: Database session
            request: Signup request
            
        Returns:
            Tuple of (user, access_token, refresh_token)
        """
        # Check if email exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise ValueError(f"Email {request.email} already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=request.email,
            full_name=request.full_name,
            password_hash=hash_password(request.password),
            role=request.role,
            phone_number=request.phone_number,
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        
        # Create role-specific profile
        if request.role == UserRole.STUDENT:
            # Student signup should include roll_number and department
            student = Student(
                id=str(uuid.uuid4()),
                user_id=user_id,
                roll_number="",  # To be filled later
                department_id="",  # To be filled later
                class_id=""  # To be filled later
            )
            db.add(student)
        elif request.role == UserRole.TEACHER:
            teacher = Teacher(
                id=str(uuid.uuid4()),
                user_id=user_id,
                employee_id=f"EMP_{user_id[:8]}",
                department_id=""
            )
            db.add(teacher)
        elif request.role == UserRole.ADMIN:
            admin = Admin(
                id=str(uuid.uuid4()),
                user_id=user_id,
                employee_id=f"ADM_{user_id[:8]}"
            )
            db.add(admin)
        
        db.commit()
        db.refresh(user)
        
        # Generate tokens
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        })
        refresh_token = create_refresh_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        })
        
        logger.info(f"New user registered: {user.email} ({user.role})")
        return user, access_token, refresh_token
    
    @staticmethod
    def login(db: Session, request: LoginRequest) -> Tuple[User, str, str]:
        """
        Authenticate user
        
        Args:
            db: Database session
            request: Login request
            
        Returns:
            Tuple of (user, access_token, refresh_token)
        """
        # Find user
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise ValueError(f"User not found")
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise ValueError("Invalid password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate tokens
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        })
        refresh_token = create_refresh_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        })
        
        logger.info(f"User logged in: {user.email}")
        return user, access_token, refresh_token
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def verify_email(db: Session, user_id: str) -> User:
        """Mark email as verified"""
        user = AuthService.get_user_by_id(db, user_id)
        if user:
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            logger.info(f"Email verified for user: {user.email}")
        return user
    
    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> User:
        """Change user password"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Incorrect password")
        
        user.password_hash = hash_password(new_password)
        db.commit()
        db.refresh(user)
        logger.info(f"Password changed for user: {user.email}")
        return user


class UserService:
    """User management service"""
    
    @staticmethod
    def get_user_profile(db: Session, user_id: str):
        """Get complete user profile with role-specific data"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        profile = {
            "user": user,
            "student": None,
            "teacher": None,
            "admin": None
        }
        
        if user.role == UserRole.STUDENT:
            profile["student"] = user.student_profile
        elif user.role == UserRole.TEACHER:
            profile["teacher"] = user.teacher_profile
        elif user.role == UserRole.ADMIN:
            profile["admin"] = user.admin_profile
        
        return profile
    
    @staticmethod
    def update_user(db: Session, user_id: str, **kwargs) -> User:
        """Update user information"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        allowed_fields = ["full_name", "phone_number", "profile_picture_url"]
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        logger.info(f"User updated: {user.email}")
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> User:
        """Deactivate user account"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        db.commit()
        db.refresh(user)
        logger.info(f"User deactivated: {user.email}")
        return user
    
    @staticmethod
    def activate_user(db: Session, user_id: str) -> User:
        """Activate user account"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_active = True
        db.commit()
        db.refresh(user)
        logger.info(f"User activated: {user.email}")
        return user
