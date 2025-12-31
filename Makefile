# =============================================================================
# LogExp Makefile
# Deterministic developer workflows for Flask, testing, linting, and CI parity
# =============================================================================

PYTHON := python3
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

# =============================================================================
# Application Development
# =============================================================================

# ---------------------------------------------------------------------------
# dev: Run Flask locally with correct environment variables
# ---------------------------------------------------------------------------
dev: ## Run Flask locally with correct environment variables
	@echo ">>> Starting Flask development server..."
	$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		export FLASK_ENV=development && \
		flask run --reload

# =============================================================================
# Linting & Formatting
# =============================================================================

# ---------------------------------------------------------------------------
# lint: Run flake8 + black + isort
# ---------------------------------------------------------------------------
lint: ## Run flake8 + black + isort
	@echo ">>> Running flake8..."
	$(ACTIVATE) && flake8 logexp

	@echo ">>> Running black..."
	$(ACTIVATE) && black --check logexp

	@echo ">>> Running isort..."
	$(ACTIVATE) && isort --check-only logexp

# ---------------------------------------------------------------------------
# format: Auto-format code with black + isort
# ---------------------------------------------------------------------------
format: ## Auto-format code
	@echo ">>> Running black..."
	$(ACTIVATE) && black logexp

	@echo ">>> Running isort..."
	$(ACTIVATE) && isort logexp

# =============================================================================
# Database Management
# =============================================================================

# ---------------------------------------------------------------------------
# db-reset: Drop + recreate + migrate the database
# ---------------------------------------------------------------------------
db-reset: ## Drop + recreate + migrate the development database
	@echo ">>> Resetting development database..."
	rm -f logexp/app/data/readings.db
	$(ACTIVATE) && flask db upgrade

# ---------------------------------------------------------------------------
# test-db: Rebuild the test database schema
# ---------------------------------------------------------------------------
test-db: ## Rebuild the test database schema
	@echo ">>> Rebuilding the test database..."
	$(ACTIVATE) && PYTHONPATH=. python scripts/rebuild_test_db.py

# =============================================================================
# Testing & CI Parity
# =============================================================================

# ---------------------------------------------------------------------------
# ci-local: Mirror GitHub Actions locally
# ---------------------------------------------------------------------------
ci-local: ## Mirror GitHub Actions locally
	@echo ">>> Running CI-local workflow..."
	$(ACTIVATE) && \
		pip install --upgrade pip && \
		pip install -r requirements.txt && \
		pytest -vv

# ---------------------------------------------------------------------------
# test-clean: Reproduce CI locally with a fully clean environment
# ---------------------------------------------------------------------------
test-clean: ## Clean environment and run tests in a fresh state
	@echo ">>> Cleaning Python bytecode caches..."
	find logexp -type d -name "__pycache__" -exec rm -rf {} +

	@echo ">>> Cleaning untracked files (git clean -xdf)..."
	git clean -xdf

	@echo ">>> Rebuilding test database..."
	$(MAKE) test-db

	@echo ">>> Running pytest..."
	$(ACTIVATE) && pytest -vv

# =============================================================================
# Developer Utilities
# =============================================================================

# ---------------------------------------------------------------------------
# help: List all available Make targets with descriptions
# ---------------------------------------------------------------------------
help: ## Show this help message
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

# ---------------------------------------------------------------------------
# check-env: Validate required environment variables for parity with CI
# ---------------------------------------------------------------------------
check-env: ## Validate required environment variables for parity with CI
	@echo ">>> Checking environment variable parity..."
	@python scripts/check_env_parity.py

# -------------------------------------------------------------------
# LOGGING UTILITIES
#
# log-demo:
#   Runs a minimal application instance using explicit config overrides
#   and emits a single structured JSON log line. This is the fastest way
#   for any maintainer to verify that:
#     - Structured logging is wired correctly
#     - UTC timestamps are being produced
#     - app.logger is isolated (root logger untouched)
#     - pytest/caplog compatibility remains intact
#
#   Implementation lives in: scripts/log_demo.py
# -------------------------------------------------------------------
log-demo:
	@PYTHONPATH=. python scripts/log_demo.py

log-demo:
	@PYTHONPATH=. python scripts/log_demo.py

.PHONY: analytics-demo

analytics-demo:
	PYTHONPATH=. python scripts/analytics_demo.py

# ==============================================================================
# Formatting & Linting (Step 10A)
#
# These targets provide a consistent, repo‑wide formatting and linting workflow.
# - `make format`      applies Black and isort to rewrite files in place
# - `make lint`        runs flake8 with bugbear and import‑order checks
# - `make check-format` verifies formatting without modifying files
# - `make check-lint`  runs linting in CI‑style "fail on error" mode
#
# All tools are configured for:
#   - 100‑character line length
#   - Black‑compatible flake8 rules (E203, W503 ignored)
#   - Google‑style import ordering via isort + flake8‑import‑order
#
# These targets are mechanical and must never change runtime behavior.
# They exist to ensure deterministic formatting, predictable diffs,
# and a clean CI pipeline.
# ==============================================================================
format:
	black .
	isort .

lint:
	flake8 .

check-format:
	black --check .
	isort --check-only .

check-lint:
	flake8 .
