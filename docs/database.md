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
      - ./scripts/init-dev.sql:/docker-entrypoint-initdb.d/init.sql
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

### Key Generation

Before setting up your environment, generate secure encryption keys:

+**⚠️ CRITICAL SECURITY WARNING**:
- NEVER use the same keys across different environments
- NEVER commit keys to version control
- NEVER share keys between team members
- Generate NEW keys for each environment using the code below

```python
# Generate encryption keys (run this in Python)
from cryptography.fernet import Fernet
import base64
import secrets

# Generate Fernet encryption key
encryption_key = Fernet.generate_key().decode()
print(f"ENCRYPTION_KEY={encryption_key}")

# Generate salt and pepper keys (32 bytes each)
salt_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
pepper_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
print(f"SALT_KEY={salt_key}")
print(f"PEPPER_KEY={pepper_key}")
```

### .env.development
```bash
DATABASE_URL=postgresql://botuser:devpassword@localhost:5432/botdb_dev
# Generate strong keys for development - never use these examples!
ENCRYPTION_KEY=<generate_with_cryptography.fernet.Fernet.generate_key()>
SALT_KEY=<generate_random_base64_32_bytes>
PEPPER_KEY=<generate_random_base64_32_bytes>
```

**⚠️ Security Warning**: Always generate unique keys for each environment. Never use example keys in any environment!

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
# Test keys - generate unique ones for your test environment
ENCRYPTION_KEY=<generate_unique_test_key>
SALT_KEY=<generate_unique_test_salt>
PEPPER_KEY=<generate_unique_test_pepper>
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
