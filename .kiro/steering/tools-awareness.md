# Available Tools & Scripts

## Our Custom Scripts (Always Use These!)

### Database Management
```bash
./scripts/db-manage.sh start     # Start PostgreSQL
./scripts/db-manage.sh stop      # Stop PostgreSQL  
./scripts/db-manage.sh reset     # Reset database (deletes data)
./scripts/db-manage.sh init      # Initialize tables
./scripts/db-manage.sh psql      # Open PostgreSQL session
./scripts/db-manage.sh status    # Check database status
./scripts/db-manage.sh logs      # View database logs
```

### Git Workflow
```bash
./scripts/new-branch.sh feat "description"    # Create new branch
./scripts/cleanup-branches.sh                 # Clean merged branches
./scripts/setup-git-hooks.sh                  # Setup git hooks
./scripts/verify-setup.sh                     # Verify dev environment
```

### Data Management
```bash
./scripts/seed-data.py           # Seed test data
./scripts/seed_test_data.py      # Additional test data
```

### Makefile Commands
```bash
make check-ci          # CI-critical syntax checks
make pre-push          # Full pre-push validation
make format            # Format code (black + isort)
make test              # Run tests with coverage
make test-db           # Database tests only
make db-start          # Start database
make new-branch        # Create branch (TYPE=feat DESC="...")
make cleanup-branches  # Clean branches
```

## File Cleanup Authority
- Remove obsolete files when identified
- Clean up temporary files after tasks complete
- Update .gitignore when removing file types
- Document removal in commit messages

## Environment Files
- `.env.development` - Development config (has encryption keys)
- `.env.test` - Test environment config
- `.env.example` - Template for new setups

## Testing Framework
- `tests/database/` - 26 comprehensive database tests
- Run with: `make test-db` or `python -m pytest tests/database/ -v`

## Development Workflow Integration
- Use our scripts instead of manual commands
- Leverage Makefile for common tasks
- Maintain our established patterns
- Extend tools when needed, don't recreate