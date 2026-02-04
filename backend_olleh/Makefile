.PHONY: help m mm run check shell superuser collectstatic test migrations migrate runserver seed typecheck typefix format lint

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
MANAGE := $(PYTHON) manage.py

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

m: ## Run migrations
	$(MANAGE) migrate

mm: ## Make migrations
	$(MANAGE) makemigrations

run: ## Run development server
	$(MANAGE) runserver

check: ## Check Django project for issues
	$(MANAGE) check

shell: ## Open Django shell
	$(MANAGE) shell

superuser: ## Create superuser
	$(MANAGE) createsuperuser

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

test: ## Run tests
	$(MANAGE) test

seed: ## Seed initial data (groups)
	$(MANAGE) seed_groups

typecheck: ## Run type checker (ty)
	uv run ty check

typefix: ## Run type checker with verbose output (ty)
	uv run ty check -v

format: ## Format code with ruff
	uv run ruff format .

lint: ## Lint code with ruff
	uv run ruff check .

# Aliases
migrations: mm ## Alias for mm
migrate: m ## Alias for m
runserver: run ## Alias for run
