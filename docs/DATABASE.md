# Database Configuration & Management

## Architecture Overview

Our database system uses SQLAlchemy with multi-environment support:

- **Development/Test**: PostgreSQL via Docker
- **Production**: Managed PostgreSQL (cloud or dedicated server)
- **CI/Tests**: In-memory SQLite (fast and isolated)

## Environments

### 🧪 Development & Test
```bash
# PostgreSQL via Docker Compose
DATABASE_URL="postgresql://botuser:devpassword@localhost:5432/botdb_dev"
```

**Advantages:**
- Same engine as production
- Complete data isolation
- Easy reset with Docker
- No risk of production data pollution

### 🚀 Production
```bash
# Managed PostgreSQL (e.g., AWS RDS, DigitalOcean, etc.)
DATABASE_URL="postgresql://prod_user:secure_password@prod-db.example.com:5432/botdb_prod"
```

**Security:**
- Dedicated user with limited permissions
- Mandatory SSL connections
- Automatic backups
- Monitoring and alerts

### ⚡ CI/Tests
```bash
# In-memory SQLite for tests
DATABASE_URL="sqlite:///:memory:"
```

**Advantages:**
- Ultra fast
- No setup required
- Perfect isolation between tests

## Development Setup with Docker

### 1. Docker Compose for PostgreSQL

Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: botdb_dev
      POSTGRES_USER: botuser
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U botuser -d botdb_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 2. Management Commands

```bash
# Start dev database
docker-compose -f docker-compose.dev.yml up -d

# Stop and clean
docker-compose -f docker-compose.dev.yml down -v

# Database logs
docker-compose -f docker-compose.dev.yml logs postgres

# Complete data reset
docker-compose -f docker-compose.dev.yml down -v && docker-compose -f docker-compose.dev.yml up -d
```

## Environment Variables

### .env.development
```bash
DATABASE_URL=postgresql://botuser:devpassword@localhost:5432/botdb_dev
ENCRYPTION_KEY=dev_encryption_key_base64_encoded_here
SALT_KEY=dev_salt_key_base64_encoded_here
PEPPER_KEY=dev_pepper_key_base64_encoded_here
```

### .env.production
```bash
DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@prod-db.example.com:5432/botdb_prod
ENCRYPTION_KEY=${ENCRYPTION_KEY}
SALT_KEY=${SALT_KEY}
PEPPER_KEY=${PEPPER_KEY}
```

### .env.test
```bash
DATABASE_URL=sqlite:///:memory:
ENCRYPTION_KEY=test_key_for_ci_only
SALT_KEY=test_salt_for_ci_only
PEPPER_KEY=test_pepper_for_ci_only
```

## Migrations & Schema

### Initialization
```bash
# Create tables
python -c "from project.database.connection import init_database; init_database()"
```

### Future Migrations
When we have more schema changes, we'll use Alembic:
```bash
# Generate a migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head
```

## Security & GDPR

### Data Encryption
- **Warning reasons**: Encrypted with Fernet (AES 128)
- **Discord IDs**: Hashed with SHA-256 + salt + pepper
- **Lookup keys**: Truncated for performance

### GDPR Compliance
- **Data export**: `WarningService.export_user_data()`
- **Deletion**: `WarningService.delete_user_data()` (soft delete)
- **Audit trail**: All actions are logged

## Monitoring & Maintenance

### Important Metrics
- Number of warnings per guild
- Database size
- Query performance
- Encryption/decryption errors

### Backups
- **Dev**: Not necessary (test data)
- **Prod**: Daily automatic backups + 30-day retention

## Troubleshooting

### Common Issues

**PostgreSQL connection error:**
```bash
# Check that Docker is running
docker-compose -f docker-compose.dev.yml ps

# Check logs
docker-compose -f docker-compose.dev.yml logs postgres
```

**Encryption error:**
```bash
# Check environment keys
python -c "import os; print('ENCRYPTION_KEY' in os.environ)"
```

**Failing tests:**
```bash
# Clean and restart
docker-compose -f docker-compose.dev.yml down -v
python -m pytest tests/database/ -v
```