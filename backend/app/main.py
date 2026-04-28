"""
Main FastAPI Application - FaceGuard Attendance System
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import Base, engine, init_db, close_db
from app.routers import (
    auth_router,
    face_router,
    attendance_router,
    admin_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Closing database...")
    await close_db()
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Smart Attendance Management System with Face Recognition and Anti-Spoofing",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)


# Include routers
app.include_router(
    auth_router,
    prefix=settings.API_V1_STR,
    tags=["authentication"]
)
app.include_router(
    face_router,
    prefix=settings.API_V1_STR,
    tags=["face-recognition"]
)
app.include_router(
    attendance_router,
    prefix=settings.API_V1_STR,
    tags=["attendance"]
)
app.include_router(
    admin_router,
    prefix=settings.API_V1_STR,
    tags=["admin"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "api_docs": "/docs",
        "api_version": settings.API_V1_STR
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_VERSION
    }


@app.get(f"{settings.API_V1_STR}/info")
async def get_api_info():
    """Get API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "face": f"{settings.API_V1_STR}/face",
            "attendance": f"{settings.API_V1_STR}/attendance",
            "admin": f"{settings.API_V1_STR}/admin"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
