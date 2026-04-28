#!/bin/bash

# FaceGuard Attendance - Database Seed Script
# Populates database with test data

set -e

echo "🌱 Seeding FaceGuard Attendance Database..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/../backend"

cd "$BACKEND_DIR"

# Create Python script for seeding
python << 'EOF'
from app.core.database import SessionLocal, engine
from app.models import (
    Base, User, Department, Class, Subject, Student, Teacher
)
from app.core.security import get_password_hash
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create departments
    dept_cse = Department(
        name="Computer Science & Engineering",
        code="CSE",
        created_at=datetime.utcnow()
    )
    dept_ece = Department(
        name="Electronics & Communication Engineering",
        code="ECE",
        created_at=datetime.utcnow()
    )
    
    db.add_all([dept_cse, dept_ece])
    db.commit()
    
    print("✅ Departments created")
    
    # Create admin user
    admin_user = User(
        email="admin@faceguard.com",
        password_hash=get_password_hash("admin123"),
        role="admin",
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    
    admin = Admin(
        user=admin_user,
        employee_id="ADM001",
        permissions={"all": True},
        created_at=datetime.utcnow()
    )
    
    db.add(admin)
    db.commit()
    
    print("✅ Admin user created (admin@faceguard.com / admin123)")
    
    # Create teacher users
    teacher_user = User(
        email="teacher@faceguard.com",
        password_hash=get_password_hash("teacher123"),
        role="teacher",
        full_name="John Teacher",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    
    teacher = Teacher(
        user=teacher_user,
        employee_id="TCH001",
        department_id=dept_cse.id,
        created_at=datetime.utcnow()
    )
    
    db.add(teacher)
    db.commit()
    
    print("✅ Teacher user created (teacher@faceguard.com / teacher123)")
    
    # Create student users
    for i in range(1, 6):
        student_user = User(
            email=f"student{i}@faceguard.com",
            password_hash=get_password_hash("student123"),
            role="student",
            full_name=f"Student {i}",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        student = Student(
            user=student_user,
            roll_number=f"STU{i:03d}",
            department_id=dept_cse.id,
            class_id=None,  # Will set after creating classes
            face_enrolled=False,
            biometric_status="not_enrolled",
            created_at=datetime.utcnow()
        )
        
        db.add(student)
    
    db.commit()
    
    print("✅ Student users created")
    
    # Create classes
    class_a = Class(
        name="Class A",
        code="CSE-A",
        semester=1,
        department_id=dept_cse.id,
        teacher_id=teacher.id,
        created_at=datetime.utcnow()
    )
    
    db.add(class_a)
    db.commit()
    
    print("✅ Classes created")
    
    # Create subjects
    subject = Subject(
        name="Data Structures",
        code="CS101",
        class_id=class_a.id,
        credits=4,
        created_at=datetime.utcnow()
    )
    
    db.add(subject)
    db.commit()
    
    print("✅ Subjects created")
    
    print("\n✨ Database seeding completed successfully!")
    print("\n📝 Test Accounts:")
    print("   Admin: admin@faceguard.com / admin123")
    print("   Teacher: teacher@faceguard.com / teacher123")
    print("   Students: student1-5@faceguard.com / student123")

except Exception as e:
    print(f"❌ Error during seeding: {e}")
    db.rollback()
    raise

finally:
    db.close()
EOF

echo "✅ Database seeding complete!"
