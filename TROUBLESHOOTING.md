# FaceGuard Attendance - Troubleshooting Guide

## 🔧 Common Issues & Solutions

### Backend Issues

#### 1. Database Connection Error

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Verify DATABASE_URL format in .env
# Should be: postgresql://user:password@host:port/database

# Test connection directly
psql postgresql://faceguard:faceguard@localhost:5432/faceguard_attendance

# Restart PostgreSQL
docker-compose restart postgres
docker-compose exec postgres psql -U faceguard -d faceguard_attendance -c "SELECT 1;"
```

#### 2. Migration Errors

**Error**: `ERROR: relation "user" already exists`

**Solutions**:
```bash
# Check migration status
docker-compose exec backend alembic current

# Downgrade to base
docker-compose exec backend alembic downgrade base

# Re-run migrations
docker-compose exec backend alembic upgrade head

# For manual rollback
docker-compose exec postgres psql -U faceguard -d faceguard_attendance -c "DROP TABLE IF EXISTS alembic_version CASCADE;"
```

#### 3. JWT Token Errors

**Error**: `Could not validate credentials` or `Invalid token`

**Solutions**:
```bash
# Verify SECRET_KEY in .env is strong
# Generate new key:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with new SECRET_KEY
# Restart backend
docker-compose restart backend

# Clients need to re-login
```

#### 4. Memory Issues

**Error**: `MemoryError` or `Out of memory`

**Solutions**:
```bash
# Increase Docker memory limit in docker-compose.yml
services:
  backend:
    mem_limit: 4g
    memswap_limit: 4g

# Or restart containers
docker-compose restart
```

#### 5. Face Recognition Model Issues

**Error**: `face_recognition model not found` or similar

**Solutions**:
```bash
# Reinstall dependencies
docker-compose exec backend pip install --force-reinstall face_recognition

# Check image size is sufficient
# From logs, face images should be at least 640x480

# Verify OpenCV installation
docker-compose exec backend python -c "import cv2; print(cv2.__version__)"
```

### Frontend Issues

#### 1. Camera Permission Denied

**Error**: `NotAllowedError: Permission denied`

**Solutions**:
- Check browser permissions (camera icon in address bar)
- Use HTTPS (required in production for camera access)
- Try a different browser
- Clear browser cache and cookies

#### 2. API Connection Errors

**Error**: `Failed to fetch`, CORS errors

**Solutions**:
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in frontend/.env
# Should match your backend URL

# Check CORS configuration in backend/.env
# BACKEND_CORS_ORIGINS should include frontend origin

# Restart both services
docker-compose restart frontend backend
```

#### 3. Build Errors

**Error**: `Module not found` or `npm ERR!`

**Solutions**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force

# Rebuild
npm run build
```

#### 4. State Management Issues

**Error**: `Cannot read property of undefined` (Zustand store)

**Solutions**:
```javascript
// Ensure store is properly initialized
import { useAuthStore } from './store'

// Check store state in console
const store = useAuthStore.getState()
console.log(store)

// Reset store to initial state
useAuthStore.setState(useAuthStore.getInitialState())
```

#### 5. Routing Issues

**Error**: `Cannot match any routes` or blank page

**Solutions**:
- Verify routes in App.jsx match your intentions
- Check ProtectedRoute is wrapping correctly
- Clear browser cache
- Check browser console for JavaScript errors

### Docker Issues

#### 1. Port Already in Use

**Error**: `Address already in use` or `Bind for 0.0.0.0:8000 failed`

**Solutions**:
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port in docker-compose.yml
ports:
  - "9000:8000"
```

#### 2. Container Won't Start

**Error**: `Container exited with code 1` or similar

**Solutions**:
```bash
# Check logs
docker-compose logs backend

# Rebuild image
docker-compose build --no-cache backend

# Remove old images/containers
docker-compose down -v
docker system prune -a

# Restart
docker-compose up
```

#### 3. Permission Denied

**Error**: `Permission denied` in Docker

**Solutions**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo docker-compose up
```

### Network Issues

#### 1. Container Can't Reach Other Container

**Error**: `Cannot connect to X container`

**Solutions**:
```bash
# Verify containers are on same network
docker network ls
docker network inspect faceguard-attendance_default

# Check container names match in docker-compose.yml
docker-compose ps

# Test connectivity
docker-compose exec backend ping postgres
docker-compose exec backend curl http://nginx/health
```

#### 2. Can't Access Service from Outside

**Error**: `Connection refused` when accessing from browser

**Solutions**:
```bash
# Verify port mapping
docker-compose ps

# Check firewall rules
sudo ufw status
sudo ufw allow 8000
sudo ufw allow 3000

# Test locally first
curl http://localhost:8000/health

# Verify service is listening
docker-compose exec backend netstat -tlnp | grep 8000
```

### Face Recognition Issues

#### 1. Face Not Detected

**Error**: `No face detected in image`

**Causes & Solutions**:
- Poor lighting → Improve lighting
- Face too small → Move closer to camera
- Partial face visible → Adjust position
- Unsupported angle → Face head-on to camera
- Image quality issues → Clear camera lens

**Debug**:
```python
# In Python shell
from app.ai.face_engine import FaceEngine
engine = FaceEngine()

# Test with image
faces = engine.detect_faces(image_data)
print(f"Faces found: {len(faces)}")
```

#### 2. Face Recognition Poor Accuracy

**Error**: `Face confidence too low` or `Match not found`

**Solutions**:
```bash
# Adjust tolerance in .env
FACE_RECOGNITION_TOLERANCE=0.6  # Lower = stricter
# Recommended range: 0.5-0.7

# Increase enrollment images
MIN_FACE_ENROLLMENT_IMAGES=20  # From 15

# Re-enroll with better images
# User should capture faces from multiple angles

# Check face quality during enrollment
# Quality score should be > 75
```

#### 3. Liveness Detection False Positives/Negatives

**Error**: `Liveness check failed unexpectedly`

**Solutions**:
```bash
# Adjust liveness score threshold
MIN_LIVENESS_SCORE=0.75  # Can lower to 0.65

# Check lighting (texture analysis needs good lighting)
# Check for natural movements
# Avoid spoof-like patterns (blinking too fast, etc)
```

### Performance Issues

#### 1. Slow API Responses

**Error**: API takes >1s to respond

**Solutions**:
```bash
# Check database query performance
docker-compose exec postgres psql -U faceguard -d faceguard_attendance
\dt+  # List tables with sizes
\l+   # Database sizes

# Monitor active queries
SELECT pid, query, query_start FROM pg_stat_activity;

# Create missing indexes
CREATE INDEX idx_attendance_session_id ON attendance_record(session_id);
CREATE INDEX idx_attendance_student_id ON attendance_record(student_id);

# Check backend logs for slow operations
docker-compose logs --tail=100 backend
```

#### 2. High Memory Usage

**Error**: Docker container memory limit exceeded

**Solutions**:
```bash
# Monitor memory
docker stats

# Increase limit in docker-compose.yml
services:
  backend:
    mem_limit: 4g

# Optimize image processing
# Reduce image size before ML operations
# Clear caches regularly

# Update backend
docker-compose build --no-cache backend
```

#### 3. Slow Face Recognition

**Error**: Face enrollment/verification takes >5s

**Solutions**:
```bash
# Reduce image resolution
# Check GPU availability (if using GPU)
# Optimize num_jitters in FaceEngine
# Clear background processes

# Profile code
python -m cProfile -s cumtime app/main.py
```

## 📞 Getting Help

### Debug Mode
```bash
# Enable verbose logging
# In backend/.env
LOG_LEVEL=DEBUG

# In frontend, browser console
localStorage.setItem('DEBUG', 'true')

# Restart services
docker-compose restart
```

### Logs Collection
```bash
# Collect all logs
docker-compose logs > debug_logs.txt

# Or specific service
docker-compose logs backend > backend_logs.txt
```

### System Information
```bash
# Docker version
docker --version

# Docker Compose version
docker-compose --version

# System info
uname -a
```

### Before Contacting Support

1. Collect error messages and logs
2. Describe exact steps to reproduce
3. Check troubleshooting guide first
4. Provide system information
5. Include docker-compose versions
6. Check .env file configuration (sanitize secrets)

---

If issues persist after following this guide, please contact the development team with collected debug information.
