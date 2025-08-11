# Development Guidelines

## Code Quality Standards
- ALWAYS run `make check-ci` before any commit/push
- Apply `make format` if formatting issues exist
- Never push code that fails CI syntax checks
- Use conventional commit messages (feat:, fix:, docs:, etc.)
- Run security checks for sensitive data handling
- Remove obsolete files proactively when identified

## Security-First Approach
- All sensitive data MUST be encrypted (warnings, user info)
- Use hashed identifiers for Discord IDs (SHA-256 + salt + pepper)
- Never log sensitive data in plain text
- Check for hardcoded secrets before push
- Validate all user inputs before database operations

## Available Tools (Always Use These!)

### Database Management
```bash
./scripts/db-manage.sh start     # Start PostgreSQL
./scripts/db-manage.sh init      # Initialize tables
./scripts/db-manage.sh reset     # Reset database (deletes data)
./scripts/db-manage.sh psql      # Open PostgreSQL session
```

### Git Workflow
```bash
./scripts/new-branch.sh feat "description"    # Create new branch
./scripts/cleanup-branches.sh                 # Clean merged branches
./scripts/verify-setup.sh                     # Verify dev environment
```

### Quality Checks
```bash
make check-ci          # CI-critical syntax checks
make pre-push          # Full pre-push validation
make format            # Format code (black + isort)
make check-security    # Security scanning
make test-db           # Database tests only
```

## Development Workflow
1. Focus on foundation completion before adding features
2. Test changes locally before pushing
3. Create logical, focused commits with clear messages
4. Use our scripts instead of manual commands
5. Clean up obsolete files when identified
6. Document architectural decisions

## Communication & Collaboration
- Be concise and actionable
- Provide clear next steps
- When you say "continue" - proceed with current task
- When CI issues mentioned - fix immediately
- Technical decisions: I can make recommendations
- Architecture changes: Always discuss first