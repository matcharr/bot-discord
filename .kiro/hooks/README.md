# Development Hooks Setup Guide

This directory contains hook configurations that automate your development workflow and enforce quality standards.

## Quick Setup

1. **Open Kiro Hook UI**: Use Command Palette → "Open Kiro Hook UI"
2. **Import hooks**: Load the hook configurations from this directory
3. **Enable recommended hooks**: Start with Auto Quality Check and Pre-Commit Validation

## Hook Categories

### 🔄 Automatic Hooks (Recommended)
- **python-quality-check.kiro.hook**: Runs quality checks on Python file saves
- **requirements-sync-hook.kiro.hook**: Updates dependencies when requirements change

### 🔘 Manual Hooks (On-Demand)
- **git-cleanup-button.kiro.hook**: Clean merged branches (button click)
- **security-audit-button.kiro.hook**: Comprehensive security scan (button click)

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

1. Enable **Python Quality Check** first (most impactful - auto-formats on save)
2. Add **Requirements Sync** (auto-installs dependencies)
3. Use manual hooks as needed for maintenance tasks

**Note**: Pre-commit validation is handled by the existing `.pre-commit-config.yaml` setup, not hooks.

## Customization

Each hook configuration can be modified to fit your specific needs. The JSON configurations in each file can be imported directly into Kiro's hook system.
