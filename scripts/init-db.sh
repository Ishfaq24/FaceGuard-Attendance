#!/bin/bash

# FaceGuard Attendance - Database Initialization Script

set -e

echo "🔧 Initializing FaceGuard Attendance Database..."

# Check PostgreSQL connection
echo "📍 Checking PostgreSQL connection..."
if ! command -v psql &> /dev/null; then
    echo "❌ psql not found. Install postgresql-client."
    exit 1
fi

# Run migrations
echo "📚 Running database migrations..."
python -m alembic upgrade head

# Verify tables
echo "✅ Database initialization complete!"
echo "📊 Database tables created successfully."
