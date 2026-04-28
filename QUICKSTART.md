# FaceGuard Attendance - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM minimum
- Port 80, 443, 8000, 3000, 5432 available

### Step 1: Clone & Setup (1 minute)
```bash
cd FaceGuard-Attendance

# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Step 2: Start Services (2 minutes)
```bash
# Build and start all services
docker-compose up --build

# Wait for all containers to show "running"
# Usually takes 1-2 minutes
```

### Step 3: Initialize Database (1 minute)
```bash
# In a new terminal:
docker-compose exec backend python -m alembic upgrade head

# Seed test data (optional)
docker-compose exec backend bash scripts/seed-data.sh
```

### Step 4: Access Application (1 minute)
```
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

### Step 5: Test Login
**Admin Account**:
- Email: `admin@faceguard.com`
- Password: `admin123`

**Teacher Account**:
- Email: `teacher@faceguard.com`
- Password: `teacher123`

**Student Account**:
- Email: `student1@faceguard.com` (1-5)
- Password: `student123`

---

## 📋 Troubleshooting Quick Fixes

### Services Won't Start
```bash
# Clean and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Port Already in Use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Database Connection Failed
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

### Can't Access Frontend
```bash
# Verify frontend is running
docker-compose logs frontend

# Check http://localhost:3000
# If blank, check browser console
```

---

## 🔄 Common Tasks

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Clean Everything
```bash
docker-compose down -v
```

---

## ✅ Verification Checklist

After startup, verify:
- [ ] Backend running: `curl http://localhost:8000/health`
- [ ] Frontend loads: `http://localhost:3000`
- [ ] API Docs available: `http://localhost:8000/docs`
- [ ] Can login with test account
- [ ] Database connected: Check backend logs

---

## 📚 Next Steps

1. **Read Documentation**:
   - [README.md](README.md) - Full documentation
   - [API_REFERENCE.md](API_REFERENCE.md) - API endpoints
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

2. **Explore Features**:
   - Try face enrollment (Students)
   - Create attendance session (Teachers)
   - View analytics (Admin)

3. **Deploy to Production**:
   - See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 💡 Pro Tips

- **Enable Camera**: Make sure to grant camera permissions
- **Use HTTPS**: Required for camera in production
- **Test Mode**: All test accounts work with password `123` suffix
- **API Docs**: Interactive Swagger UI at `/docs`
- **Dark Mode**: Toggle in frontend settings

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
