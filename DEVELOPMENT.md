# FaceGuard Attendance - Development Guide

## 📋 Quick Start

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11+, Node.js 18+, PostgreSQL 16

### First Time Setup

```bash
# Clone and navigate
git clone <repo>
cd FaceGuard-Attendance

# Using Docker (Recommended)
docker-compose up --build

# Initialize database
docker exec faceguard-backend python -m alembic upgrade head

# Seed test data
docker exec faceguard-backend bash scripts/seed-data.sh

# Visit http://localhost:3000
```

## 🏗️ Project Structure

```
FaceGuard-Attendance/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── ai/                # Face recognition & ML
│   │   ├── services/          # Business logic layer
│   │   ├── routers/           # API route handlers
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   │   ├── ui/            # Basic UI components
│   │   │   └── attendance/    # Attendance-specific components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client layer
│   │   ├── store/             # Zustand stores
│   │   ├── hooks/             # Custom React hooks
│   │   ├── layouts/           # Layout components
│   │   ├── App.jsx            # Main app component
│   │   └── index.css          # Global styles
│   ├── package.json           # NPM dependencies
│   ├── vite.config.js         # Build configuration
│   └── .env.example           # Environment template
│
├── docker/                     # Docker configuration
│   ├── Dockerfile.backend     # Backend image
│   ├── Dockerfile.frontend    # Frontend image
│   └── nginx.conf             # Reverse proxy config
│
├── docker-compose.yml         # Service orchestration
├── README.md                  # Full documentation
├── DEPLOYMENT.md              # Production deployment
└── scripts/                   # Utility scripts
    ├── init-db.sh
    └── seed-data.sh
```

## 🔄 Development Workflow

### Adding a New API Endpoint

1. **Create Pydantic Schema** (`backend/app/schemas/__init__.py`):
```python
class MyRequestSchema(BaseModel):
    field1: str
    field2: int
```

2. **Create Database Model** (`backend/app/models/__init__.py`):
```python
class MyModel(Base):
    __tablename__ = "my_model"
    id = Column(Integer, primary_key=True)
    field1 = Column(String)
```

3. **Create Service** (`backend/app/services/my_service.py`):
```python
class MyService:
    @staticmethod
    def create_item(db: Session, request: MyRequestSchema):
        item = MyModel(**request.dict())
        db.add(item)
        db.commit()
        return item
```

4. **Create Router** (`backend/app/routers/my_router.py`):
```python
from fastapi import APIRouter, Depends
from app.core.database import get_db

router = APIRouter(prefix="/my", tags=["my"])

@router.post("/items")
def create_item(request: MyRequestSchema, db: Session = Depends(get_db)):
    return MyService.create_item(db, request)
```

5. **Register Router** (`backend/app/main.py`):
```python
from app.routers import my_router
app.include_router(my_router.router, prefix=API_V1_STR)
```

### Adding a React Page

1. **Create Page Component** (`frontend/src/pages/my_feature/MyPage.jsx`):
```jsx
import { useState, useEffect } from 'react'
import { Card, Button, LoadingSpinner } from '../../components/ui'

export default function MyPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setIsLoading(true)
    try {
      // Fetch data
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">My Feature</h1>
      <Card>Content here</Card>
    </div>
  )
}
```

2. **Add Route** (`frontend/src/App.jsx`):
```jsx
<Route path="/my-feature" element={<MyPage />} />
```

3. **Update Navigation** (`frontend/src/layouts/MainLayout.jsx`):
```jsx
<a href="/my-feature">My Feature</a>
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/test_auth.py::test_login
```

### Frontend Tests
```bash
cd frontend
npm test
npm test -- --coverage
```

## 📦 Database Migrations

### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

### Apply Migration
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

## 🐛 Common Issues & Solutions

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Verify DATABASE_URL in .env
# Format: postgresql://user:password@host:port/db_name

# Test connection
psql postgresql://user:password@host:port/db_name
```

### Face Recognition Not Working
1. Check lighting conditions
2. Ensure face is centered
3. Verify min image size (640x480)
4. Check FACE_RECOGNITION_TOLERANCE value

## 🔐 Security Best Practices

- Never commit .env files with actual secrets
- Use environment variables for sensitive data
- Always validate user input with Pydantic
- Use HTTPS in production
- Regularly update dependencies
- Keep JWT secrets strong and rotated
- Monitor and log all access attempts

## 📊 Performance Tips

### Backend
- Use database indexes on frequently queried columns
- Cache embedding vectors to avoid recalculation
- Use async operations for I/O
- Monitor database query performance

### Frontend
- Use lazy loading for routes
- Optimize images before upload
- Implement request debouncing
- Use React.memo for expensive components

## 🚀 Deployment

See DEPLOYMENT.md for production deployment guide.
