# Development Guidelines

## Code Quality Standards (Automated via Hooks)
- **Auto Quality Check Hook**: Automatically runs `make check-ci` and `make format` on Python file saves
- **Pre-Commit Hook**: Validates all code before commits (blocks bad commits)
- Use conventional commit messages (feat:, fix:, docs:, etc.)
- **Security Audit Hook**: Regular automated security scanning
- Remove obsolete files proactively when identified

## CI Cost Optimization
- Fast CI runs on all changes (syntax + critical tests)
- Comprehensive CI runs only on code changes
- Documentation changes skip CI automatically
- Draft PRs skip CI to save costs
- Use dependency caching for faster runs

## Security-First Approach
- All sensitive data MUST be encrypted (warnings, user info)
- Use hashed identifiers for Discord IDs (SHA-256 + salt + pepper)
- Never log sensitive data in plain text
- Check for hardcoded secrets before push
- Validate all user inputs before database operations

## Available Tools & Automation

### Automated Hooks (Recommended Setup)
- **Auto Quality Check**: Runs on Python file save (formatting + CI checks)
- **Pre-Commit Validation**: Blocks commits that fail quality standards
- **Database Schema Check**: Validates schema changes with confirmation prompts (dev/test only, never auto-applies destructive changes)
- **Dependency Update**: Auto-installs when requirements.txt changes
- **Branch Cleanup**: Manual button to clean merged branches
- **Security Audit**: Manual/scheduled comprehensive security scan

### Virtual Environment
- **Automatic activation**: Virtual environment (.venv) auto-activates in project directory
- **All make commands**: Automatically use virtual environment Python 3.11.13
- **Dependency Hook**: Auto-updates when requirements change

### Database Management (Partially Automated)
```bash
./scripts/db-manage.sh start     # Start PostgreSQL
./scripts/db-manage.sh init      # Initialize tables (safe, creates only)
./scripts/db-manage.sh reset     # Reset database (⚠️ DELETES ALL DATA)
./scripts/db-manage.sh psql      # Open PostgreSQL session
```

**⚠️ Database Safety Rules:**
- Schema changes require explicit confirmation in dev/test environments
- Production schema changes are NEVER automated
- Always backup before destructive operations
- Use migrations for production schema changes

### Git Workflow (Partially Automated)
```bash
./scripts/new-branch.sh feat "description"    # Create new branch
# ./scripts/cleanup-branches.sh               # Now available as hook button
./scripts/verify-setup.sh                     # Verify dev environment
```

### Quality Checks (Mostly Automated)
```bash
# make check-ci          # Auto-runs on file save via hook
# make format            # Auto-runs on file save via hook
# make check-security    # Available as manual hook
make test-db           # Auto-runs when database files change
make test              # Full test suite (manual)
make install           # Auto-runs when requirements change
```

## Development Workflow (Hook-Enhanced)
1. Focus on foundation completion before adding features
2. **Automated**: Quality checks run on file save, tests run on relevant changes
3. **Automated**: Pre-commit hook ensures quality before commits
4. **Automated**: Use hooks for repetitive tasks, scripts for complex operations
5. **Manual**: Clean up obsolete files when identified (use Branch Cleanup hook)
6. Document architectural decisions

### Hook-Driven Development
- Save Python files → Auto quality check + formatting
- Modify database models → Schema validation + explicit confirmation for any changes (dev/test only, requires backup confirmation for destructive operations)
- Update requirements → Auto dependency installation
- Commit code → Auto validation (blocks bad commits)
- Need cleanup → Click Branch Cleanup hook button
- Security review → Click Security Audit hook button

## Communication & Collaboration
- Be concise and actionable
- Provide clear next steps
- When you say "continue" - proceed with current task
- When CI issues mentioned - fix immediately
- Technical decisions: I can make recommendations
- Architecture changes: Always discuss first
