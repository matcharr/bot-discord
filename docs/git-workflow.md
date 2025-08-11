# Git Workflow Guide

This document describes the standardized Git workflow for this project.

## 🌿 Branch Naming Convention

### Format
```
type/description-in-kebab-case
```

### Available Types
- `feat/` - New features
- `fix/` - Bug fixes
- `chore/` - Maintenance, dependencies, configuration
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Adding/modifying tests

### Examples
```bash
feat/discord-slash-commands
fix/memory-leak-moderation
chore/update-dependencies
docs/api-documentation
refactor/config-system
test/moderation-coverage
```

## 🚀 Creating a New Branch

### Automatic Method (Recommended)
```bash
./scripts/new-branch.sh feat "add-user-roles"
./scripts/new-branch.sh fix "memory-leak-issue"
```

### Manual Method
```bash
# 1. Switch to main and update
git checkout main
git pull origin main

# 2. Create the new branch
git checkout -b feat/my-new-feature
```

## 📝 Commit Convention

### Format
```
type(scope): description

body (optional)

footer (optional)
```

### Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting, style
- `refactor` - Refactoring
- `test` - Tests
- `chore` - Maintenance

### Examples
```bash
feat(auth): add user login functionality
fix(moderation): resolve memory leak in warning system
docs: update README with setup instructions
chore(deps): update discord.py to v2.3.2
```

## 🔄 Complete Workflow

### 1. Create a Branch
```bash
./scripts/new-branch.sh feat "my-feature"
```

### 2. Develop
```bash
# Make your changes
git add .
git commit -m "feat(scope): description"
```

### 3. Push and Create PR
```bash
git push -u origin feat/my-feature
# Create a Pull Request on GitHub
```

### 4. After Merge
```bash
git checkout main
git pull origin main
git branch -d feat/my-feature  # Delete local branch
```

## 🛡️ Git Hooks

### Active Hooks
- **commit-msg**: Validates commit message format
- **pre-push**: Validates branch names before push

### Enable Hooks
```bash
git config core.hooksPath .githooks
```

## 🚫 Forbidden Branches

These branch names are **forbidden**:
- `new-branch`
- `test-branch`
- `temp`
- `wip`
- Any name without type/ prefix

## 🧹 Branch Cleanup

### Automatic Script
```bash
./scripts/cleanup-branches.sh
```

### Manual Commands
```bash
# Clean remote references
git remote prune origin

# View merged local branches
git branch --merged main

# Delete merged local branches (except main)
git branch --merged main | grep -v "main" | xargs -n 1 git branch -d
```

## 💡 Tips

### Branch Names
- Use dashes, not underscores
- All lowercase
- Be descriptive but concise
- Avoid special characters

### Commit Messages
- Use imperative mood ("add" not "added")
- First line max 50 characters
- Be specific about scope
- Explain the "why" in the body if necessary

### Pull Requests
- Descriptive title
- Clear description of changes
- Link related issues
- Request review if necessary

### Regular Maintenance
- Clean branches after each merge
- Use `./scripts/cleanup-branches.sh` regularly
- Close obsolete Dependabot PRs on GitHub