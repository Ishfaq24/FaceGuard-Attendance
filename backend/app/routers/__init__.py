"""Routers module initialization"""
from .auth import router as auth_router
from .face import router as face_router
from .attendance import router as attendance_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "face_router",
    "attendance_router",
    "admin_router",
]
