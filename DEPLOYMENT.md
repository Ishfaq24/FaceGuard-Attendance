# FaceGuard Attendance - Production Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying FaceGuard Attendance to production environments.

## 📋 Pre-Deployment Checklist

### Security
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Update `DATABASE_URL` to production PostgreSQL instance
- [ ] Configure HTTPS/TLS certificates
- [ ] Review and restrict `BACKEND_CORS_ORIGINS`
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Configure email service for notifications
- [ ] Enable database backups
- [ ] Set up monitoring and alerting

### Infrastructure
- [ ] Allocate sufficient resources for PostgreSQL
- [ ] Configure firewall rules
- [ ] Set up CDN for static assets (optional)
- [ ] Configure domain DNS records
- [ ] Test SSL certificate installation

### Application
- [ ] Run full test suite
- [ ] Perform load testing
- [ ] Verify all endpoints in staging
- [ ] Test face recognition accuracy
- [ ] Check geofencing calculations
- [ ] Validate fraud detection logic

## 🏢 Deployment Options

### Option 1: Docker Compose on VPS/Cloud VM

#### Provider Examples
- AWS EC2, DigitalOcean Droplets, Linode, Google Cloud Compute Engine, Azure VM

#### Steps

```bash
# 1. SSH into server
ssh user@server-ip

# 2. Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Clone repository
git clone <repository-url>
cd FaceGuard-Attendance

# 4. Create production environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 5. Edit environment files with production values
nano backend/.env
# Update:
# - DATABASE_URL (use managed PostgreSQL if available)
# - SECRET_KEY (use strong random key)
# - ENVIRONMENT=production
# - DEBUG=False
# - BACKEND_CORS_ORIGINS

nano frontend/.env
# Update:
# - VITE_API_URL=https://yourdomain.com/api/v1

# 6. Set up SSL certificate (Let's Encrypt)
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com

# 7. Update nginx.conf with certificate paths
nano docker/nginx.conf
# Uncomment HTTPS section and update paths

# 8. Build and start
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d

# 9. Verify services
docker-compose ps
curl http://localhost/health

# 10. Initialize database
docker-compose exec backend python -m alembic upgrade head
docker-compose exec backend bash scripts/seed-data.sh
```

### Option 2: Kubernetes Deployment

#### Prerequisites
- EKS, GKE, AKS, or self-managed Kubernetes cluster
- `kubectl` configured
- Docker registry (Docker Hub, ECR, GCR, etc.)

#### Steps

```bash
# 1. Build and push images to registry
docker build -f docker/Dockerfile.backend -t registry.example.com/faceguard-backend:v1.0 .
docker build -f docker/Dockerfile.frontend -t registry.example.com/faceguard-frontend:v1.0 .

docker push registry.example.com/faceguard-backend:v1.0
docker push registry.example.com/faceguard-frontend:v1.0

# 2. Create Kubernetes namespace
kubectl create namespace faceguard

# 3. Create ConfigMap for environment variables
kubectl create configmap faceguard-config \
  --from-env-file=backend/.env \
  -n faceguard

# 4. Create database (using managed service recommended)
# e.g., AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL

# 5. Deploy services (use provided k8s manifests)
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/ingress.yaml

# 6. Verify deployment
kubectl get pods -n faceguard
kubectl get svc -n faceguard
```

### Option 3: Managed Platforms

#### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker faceguard-attendance

# Create environment
eb create production

# Deploy
eb deploy

# View logs
eb logs
```

#### Heroku
```bash
# Login
heroku login

# Create app
heroku create faceguard-attendance

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Deploy
git push heroku main

# Run migrations
heroku run python -m alembic upgrade head
```

## 🔐 SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx.conf with certificate path
# Certificates are at: /etc/letsencrypt/live/yourdomain.com/

# Auto-renewal (runs daily)
sudo certbot renew --dry-run
```

### Update nginx.conf

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS header
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Monitoring & Logging

### Application Monitoring

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Or with Kubernetes
kubectl logs -f deployment/backend -n faceguard
```

### Database Monitoring

```bash
# Connect to PostgreSQL
psql postgresql://user:password@host:5432/faceguard_attendance

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Monitor connections
SELECT count(*) FROM pg_stat_activity;
```

### Third-Party Monitoring Tools

- **Datadog**: Centralized monitoring and logging
- **New Relic**: Application performance monitoring
- **Prometheus + Grafana**: Open-source monitoring stack
- **ELK Stack**: Elasticsearch, Logstash, Kibana for logs

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build images
        run: docker-compose build

      - name: Push to registry
        run: |
          docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}
          docker-compose push

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd FaceGuard-Attendance
            git pull
            docker-compose -f docker-compose.yml pull
            docker-compose -f docker-compose.yml up -d
            docker-compose exec -T backend python -m alembic upgrade head
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use PostgreSQL connection pooling (PgBouncer)
- Cache frequently accessed data (Redis)
- Use CDN for static frontend assets

### Vertical Scaling
- Increase CPU/RAM for database server
- Optimize database queries
- Enable caching strategies

### Performance Optimization

```bash
# Enable PostgreSQL query optimization
# Add to postgresql.conf:
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB

# Create database indexes
docker-compose exec backend python << 'EOF'
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE INDEX idx_attendance_student_id ON attendance_record(student_id);"))
    conn.execute(text("CREATE INDEX idx_attendance_session_id ON attendance_record(session_id);"))
    conn.commit()
EOF
```

## 🔄 Backup & Recovery

### Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U faceguard -Fc faceguard_attendance > backup.dump

# Automated backups with cron
0 2 * * * cd /path/to/FaceGuard-Attendance && docker-compose exec -T postgres pg_dump -U faceguard -Fc faceguard_attendance > backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).dump

# Restore from backup
docker-compose exec postgres pg_restore -U faceguard -d faceguard_attendance backup.dump
```

### Disaster Recovery Plan

1. Regular backups to off-site storage
2. Document recovery procedures
3. Test recovery process regularly
4. Monitor backup integrity
5. Keep application versioning for rollback

## 🧪 Testing Before Deployment

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/health

# Using LoadRunner or JMeter for complex scenarios
```

### Security Testing

```bash
# OWASP ZAP scanning
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://yourdomain.com

# Dependency scanning
docker run --rm -v $(pwd):/root anchore/grype:latest /root
```

### Functionality Testing

- Test all API endpoints
- Verify face recognition accuracy
- Test geofencing calculations
- Verify fraud detection triggers
- Test role-based access control

## 📞 Production Support

### Incident Response

1. **Monitoring Alerts**: Set up alerts for high error rates
2. **On-Call Rotation**: Establish support schedule
3. **Communication**: Use status page for transparency
4. **Root Cause Analysis**: Document incidents
5. **Post-Mortem**: Review and improve

### Troubleshooting Commands

```bash
# Check service health
curl https://yourdomain.com/health

# View error logs
docker-compose logs --tail=100 backend

# Database connectivity
docker-compose exec postgres psql -U faceguard -d faceguard_attendance -c "SELECT 1;"

# Restart specific service
docker-compose restart backend
```

## 📝 Maintenance Schedule

### Daily
- Monitor error logs
- Check database size
- Verify backups completed

### Weekly
- Review performance metrics
- Update dependencies
- Security patches

### Monthly
- Full security audit
- Performance optimization review
- Capacity planning

## 🎯 Performance Targets

- API Response Time: < 200ms (p95)
- Database Query Time: < 100ms (p95)
- Page Load Time: < 3s
- Face Recognition: < 500ms per image
- Liveness Detection: < 1s per check
- 99.9% uptime SLA

---

For additional support and updates, refer to README.md and DEVELOPMENT.md
