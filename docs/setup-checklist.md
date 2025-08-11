# Setup Checklist 📋

Step-by-step guide to configure the development environment.

## ✅ Prerequisites

- [ ] **Python 3.11+** installed
- [ ] **Docker** and **Docker Compose** installed
- [ ] **Git** configured with your name/email
- [ ] **Kiro IDE** with recommended extensions

### Recommended Kiro Extensions
- [ ] **Python** - Complete Python support with IntelliSense
- [ ] **GitLens** - Visual Git history
- [ ] **SQLite Viewer** - Visualize SQLite databases
- [ ] **PostgreSQL** - PostgreSQL support (Chris Kolkman or SQL Tools)
- [ ] **YAML** - YAML support for docker-compose
- [ ] **Markdown All in One** - Markdown editing
- [ ] **Error Lens** - Inline errors

Note: Docker will be managed via external CLI (Kiro compatibility issue)

## 🚀 Installation

### 1. Clone and Initial Setup
```bash
# Clone the repo
git clone <your-repo-url>
cd bot-discord

# Install Python dependencies
pip install -r project/requirements.txt
pip install -r requirements-dev.txt

# Setup Git hooks
./scripts/setup-git-hooks.sh
chmod +x scripts/*.sh
```

### 2. Database Configuration
```bash
# Start PostgreSQL via Docker
./scripts/db-manage.sh start

# Check that DB is ready
./scripts/db-manage.sh status

# Initialize tables
./scripts/db-manage.sh init
```

### 3. Environment Configuration
```bash
# Copy the dev environment file
cp .env.development .env

# Edit .env with your Discord tokens
# DISCORD_TOKEN=your_bot_token_here
# DISCORD_GUILD_ID=your_test_guild_id
```

### 4. Validation Tests
```bash
# Test the database
python -m pytest tests/database/ -v

# Test PostgreSQL connection
./scripts/db-manage.sh psql
# In psql: \dt to see tables, \q to quit

# Check linting
make check
```

## 🔧 Verifications

### Database
- [ ] PostgreSQL starts without error
- [ ] Tables created correctly (`\dt` in psql)
- [ ] Database tests pass (26/26)
- [ ] Connection from Python works

### Python Environment
- [ ] All dependencies installed
- [ ] Tests pass without error
- [ ] Linting/formatting configured
- [ ] Type checking with mypy

### Git Workflow
- [ ] Git hooks installed
- [ ] Branch creation works
- [ ] Commits follow conventional format

### Discord (optional for DB dev)
- [ ] Bot token configured
- [ ] Guild ID configured
- [ ] Bot added to test server

## 🛠️ Useful Commands

### Database
```bash
./scripts/db-manage.sh start     # Start
./scripts/db-manage.sh stop      # Stop
./scripts/db-manage.sh restart   # Restart
./scripts/db-manage.sh reset     # Complete reset
./scripts/db-manage.sh psql      # PostgreSQL session
./scripts/db-manage.sh logs      # View logs
./scripts/db-manage.sh pgadmin   # Web interface
```

### Development
```bash
# Tests
python -m pytest                    # All tests
python -m pytest tests/database/    # Database tests only
python -m pytest --cov=project      # With coverage

# Code quality
make check          # Complete linting
black .            # Formatting
isort .            # Import sorting
flake8 .           # Linting
mypy project/      # Type checking

# Git workflow
./scripts/new-branch.sh feat "feature-name"  # New branch
./scripts/cleanup-branches.sh               # Cleanup
```

## 🚨 Troubleshooting

### Docker Won't Start
```bash
# Check Docker
docker --version
docker-compose --version

# Clean and restart
./scripts/db-manage.sh reset
```

### Tests Fail
```bash
# Check environment variables
python -c "import os; print(os.getenv('DATABASE_URL'))"

# Reset test database
./scripts/db-manage.sh reset
python -m pytest tests/database/ -v
```

### Python Import Errors
```bash
# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip install -r project/requirements.txt --force-reinstall
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Check Docker permissions
sudo usermod -aG docker $USER  # Linux
# Restart session
```

## ✅ Setup Complete!

Once all items are checked, you should have:
- ✅ Functional PostgreSQL database
- ✅ Passing tests (26/26)
- ✅ Configured development environment
- ✅ Operational Git workflow
- ✅ Kiro extensions installed

**Next steps:** Discord integration or new feature development! 🚀