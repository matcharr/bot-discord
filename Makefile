.PHONY: help install format lint test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and pre-commit hooks
	pip install -r project/requirements.txt
	pip install black isort flake8 mypy pre-commit
	pre-commit install

format: ## Format code with black and isort
	black project/
	isort project/

lint: ## Run linting checks
	flake8 project/
	mypy project/

test: ## Run tests
	pytest tests/ -v --cov=project/

clean: ## Clean up cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

check: format lint ## Format and lint code

run: ## Run the bot locally
	cd project && python main.py

dev: ## Run in development mode with auto-reload
	cd project && python -m watchdog.observers main.py