# Discord Moderation Bot

[![CI](https://github.com/matcharr/bot-discord/workflows/CI/badge.svg)](https://github.com/matcharr/bot-discord/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3.1-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive Discord bot with moderation tools, anti-raid protection, and server management features.

## Quick Start

1. **Install dependencies**: `pip install -r project/requirements.txt`
2. **Setup database**: `./scripts/db-manage.sh start && ./scripts/db-manage.sh init`
3. **Configure environment**: Copy `.env.development` and update with your bot token
4. **Create a "logs" channel** in your Discord server
5. **Run the bot**: `python main.py`

## Development Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup Steps
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup database (PostgreSQL via Docker)
./scripts/db-manage.sh start
./scripts/db-manage.sh init

# Setup Git hooks and workflow tools
./scripts/setup-git-hooks.sh

# Create a new feature branch
./scripts/new-branch.sh feat "your-feature-name"

# Run tests
python -m pytest

# Format and lint code
make check
```

### Database Management
```bash
# Start PostgreSQL
./scripts/db-manage.sh start

# Stop PostgreSQL  
./scripts/db-manage.sh stop

# Reset database (⚠️ deletes all data)
./scripts/db-manage.sh reset

# Open PostgreSQL session
./scripts/db-manage.sh psql

# View logs
./scripts/db-manage.sh logs
```

See [docs/DATABASE.md](docs/DATABASE.md) for complete database documentation.

### Git Workflow
This project uses a standardized Git workflow with automated tools:

- **Branch naming**: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`
- **Automated branch creation**: `./scripts/new-branch.sh <type> <description>`
- **Branch cleanup**: `./scripts/cleanup-branches.sh`
- **Commit validation**: Enforced conventional commit format

See [docs/git-workflow.md](docs/git-workflow.md) for complete documentation.

## Features & Commands

### 🛡️ Anti-Raid Protection
Automatically detects and kicks spammers (10+ messages triggers kick, 10-second cooldown per message).

### ⚖️ Moderation Commands
- `/warn @user reason` - Issue warnings (stored in warnings.json)
- `/warnings @user` - View user warnings
- `/kick @user reason` - Kick user
- `/ban @user reason` - Ban user  
- `/unban user#1234` - Unban user
- `/mute @user reason` - Mute user (creates Muted role)
- `/tempban @user 1h reason` - Temporary ban (m/h/d)
- `/tempmute @user 30m reason` - Temporary mute
- `/purge 10 @user` - Delete messages (optional user filter)

### 🔧 Role Management
- `/create_role name color` - Create new role
- `/delete_role @role` - Delete role
- `/add_role @user @role` - Assign role
- `/remove_role @user @role` - Remove role

### 📊 Logging & Monitoring
- **Auto-logs**: Message deletions, member joins/leaves to #logs channel
- **Invite tracking**: Monitors invite creation/deletion and usage
- **Report system**: `/report @user reason` sends reports to moderators

## Required Bot Permissions

```
✅ Send Messages          ✅ Manage Messages
✅ Kick Members           ✅ Ban Members  
✅ Manage Roles           ✅ View Audit Log
✅ Embed Links            ✅ Manage Guild
```

## Setup Checklist

1. Copy `.env.example` to `.env` and configure:
   - `BOT_TOKEN=your_bot_token`
   - `REPORT_CHANNEL_ID=your_channel_id`
2. Create `#logs` channel for event logging
3. Create report channel and add ID to `.env` file
4. Ensure bot role is above roles it needs to manage
5. Test with `!warn @user test` to verify warnings.json creation

## File Structure
```
project/cogs/
├── anti_raid.py      # Spam detection & auto-kick
├── moderation.py     # Warning/kick/ban/mute commands  
├── logging_system.py # Event logging to #logs
├── role_management.py # Role creation & assignment
├── invite_management.py # Invite tracking
└── reporting.py      # User reporting system
```

## Loading Cogs
```python
# In your main bot file
cogs = ['anti_raid', 'moderation', 'logging_system', 
        'role_management', 'invite_management', 'reporting']

for cog in cogs:
    await bot.load_extension(f'cogs.{cog}')
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and commit message standards.

## Documentation

- **[Database Setup](docs/database.md)** - Database configuration and management
- **[Git Workflow](docs/git-workflow.md)** - Git development process  
- **[Setup Checklist](docs/setup-checklist.md)** - Step-by-step setup guide
- **[Setup without Docker](docs/setup-no-docker.md)** - Alternative setup method

## Project Structure
```
├── project/cogs/          # Bot functionality modules
├── .env.example          # Environment configuration template
├── TODO.md              # Future enhancements
├── CONTRIBUTING.md      # Development guidelines
└── .gitmessage         # Commit message template
```