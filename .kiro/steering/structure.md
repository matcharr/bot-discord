# Project Structure

## Root Directory Layout
```
├── project/                 # Main application code
├── tests/                   # Test suite
├── scripts/                 # Shell scripts for automation
├── docs/                    # Documentation
├── .kiro/                   # Kiro AI assistant configuration
├── .github/                 # GitHub workflows and templates
└── [config files]          # Various configuration files
```

## Core Application (`project/`)
```
project/
├── main.py                  # Bot entry point and event handlers
├── config.py                # Configuration management from env vars
├── requirements.txt         # Production dependencies
├── cogs/                    # Bot functionality modules (Discord cogs)
├── database/                # Database layer and models
├── utils/                   # Shared utilities and helpers
└── logs/                    # Runtime log files
```

## Cogs Architecture (`project/cogs/`)
Each cog is a self-contained module providing specific bot functionality:
- `anti_raid.py` - Spam detection and automatic user kicking
- `moderation.py` - Warning, kick, ban, mute commands
- `logging_system.py` - Event logging to designated channels
- `role_management.py` - Role creation and assignment
- `invite_management.py` - Invite tracking and monitoring
- `reporting.py` - User reporting system
- `admin.py` - Administrative commands
- `server_stats.py` - Server statistics and monitoring
- `user_info.py` - User information commands
- `welcome_goodbye.py` - Member join/leave handling

## Database Layer (`project/database/`)
- `models.py` - SQLAlchemy models with encryption/security
- `connection.py` - Database connection and base setup
- `services.py` - Business logic and data access layer
- `security.py` - Encryption, hashing, and security utilities
- `migration.py` - Database schema migrations
- `cleanup.py` - Data retention and cleanup tasks

## Utilities (`project/utils/`)
- `logger.py` - Centralized logging configuration
- `permissions.py` - Permission validation helpers
- `audit.py` - Audit logging for moderation actions
- `health.py` - Health monitoring and status checks
- `backup.py` - Data backup utilities

## Testing Structure (`tests/`)
- `test_config.py` - Configuration testing
- `test_moderation.py` - Moderation functionality tests
- `database/` - Database-specific tests
  - `test_models.py` - Model validation tests
  - `test_services.py` - Service layer tests
  - `test_security.py` - Security and encryption tests

## Configuration Files
- `.env.example` - Environment variable template
- `.env.development` - Development environment config
- `.env.test` - Test environment config
- `pyproject.toml` - Python project and tool configuration
- `docker-compose.yml` - Production container setup
- `docker-compose.dev.yml` - Development container setup

## Automation Scripts (`scripts/`)
- `db-manage.sh` - Database management (start/stop/reset/init)
- `setup-git-hooks.sh` - Git workflow setup
- `new-branch.sh` - Standardized branch creation
- `cleanup-branches.sh` - Branch cleanup automation
- `verify-setup.sh` - Development environment verification

## Key Patterns
- **Cog-based architecture** - Each feature is a separate Discord cog
- **Layered database access** - Models → Services → Cogs
- **Security-first design** - Encrypted storage, hashed identifiers
- **Environment-based config** - All settings via environment variables
- **Comprehensive logging** - Structured logging throughout application
- **Git workflow automation** - Scripts for branch management and hooks