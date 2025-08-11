# Quality Checks Protocol

## Pre-Push Checklist

Before any push or commit, ALWAYS run these checks locally:

### 1. Critical Syntax Check (CI Blocker)
```bash
flake8 project/ --count --select=E9,F63,F7,F82 --show-source --statistics
```
**Must return 0 errors** - This is what CI checks first

### 2. Code Formatting
```bash
black project/ --line-length 88 --check
isort project/ --profile black --check-only
```

### 3. Full Linting (Optional but Recommended)
```bash
flake8 project/ --count --statistics
```

### 4. Type Checking
```bash
mypy project/ --ignore-missing-imports
```

### 5. Tests
```bash
python -m pytest tests/ -v
```

## Quick Fix Commands

If checks fail, run these to fix:

```bash
# Fix formatting
black project/ --line-length 88
isort project/ --profile black

# Check syntax again
flake8 project/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Makefile Integration

Add to Makefile for easy use:
```makefile
check-ci: ## Run CI-critical checks locally
	flake8 project/ --count --select=E9,F63,F7,F82 --show-source --statistics

format: ## Format code
	black project/ --line-length 88
	isort project/ --profile black

check: format check-ci ## Full quality check
	flake8 project/ --count --statistics
	mypy project/ --ignore-missing-imports

test: ## Run tests
	python -m pytest tests/ -v
```

## Rule: Never Push Without check-ci Passing

Always run `make check-ci` before any push to avoid CI failures.