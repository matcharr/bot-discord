# Development Hooks Setup Guide

This directory contains hook configurations that automate your development workflow and enforce quality standards.

## Quick Setup

1. **Open Kiro Hook UI**: Use Command Palette → "Open Kiro Hook UI"
2. **Import hooks**: Load the hook configurations from this directory
3. **Enable recommended hooks**: Start with Auto Quality Check and Pre-Commit Validation

## Hook Categories

### 🔄 Automatic Hooks (Recommended)
- **auto-quality-check.md**: Runs quality checks on Python file saves
- **pre-commit-validation.md**: Validates code before commits
- **database-sync.md**: Syncs database when models change
- **dependency-update.md**: Updates dependencies when requirements change

### 🔘 Manual Hooks (On-Demand)
- **branch-cleanup.md**: Clean merged branches (button click)
- **security-audit.md**: Comprehensive security scan (button click)

## Benefits of Hook-Driven Development

### Before Hooks (Manual Process)
```bash
# Every time you save a Python file:
make check-ci
make format
make check-security

# Before every commit:
make pre-push
make test-db

# When requirements change:
make install

# Regular maintenance:
./scripts/cleanup-branches.sh
make check-security
```

### After Hooks (Automated Process)
```bash
# Just save your Python files → Everything runs automatically
# Just commit → Pre-commit validation runs automatically
# Just update requirements.txt → Dependencies install automatically
# Just click hook buttons for maintenance tasks
```

## Productivity Impact

- **Time Saved**: ~15-20 commands per day automated
- **Quality Improved**: Catches issues immediately, not at commit time
- **Consistency**: Same checks run every time, no human error
- **Focus**: Spend time coding, not running maintenance commands

## Getting Started

1. Enable **Auto Quality Check** first (most impactful)
2. Add **Pre-Commit Validation** (prevents broken commits)
3. Enable **Database Sync** if working with database models
4. Add manual hooks as needed for maintenance tasks

## Customization

Each hook configuration can be modified to fit your specific needs. The JSON configurations in each file can be imported directly into Kiro's hook system.
