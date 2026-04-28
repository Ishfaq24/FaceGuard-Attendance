# FaceGuard Attendance - API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints (except `/auth/signup` and `/auth/login`) require:
```
Authorization: Bearer <access_token>
```

## Response Format
```json
{
  "data": {},
  "message": "Success",
  "status": 200
}
```

---

## Authentication Endpoints

### 1. User Signup
```
POST /auth/signup
```

**Request**:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "SecurePass123!",
  "role": "student"
}
```

**Response** (201):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "student"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 2. User Login
```
POST /auth/login
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):
```json
{
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 3. Refresh Token
```
POST /auth/refresh
```

**Request**:
```json
{
  "refresh_token": "eyJ..."
}
```

**Response** (200):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 4. Get Current User
```
GET /auth/me
```

**Response** (200):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "student"
}
```

### 5. Change Password
```
POST /auth/change-password
```

**Request**:
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

**Response** (200):
```json
{
  "message": "Password updated successfully"
}
```

### 6. Logout
```
POST /auth/logout
```

**Response** (200):
```json
{
  "message": "Logout successful"
}
```

---

## Face Management Endpoints

### 1. Start Enrollment
```
POST /face/enroll/start
```

**Response** (200):
```json
{
  "enrollment_id": "enc-123",
  "images_required": 15,
  "message": "Enrollment started"
}
```

### 2. Capture Enrollment Image
```
POST /face/enroll/capture
```

**Request**:
```json
{
  "image_base64": "iVBORw0KGgo...",
  "challenge_response": "iVBORw0KGgo..."
}
```

**Response** (200):
```json
{
  "message": "Image captured",
  "progress": {
    "images_captured": 5,
    "images_required": 15,
    "enrollment_complete": false
  }
}
```

### 3. Complete Enrollment
```
POST /face/enroll/complete
```

**Response** (200):
```json
{
  "message": "Face enrollment completed",
  "primary_embedding": "...",
  "images_stored": 15
}
```

### 4. Verify Face
```
POST /face/verify
```

**Request**:
```json
{
  "image_base64": "iVBORw0KGgo..."
}
```

**Response** (200):
```json
{
  "is_verified": true,
  "confidence": 0.95,
  "liveness_score": 0.92,
  "message": "Face verified successfully"
}
```

### 5. Get Enrollment Status
```
GET /face/enrollment-status
```

**Response** (200):
```json
{
  "is_enrolled": true,
  "enrollment_date": "2024-01-15T10:30:00",
  "image_count": 15,
  "quality_score": 0.88
}
```

---

## Attendance Endpoints

### 1. Create Attendance Session
```
POST /attendance/sessions
```

**Request**:
```json
{
  "subject_id": 1,
  "class_id": 1,
  "session_name": "Lecture 1",
  "scheduled_start": "2024-01-20T10:00:00",
  "scheduled_end": "2024-01-20T11:00:00",
  "require_geofence": true,
  "require_liveness": true
}
```

**Response** (201):
```json
{
  "session_id": 1,
  "status": "pending",
  "message": "Session created"
}
```

### 2. Start Session
```
POST /attendance/sessions/{session_id}/start
```

**Response** (200):
```json
{
  "session_id": 1,
  "status": "active",
  "actual_start_time": "2024-01-20T10:00:00"
}
```

### 3. End Session
```
POST /attendance/sessions/{session_id}/end
```

**Response** (200):
```json
{
  "session_id": 1,
  "status": "closed",
  "actual_end_time": "2024-01-20T11:00:00",
  "total_students": 30,
  "present": 28
}
```

### 4. Mark Attendance
```
POST /attendance/mark
```

**Request**:
```json
{
  "session_id": 1,
  "image_base64": "iVBORw0KGgo...",
  "user_latitude": 28.6139,
  "user_longitude": 77.2090,
  "challenge_response": "iVBORw0KGgo..."
}
```

**Response** (200):
```json
{
  "attendance_id": 1,
  "status": "present",
  "face_confidence": 0.95,
  "liveness_score": 0.92,
  "geofence_verified": true,
  "is_flagged": false,
  "message": "Attendance marked successfully"
}
```

### 5. Get Attendance History
```
GET /attendance/history?limit=30
```

**Response** (200):
```json
{
  "data": [
    {
      "session_id": 1,
      "subject": "Data Structures",
      "date": "2024-01-20",
      "status": "present",
      "confidence": 0.95
    }
  ],
  "total": 45
}
```

### 6. Get Session Records (Teacher/Admin)
```
GET /attendance/sessions/{session_id}/records
```

**Response** (200):
```json
{
  "session": { ... },
  "records": [
    {
      "student_id": 1,
      "status": "present",
      "face_confidence": 0.95,
      "liveness_score": 0.92,
      "is_flagged": false
    }
  ]
}
```

### 7. Get Fraud Logs (Admin)
```
GET /attendance/fraud-logs?severity=high&limit=50
```

**Response** (200):
```json
{
  "data": [
    {
      "fraud_log_id": 1,
      "student_id": 1,
      "fraud_type": "spoof_attempt",
      "severity": "high",
      "evidence": { ... },
      "created_at": "2024-01-20T10:15:00",
      "is_resolved": false
    }
  ],
  "total": 15
}
```

---

## Admin Endpoints

### 1. Create Department
```
POST /admin/departments
```

**Request**:
```json
{
  "name": "Computer Science",
  "code": "CSE"
}
```

**Response** (201):
```json
{
  "department_id": 1,
  "name": "Computer Science",
  "code": "CSE"
}
```

### 2. Get Departments
```
GET /admin/departments
```

**Response** (200):
```json
{
  "data": [ ... ],
  "total": 5
}
```

### 3. Create Class
```
POST /admin/classes
```

**Request**:
```json
{
  "name": "Class A",
  "code": "CSE-A",
  "semester": 1,
  "department_id": 1,
  "teacher_id": 1
}
```

**Response** (201):
```json
{
  "class_id": 1,
  "name": "Class A",
  "code": "CSE-A"
}
```

### 4. Create Subject
```
POST /admin/subjects
```

**Request**:
```json
{
  "name": "Data Structures",
  "code": "CS101",
  "class_id": 1,
  "credits": 4
}
```

**Response** (201):
```json
{
  "subject_id": 1,
  "name": "Data Structures",
  "code": "CS101"
}
```

### 5. Create Geofence
```
POST /admin/geofence
```

**Request**:
```json
{
  "class_id": 1,
  "latitude": 28.6139,
  "longitude": 77.2090,
  "radius_meters": 100
}
```

**Response** (201):
```json
{
  "geofence_id": 1,
  "class_id": 1,
  "radius_meters": 100
}
```

### 6. Get Analytics - Attendance
```
GET /admin/analytics/attendance?start_date=2024-01-01&end_date=2024-01-31&department_id=1
```

**Response** (200):
```json
{
  "total_sessions": 20,
  "total_records": 600,
  "average_attendance": 0.92,
  "by_class": [ ... ]
}
```

### 7. Get Analytics - Fraud
```
GET /admin/analytics/fraud?start_date=2024-01-01&severity=high
```

**Response** (200):
```json
{
  "total_incidents": 15,
  "by_type": {
    "spoof": 5,
    "duplicate": 4,
    "geofence": 3,
    "mismatch": 2,
    "time": 1
  },
  "by_severity": { ... }
}
```

### 8. Get Users (Admin)
```
GET /admin/users?role=student&limit=50
```

**Response** (200):
```json
{
  "data": [ ... ],
  "total": 150
}
```

### 9. Deactivate User
```
POST /admin/users/{user_id}/deactivate
```

**Response** (200):
```json
{
  "message": "User deactivated",
  "user_id": 1,
  "is_active": false
}
```

### 10. Activate User
```
POST /admin/users/{user_id}/activate
```

**Response** (200):
```json
{
  "message": "User activated",
  "user_id": 1,
  "is_active": true
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Duplicate attendance record"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Pagination

List endpoints support pagination:
```
GET /endpoint?limit=20&offset=0
```

**Response**:
```json
{
  "data": [ ... ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

---

## Rate Limiting

- `/auth/login`: 5 attempts per minute per IP
- `/auth/signup`: 10 requests per minute per IP
- Other endpoints: 100 requests per minute per user

---

**API Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production Ready
