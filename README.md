# FaceGuard Attendance - Smart Attendance Management with Face Recognition

A production-grade, enterprise-level full-stack web application for intelligent attendance management with face recognition, anti-spoofing, geofencing, and comprehensive fraud detection.

## 📋 Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Core Functionality
- **Face Recognition**: 128-D embedding-based biometric identification with 99%+ accuracy
- **Liveness Detection**: Multi-factor liveness verification (blink, head movement, smile)
- **Anti-Spoofing**: Texture, frequency, and motion-based spoof detection
- **Geofencing**: GPS-based location verification with configurable radius
- **Fraud Detection**: Multi-layer validation system with comprehensive logging
- **Role-Based Access**: Student, Teacher, and Admin roles with specific permissions

### Advanced Security
- JWT-based authentication with refresh tokens (30 min access, 7 day refresh)
- bcrypt password hashing (cost factor 12)
- Challenge-based liveness verification
- Duplicate detection to prevent unauthorized access
- Time window verification for attendance sessions
- Audit logging for all operations

### User Management
- User registration with role assignment
- Email verification system
- Password reset functionality
- User profile management
- Account activation/deactivation

### Analytics & Reporting
- Attendance statistics with period-based filtering
- Fraud metrics and incident tracking
- Department and class-level analytics
- Individual student attendance history
- Real-time session monitoring

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React 18.2)                    │
│  • Vite Build Tool  • Tailwind CSS  • Zustand State Mgmt     │
│  • Framer Motion    • React Router   • Axios HTTP Client     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Nginx Reverse Proxy                         │
│  • SSL/TLS Termination  • Load Balancing  • Caching         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI + Python)                  │
│  • RESTful Endpoints  • Dependency Injection  • Async I/O    │
│  • Error Handling     • Request Validation    • Logging      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬────────────────────┐
│   AI/ML Engine   │  Services Layer  │  Authentication    │
│  • Face Engine   │  • Attendance    │  • JWT/bcrypt      │
│  • Liveness      │  • Face Service  │  • RBAC            │
│  • Anti-Spoof    │  • Fraud Detect  │  • Sessions        │
│  • Challenges    │  • Admin Ops     │                    │
└──────────────────┴──────────────────┴────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           SQLAlchemy ORM + PostgreSQL (13 Tables)            │
│  • User, Student, Teacher, Admin  • Attendance Records      │
│  • Face Embeddings  • Fraud Logs  • Audit Trail             │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1 (async Python web framework)
- **Database**: PostgreSQL 16 with SQLAlchemy ORM
- **Authentication**: JWT (python-jose) + bcrypt
- **AI/ML**:
  - face_recognition (128-D embeddings)
  - MediaPipe Face Mesh (pose detection)
  - OpenCV (image processing)
  - NumPy/SciPy (numerical operations)
- **Validation**: Pydantic v2
- **Migration**: Alembic

### Frontend
- **UI Framework**: React 18.2.0
- **Build Tool**: Vite 4.5.0
- **Styling**: Tailwind CSS 3.3.0 + PostCSS
- **State Management**: Zustand 4.4.0
- **HTTP Client**: Axios 1.6.0 with interceptors
- **Routing**: React Router 6.18.0
- **Animations**: Framer Motion 10.16.4
- **Icons**: lucide-react 0.292.0
- **Notifications**: react-hot-toast 2.4.1
- **Charts**: Recharts 2.10.0

### DevOps
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx (Alpine)
- **CI/CD Ready**: GitHub Actions compatible

## 📦 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Node.js**: 18+ (for local frontend development)
- **Python**: 3.11+ (for local backend development)
- **PostgreSQL**: 16 (optional if using Docker)

### Required Ports
- `80`: Nginx HTTP
- `443`: Nginx HTTPS (when configured)
- `8000`: Backend API
- `3000`: Frontend
- `5432`: PostgreSQL

## 🚀 Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd FaceGuard-Attendance

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Build and start services
docker-compose up --build

# Initialize database
docker exec faceguard-backend python -m alembic upgrade head

# Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env with your values
# DATABASE_URL=postgresql://user:password@localhost:5432/faceguard_attendance
# ENVIRONMENT=development
# DEBUG=True

# Initialize database
alembic upgrade head

# Run development server
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev

# Access at http://localhost:5173
```

## ⚙️ Configuration

### Backend Configuration (backend/.env)

```env
# Database
DATABASE_URL=postgresql://faceguard:faceguard@localhost:5432/faceguard_attendance

# API
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Security
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=production
DEBUG=False

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Face Recognition
FACE_RECOGNITION_TOLERANCE=0.6  # Lower = stricter matching
MIN_CONFIDENCE_THRESHOLD=0.85
MIN_FACE_ENROLLMENT_IMAGES=15

# Liveness Detection
LIVENESS_DETECTION_ENABLED=True
MIN_LIVENESS_SCORE=0.75

# Geofencing
GEOFENCE_VERIFICATION_ENABLED=True

# Email (if needed for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration (frontend/.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=FaceGuard Attendance
VITE_ENVIRONMENT=development
```

## 🏃 Running the Application

### Using Docker Compose
```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Local Development
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Building Production Images
```bash
# Build images
docker-compose build

# Push to registry (optional)
docker tag faceguard-frontend:latest your-registry/faceguard-frontend:v1.0
docker push your-registry/faceguard-frontend:v1.0
```

## 📚 API Documentation

### Automatic Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Authentication Endpoints
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/change-password` - Change password

### Face Management Endpoints
- `POST /api/v1/face/enroll/start` - Start enrollment
- `POST /api/v1/face/enroll/capture` - Capture enrollment image
- `POST /api/v1/face/enroll/complete` - Complete enrollment
- `POST /api/v1/face/verify` - Verify face
- `GET /api/v1/face/enrollment-status` - Get enrollment status

### Attendance Endpoints
- `POST /api/v1/attendance/sessions` - Create session
- `POST /api/v1/attendance/mark` - Mark attendance
- `GET /api/v1/attendance/history` - Get history
- `GET /api/v1/attendance/sessions/{id}/records` - Get records

### Admin Endpoints
- `POST /api/v1/admin/departments` - Create department
- `POST /api/v1/admin/classes` - Create class
- `GET /api/v1/admin/analytics/attendance` - Attendance analytics
- `GET /api/v1/admin/analytics/fraud` - Fraud analytics

## 🗄️ Database Schema

### Core Tables
- **User**: Base authentication table (email, password_hash, role, is_verified)
- **Student**: Student profile (roll_number, department_id, class_id, face_enrolled)
- **Teacher**: Teacher profile (employee_id, department_id)
- **Admin**: Admin profile (employee_id, permissions JSON)

### Academic Tables
- **Department**: Departments (name, code, head_teacher_id)
- **Class**: Classes/Sections (name, code, semester, department_id, teacher_id)
- **Subject**: Subjects (name, code, class_id, credits)

### Biometric Tables
- **FaceEmbedding**: 128-D face vectors (student_id, embedding, quality_score, is_primary)
- **AttendanceSession**: Attendance session config (teacher_id, subject_id, status, timestamps)

### Tracking Tables
- **AttendanceRecord**: Individual attendance marks (session_id, student_id, status, face_confidence, liveness_score)
- **FraudLog**: Fraud attempts (student_id, fraud_type, severity, evidence, is_resolved)
- **GeofenceConfig**: Location boundaries (class_id, latitude, longitude, radius_meters)
- **AuditLog**: System audit trail (user_id, action, resource_type, timestamp)

## 🔒 Security Features

### Authentication & Authorization
- JWT tokens with short expiry (30 minutes access, 7 days refresh)
- bcrypt password hashing with cost factor 12
- Role-based access control (RBAC) on all endpoints
- Protected routes with automatic redirect for unauthorized access

### Face Recognition Security
- 128-D embedding verification (not image comparison)
- Duplicate face detection to prevent unauthorized access
- Liveness detection prevents spoofing attacks
- Multi-factor anti-spoof: texture, frequency, motion analysis

### Operational Security
- CORS middleware restricting origins
- TrustedHost middleware preventing header attacks
- Request validation with Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- Comprehensive error handling without data leakage
- Audit logging for compliance tracking

### Fraud Prevention
- Time window verification (5-minute buffer)
- Geofence validation with Haversine distance calculation
- Duplicate attendance detection per session
- Face mismatch detection with confidence thresholds
- Spoof attempt logging and escalation

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Verify connection string in .env
# Should be: postgresql://user:password@host:port/database
```

### Camera/Permissions Issues
```
Error: Camera permission denied
→ Grant camera permissions in browser
→ Check HTTPS is enabled (required for camera access in production)
```

### Face Recognition Not Working
```
Error: No face detected
→ Ensure good lighting
→ Keep face centered in frame
→ Check image quality (min 640x480)

Error: Face mismatch
→ Ensure proper enrollment with 15+ images
→ Check lighting conditions during verification
→ Increase FACE_RECOGNITION_TOLERANCE in .env
```

### Docker Build Failures
```bash
# Clean and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Port Already in Use
```bash
# Change port in docker-compose.yml
# Or kill existing process:
lsof -i :8000  # Find process
kill -9 <PID>
```

## 📈 Performance Optimization

### Backend
- Connection pooling with NullPool for production
- Async I/O for all database operations
- Image resizing/preprocessing before ML operations
- Caching of frequently accessed data

### Frontend
- Code splitting with lazy route loading
- Image optimization and lazy loading
- CSS-in-JS minification via Tailwind
- Gzip compression via Nginx

### Database
- Indexed columns: user_id, session_id, student_id
- Composite indexes on (session_id, student_id)
- Connection pooling
- Query optimization with SQLAlchemy

## 🚢 Production Deployment

### Pre-Deployment Checklist
- [ ] Change all SECRET_KEY values
- [ ] Update DATABASE_URL to production database
- [ ] Enable HTTPS with valid certificates
- [ ] Configure CORS origins for production domain
- [ ] Set ENVIRONMENT=production
- [ ] Set DEBUG=False
- [ ] Configure email service for notifications
- [ ] Set up database backups
- [ ] Enable audit logging
- [ ] Configure monitoring/alerting

### Deployment Steps
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run migrations
docker-compose run backend alembic upgrade head

# Start services
docker-compose -f docker-compose.yml up -d

# Verify health
docker-compose ps
curl http://localhost/health
```

## 📝 License

This project is proprietary and confidential.

## 👥 Support

For issues and questions, please refer to the troubleshooting section or contact the development team.
