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
	PYTHONPATH=project black project/ --line-length 88
	PYTHONPATH=project isort project/ --profile black

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

check-ci: ## Run CI-critical checks (must pass before push)
	@echo "🔍 Running CI-critical syntax checks..."
	PYTHONPATH=project flake8 project/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "✅ CI checks passed!"

check-format: ## Check if code needs formatting
	PYTHONPATH=project black project/ --check --line-length 88
	PYTHONPATH=project isort project/ --profile black --check-only

pre-push: check-ci check-format ## Run all pre-push checks
	@echo "🚀 Ready to push!"

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

# Database commands
db-start: ## Start PostgreSQL database
	./scripts/db-manage.sh start

db-stop: ## Stop PostgreSQL database
	./scripts/db-manage.sh stop

db-restart: ## Restart PostgreSQL database
	./scripts/db-manage.sh restart

db-reset: ## Reset database (⚠️ deletes all data)
	./scripts/db-manage.sh reset

db-init: ## Initialize database tables
	./scripts/db-manage.sh init

db-psql: ## Open PostgreSQL session
	./scripts/db-manage.sh psql

db-logs: ## Show database logs
	./scripts/db-manage.sh logs

db-status: ## Show database status
	./scripts/db-manage.sh status

db-pgadmin: ## Start pgAdmin web interface
	./scripts/db-manage.sh pgadmin

test-db: ## Run database tests only
	PYTHONPATH=project pytest tests/database/ -v

dev-setup: db-start db-init ## Complete development setup with database
	@echo "✅ Development environment with database ready!"