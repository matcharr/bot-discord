# Documentation Index

Welcome to the Discord bot documentation! 📚

## 🚀 Getting Started

- **[README.md](../README.md)** - Quick start guide
- **[DATABASE.md](DATABASE.md)** - Database configuration and management
- **[Git Workflow](git-workflow.md)** - Git development process

## 📋 Architecture

### Database
- **Models**: `project/database/models.py`
- **Services**: `project/database/services.py`
- **Security**: `project/database/security.py`
- **Tests**: `tests/database/`

### Project Structure
```
project/
├── database/           # Database layer
│   ├── models.py      # SQLAlchemy models
│   ├── services.py    # Business services
│   ├── security.py    # Encryption and security
│   └── connection.py  # Database configuration
├── cogs/              # Discord commands (future)
└── utils/             # Utilities

scripts/
├── db-manage.sh       # Database management
├── setup-git-hooks.sh # Git configuration
└── new-branch.sh      # Branch creation

docs/
├── DATABASE.md        # Database guide
└── git-workflow.md    # Git workflow
```

## 🛠️ Development

### Environments
- **Development**: PostgreSQL via Docker (`./scripts/db-manage.sh start`)
- **Test**: In-memory SQLite (`python -m pytest`)
- **Production**: Managed PostgreSQL (future)

### Useful Commands
```bash
# Database
./scripts/db-manage.sh start    # Start PostgreSQL
./scripts/db-manage.sh init     # Initialize tables
./scripts/db-manage.sh reset    # Complete reset

# Tests
python -m pytest tests/database/ -v    # Database tests
python -m pytest --cov=project        # With coverage

# Git workflow
./scripts/new-branch.sh feat "feature-name"  # New branch
./scripts/cleanup-branches.sh               # Cleanup
```

## 🔒 Security & GDPR

### Encryption
- **Sensitive data**: Encrypted with Fernet (AES 128)
- **Discord IDs**: Hashed with SHA-256 + salt + pepper
- **Lookup keys**: Optimized for performance

### GDPR Compliance
- **Export**: `WarningService.export_user_data(user_id)`
- **Deletion**: `WarningService.delete_user_data(user_id)`
- **Audit**: All actions are logged

## 📊 Tests & Quality

### Current Coverage
- **Database layer**: 26 tests ✅
- **Security**: 8 tests ✅
- **Services**: 10 tests ✅
- **Models**: 8 tests ✅

### Standards
- **Linting**: Black, isort, flake8
- **Type checking**: mypy
- **Tests**: pytest with coverage
- **CI/CD**: GitHub Actions

## 🚀 Deployment (future)

### Production
- Managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- Secure environment variables
- Automatic backups
- Monitoring and alerts

### Docker
- Optimized production image
- Multi-stage build
- Health checks
- Secrets management

## 📞 Support

### Troubleshooting
- **DB connection**: Check Docker with `./scripts/db-manage.sh status`
- **Tests failing**: Reset with `./scripts/db-manage.sh reset`
- **Import errors**: Check PYTHONPATH and structure

### Useful Logs
```bash
# Database logs
./scripts/db-manage.sh logs

# Application logs
tail -f logs/bot_dev.log

# Test logs
python -m pytest -v -s
```