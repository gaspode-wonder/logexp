# =============================================================================
# LogExp Makefile
# Deterministic developer workflows for Flask, testing, linting, and CI parity
# =============================================================================

PYTHON := python3
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

# ---------------------------------------------------------------------------
# dev: Run Flask locally with correct environment variables
# ---------------------------------------------------------------------------
dev: ## dev: Run Flask locally with correct environment variables
	@echo ">>> Starting Flask development server..."
	$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		export FLASK_ENV=development && \
		flask run --reload

# ---------------------------------------------------------------------------
# lint: Run flake8 + black + isort
# ---------------------------------------------------------------------------
lint: ## lint: Run flake8 + black + isort
	@echo ">>> Running flake8..."
	$(ACTIVATE) && flake8 logexp

	@echo ">>> Running black..."
	$(ACTIVATE) && black --check logexp

	@echo ">>> Running isort..."
	$(ACTIVATE) && isort --check-only logexp

# ---------------------------------------------------------------------------
# db-reset: Drop + recreate + migrate the database
# ---------------------------------------------------------------------------
db-reset: ## db-reset: Drop + recreate + migrate the database
	@echo ">>> Resetting database..."
	rm -f logexp/app/data/readings.db
	$(ACTIVATE) && flask db upgrade

# ---------------------------------------------------------------------------
# ci-local: Mirror GitHub Actions locally
# ---------------------------------------------------------------------------
ci-local: ## ci-local: Mirror GitHub Actions locally
	@echo ">>> Running CI-local workflow..."
	$(ACTIVATE) && \
		pip install --upgrade pip && \
		pip install -r requirements.txt && \
		pytest -vv

# ---------------------------------------------------------------------------
# test-clean: Reproduce CI locally with a fully clean environment
# ---------------------------------------------------------------------------
test-clean: ## test-clean: Reproduce CI locally with a fully clean environment
	@echo ">>> Removing virtual environment..."
	rm -rf $(VENV)

	@echo ">>> Removing Python bytecode caches..."
	find logexp -type d -name "__pycache__" -exec rm -rf {} +

	@echo ">>> Cleaning untracked files (git clean -xdf)..."
	git clean -xdf

	@echo ">>> Creating fresh virtual environment..."
	$(PYTHON) -m venv $(VENV)

	@echo ">>> Installing dependencies..."
	$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt

	@echo ">>> Running pytest in a clean environment..."
	$(ACTIVATE) && pytest -vv

# =============================================================================
# Developer Utilities
# =============================================================================

# ---------------------------------------------------------------------------
# help: List all available Make targets with descriptions
# ---------------------------------------------------------------------------
help:
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""

# ---------------------------------------------------------------------------
# doctor: Environment sanity checks (Python, venv, Flask, DB, ports)
# ---------------------------------------------------------------------------
doctor: ## Run environment sanity checks
	@echo ">>> Python version:"
	$(PYTHON) --version

	@echo ">>> Checking virtual environment..."
	@test -d $(VENV) && echo "Venv OK" || echo "Venv missing"

	@echo ">>> Checking Flask import..."
	$(ACTIVATE) && python -c "import flask; print('Flask OK')"

	@echo ">>> Checking for running processes on port 5000..."
	@if lsof -i :5000 >/dev/null 2>&1; then \
		echo 'Port 5000 is in use'; \
	else \
		echo 'Port 5000 is free'; \
	fi

	@echo ">>> Checking SQLite database..."
	@test -f logexp/app/data/readings.db && echo "DB exists" || echo "DB missing"

# ---------------------------------------------------------------------------
# format: Auto-format code with black + isort
# ---------------------------------------------------------------------------
format: ## Auto-format code
	@echo ">>> Running black..."
	$(ACTIVATE) && black logexp

	@echo ">>> Running isort..."
	$(ACTIVATE) && isort logexp

# ---------------------------------------------------------------------------
# shell: Flask shell with app context
# ---------------------------------------------------------------------------
shell: ## Open Flask shell with app context
	$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		flask shell

# ---------------------------------------------------------------------------
# db-migrate: Create a new Alembic migration
# ---------------------------------------------------------------------------
db-migrate: ## Create a new database migration
	$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		flask db migrate

# ---------------------------------------------------------------------------
# db-upgrade: Apply migrations
# ---------------------------------------------------------------------------
db-upgrade: ## Apply database migrations
	$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		flask db upgrade
