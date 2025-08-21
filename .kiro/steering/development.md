# Development Guidelines

**Current Focus**: Development environment setup and workflow optimization. No production deployment yet.

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

### Automated Hooks (Current Setup)
- **Python Quality Check**: Runs on Python file save (formatting + CI checks)
- **Requirements Sync**: Auto-installs when requirements.txt changes
- **Security Audit**: Runs when security-sensitive files are modified
- **Pre-Commit Validation**: Handled by `.pre-commit-config.yaml` (not Kiro hooks)

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
- Always backup before destructive operations
- Use migrations for schema changes (production readiness for future)

### Git Workflow (Partially Automated)
```bash
./scripts/new-branch.sh feat "description"    # Create new branch
./scripts/cleanup-branches.sh                 # Clean merged branches (manual)
./scripts/verify-setup.sh                     # Verify dev environment
```

### Quality Checks (Mostly Automated)
```bash
# make check-ci          # Auto-runs on file save via hook
# make format            # Auto-runs on file save via hook
# make check-security    # Auto-runs when security files change via hook
make test-db           # Manual (run when needed)
make test              # Full test suite (manual)
# make install           # Auto-runs when requirements change via hook
```

## Development Workflow (Hook-Enhanced)
1. Focus on foundation completion before adding features
2. **Automated**: Quality checks run on file save, tests run on relevant changes
3. **Automated**: Pre-commit hook ensures quality before commits
4. **Automated**: Use hooks for repetitive tasks, scripts for complex operations
5. **Manual**: Clean up obsolete files when identified (use `make cleanup-branches`)
6. Document architectural decisions

### Hook-Driven Development
- Save Python files → Auto quality check + formatting
- Update requirements → Auto dependency installation
- Modify security files → Auto security audit
- Commit code → Pre-commit hooks validate (via .pre-commit-config.yaml)
- Need branch cleanup → Use `make cleanup-branches` or `./scripts/cleanup-branches.sh`
- Database operations → Manual via `./scripts/db-manage.sh` (safer)

## Communication & Collaboration
- Be concise and actionable
- Provide clear next steps
- When you say "continue" - proceed with current task
- When CI issues mentioned - fix immediately
- Technical decisions: I can make recommendations
- Architecture changes: Always discuss first
