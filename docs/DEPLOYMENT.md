# Deployment Guide

## Overview

This guide covers deploying the QI Digital Platform in various environments.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git

## Local Development Deployment

### 1. Clone Repository
```bash
git clone <repository-url>
cd aas-data-modeling
```

### 2. Setup Environment
```bash
# Create conda environment
conda create -n qi-digital-platform python=3.11 -y
conda activate qi-digital-platform

# Install dependencies
pip install -r requirements.txt
pip install -r webapp/requirements.txt
```

### 3. Start Platform
```bash
python main.py start
```

### 4. Access Services
- Web Interface: http://localhost:5000
- AI/RAG API: http://localhost:8000
- Twin Registry: http://localhost:8001
- Certificate Manager: http://localhost:3001
- Analytics Dashboard: http://localhost:3002

## Docker Deployment

### 1. Build and Start
```bash
docker-compose up -d
```

### 2. Check Status
```bash
docker-compose ps
```

### 3. View Logs
```bash
docker-compose logs -f
```

### 4. Stop Services
```bash
docker-compose down
```

## Production Deployment

### Environment Variables

Create a `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/qi_platform
REDIS_URL=redis://host:6379

# AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# Application
NODE_ENV=production
FLASK_ENV=production
```

### Database Setup

1. **PostgreSQL**
```sql
CREATE DATABASE qi_platform;
CREATE USER qi_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE qi_platform TO qi_user;
```

2. **Redis**
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: bind 127.0.0.1
# Set: requirepass your_redis_password
```

### Web Server (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Logging

### Health Checks

All services provide health check endpoints:
- `/health` - Service health status

### Logging

Services log to:
- Application logs: `logs/`
- System logs: `/var/log/`

### Monitoring

Recommended monitoring tools:
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- New Relic
- Datadog

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump qi_platform > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump qi_platform > $BACKUP_DIR/backup_$DATE.sql
```

### File Backup

```bash
# Backup important directories
tar -czf backup_$(date +%Y%m%d).tar.gz \
    digital-twins/ \
    certificates/ \
    logs/ \
    config/
```

## Security Considerations

### 1. Network Security
- Use HTTPS in production
- Implement firewall rules
- Use VPN for remote access

### 2. Authentication
- Implement JWT authentication
- Use strong passwords
- Enable 2FA where possible

### 3. Data Protection
- Encrypt sensitive data
- Regular security updates
- Access control and audit logs

### 4. API Security
- Rate limiting
- Input validation
- CORS configuration

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check port availability
   - Verify dependencies
   - Check logs

2. **Database connection issues**
   - Verify database is running
   - Check connection string
   - Test network connectivity

3. **Memory issues**
   - Monitor resource usage
   - Optimize configurations
   - Scale horizontally if needed

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set environment variables
export FLASK_DEBUG=1
export NODE_ENV=development

# Start with debug logging
python main.py start --debug
```

## Scaling

### Horizontal Scaling

1. **Load Balancer**
   - Use Nginx or HAProxy
   - Configure multiple instances
   - Health checks

2. **Database Scaling**
   - Read replicas
   - Connection pooling
   - Sharding if needed

3. **Microservices**
   - Deploy services independently
   - Use service mesh (Istio)
   - Implement circuit breakers

### Performance Optimization

1. **Caching**
   - Redis for session storage
   - CDN for static assets
   - Application-level caching

2. **Database Optimization**
   - Index optimization
   - Query optimization
   - Connection pooling

3. **Application Optimization**
   - Code profiling
   - Memory optimization
   - Async processing

## Maintenance

### Regular Tasks

1. **Security Updates**
   - Weekly dependency updates
   - Monthly security patches
   - Quarterly security audits

2. **Backup Verification**
   - Daily backup tests
   - Weekly restore tests
   - Monthly disaster recovery drills

3. **Performance Monitoring**
   - Daily health checks
   - Weekly performance reviews
   - Monthly capacity planning

### Update Procedures

1. **Zero-Downtime Deployment**
   - Blue-green deployment
   - Rolling updates
   - Feature flags

2. **Rollback Procedures**
   - Database rollback scripts
   - Application rollback
   - Configuration rollback

## Support

For deployment support:
- Check logs in `logs/` directory
- Review this documentation
- Create issues in the repository
- Contact the development team 