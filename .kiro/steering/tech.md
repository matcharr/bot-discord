# Technology Stack

## Core Technologies
- **Python 3.11+** - Primary language
- **discord.py 2.5.2** - Discord API library
- **PostgreSQL** - Database for secure data storage
- **SQLAlchemy 2.0.23** - ORM and database toolkit
- **Alembic 1.13.1** - Database migrations
- **Docker & Docker Compose** - Containerization and development environment

## Key Libraries
- **python-dotenv** - Environment variable management
- **psycopg2-binary** - PostgreSQL adapter
- **cryptography** - Data encryption for sensitive information
- **aiohttp** - Async HTTP client
- **psutil** - System monitoring

## Development Tools
- **Black** - Code formatting (line length: 88)
- **isort** - Import sorting (black profile)
- **flake8** - Linting
- **mypy** - Type checking
- **pre-commit** - Git hooks
- **pytest** - Testing framework with async support

## Common Commands

### Development Setup
```bash
make setup                    # Complete development setup
make install                  # Install dependencies only
pip install -r project/requirements.txt  # Production deps
pip install -r requirements-dev.txt      # Development deps
```

### Code Quality
```bash
make check                    # Format and lint code
make format                   # Format with black and isort
make lint                     # Run flake8 and mypy
```

### Testing
```bash
make test                     # Run tests with coverage
make test-fast               # Run tests without coverage
make test-db                 # Run database tests only
```

### Database Management
```bash
make db-start                # Start PostgreSQL
make db-init                 # Initialize database tables
make db-reset                # Reset database (deletes data)
make db-psql                 # Open PostgreSQL session
```

### Git Workflow
```bash
make new-branch TYPE=feat DESC="description"  # Create feature branch
make cleanup-branches        # Clean merged branches
./scripts/setup-git-hooks.sh # Setup Git hooks
```

### Running the Bot
```bash
make run                     # Run bot locally
python run.py               # Alternative run command
```

## Build System
- **Makefile** - Primary build automation
- **pyproject.toml** - Python project configuration
- **Docker** - Production deployment
- **Scripts** - Shell scripts for database and Git management