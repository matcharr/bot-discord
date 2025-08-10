.PHONY: help install format lint test clean setup git-setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and pre-commit hooks
	pip install -r project/requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

setup: install git-setup ## Complete development setup
	@echo "✅ Development environment ready!"

git-setup: ## Setup Git hooks and workflow tools
	./scripts/setup-git-hooks.sh

format: ## Format code with black and isort
	PYTHONPATH=project black project/
	PYTHONPATH=project isort project/

lint: ## Run linting checks
	PYTHONPATH=project flake8 project/
	PYTHONPATH=project mypy project/ --ignore-missing-imports || true

test: ## Run tests with coverage
	PYTHONPATH=project pytest tests/ -v --cov=project/ --cov-report=xml --cov-report=html

test-fast: ## Run tests without coverage
	PYTHONPATH=project pytest tests/ -v

clean: ## Clean up cache and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache htmlcov .coverage coverage.xml

check: format lint ## Format and lint code

run: ## Run the bot locally
	python run.py

new-branch: ## Create a new branch (usage: make new-branch TYPE=feat DESC="description")
	@if [ -z "$(TYPE)" ] || [ -z "$(DESC)" ]; then \
		echo "Usage: make new-branch TYPE=feat DESC=\"your-description\""; \
		echo "Types: feat, fix, chore, docs, refactor, test"; \
	else \
		./scripts/new-branch.sh $(TYPE) "$(DESC)"; \
	fi

cleanup-branches: ## Clean up merged branches
	./scripts/cleanup-branches.sh