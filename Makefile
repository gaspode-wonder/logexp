# =============================================================================
# LogExp Makefile
# Deterministic developer workflows for Flask, testing, linting, typing, and CI parity
# =============================================================================

PYTHON := python3
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

# =============================================================================
# Application Development
# =============================================================================

dev: ## Run Flask locally with correct environment variables
    @echo ">>> Starting Flask development server..."
    $(ACTIVATE) && \
        export FLASK_APP=logexp.app:create_app && \
        export FLASK_ENV=development && \
        flask run --reload

# =============================================================================
# Linting, Formatting, Typing
# =============================================================================

lint: ## Run flake8 + black + isort + mypy
    @echo ">>> Running flake8..."
    $(ACTIVATE) && flake8 logexp

    @echo ">>> Running black..."
    $(ACTIVATE) && black --check logexp

    @echo ">>> Running isort..."
    $(ACTIVATE) && isort --check-only logexp

    @echo ">>> Running mypy..."
    $(ACTIVATE) && mypy logexp

format: ## Auto-format code with black + isort
    @echo ">>> Running black..."
    $(ACTIVATE) && black logexp

    @echo ">>> Running isort..."
    $(ACTIVATE) && isort logexp

check-format: ## Verify formatting without modifying files
    $(ACTIVATE) && black --check .
    $(ACTIVATE) && isort --check-only .

check-lint: ## Run flake8 in CI-style fail-on-error mode
    $(ACTIVATE) && flake8 .

check-mypy: ## Run mypy in strict CI mode
    $(ACTIVATE) && mypy --strict logexp

typecheck: ## Run mypy using project configuration
    $(ACTIVATE) && mypy .

# =============================================================================
# Database Management
# =============================================================================

db-reset: ## Drop + recreate + migrate the development database
    @echo ">>> Resetting development database..."
    rm -f logexp/app/data/readings.db
    $(ACTIVATE) && flask db upgrade

test-db: ## Rebuild the test database schema
    @echo ">>> Rebuilding the test database..."
    $(ACTIVATE) && PYTHONPATH=. python scripts/rebuild_test_db.py

# =============================================================================
# Testing & CI Parity
# =============================================================================

ci-local: ## Mirror GitHub Actions locally
    @echo ">>> Running CI-local workflow..."
    $(ACTIVATE) && \
        pip install --upgrade pip && \
        pip install -r requirements.txt && \
        mypy . && \
        pytest -vv

test-clean: ## Clean environment and run tests in a fresh state
    @echo ">>> Cleaning Python bytecode caches..."
    find logexp -type d -name "__pycache__" -exec rm -rf {} +

    @echo ">>> Cleaning untracked files (git clean -xdf)..."
    git clean -xdf

    @echo ">>> Rebuilding test database..."
    $(MAKE) test-db

    @echo ">>> Running pytest..."
    $(ACTIVATE) && pytest -vv

test-architecture: ## Run architecture-level tests only
    $(ACTIVATE) && pytest tests/architecture -q

test-smart: ## Run pytest in fail-fast / last-failed mode
    $(ACTIVATE) && pytest --lf --ff -q

# =============================================================================
# Developer Utilities
# =============================================================================

help: ## Show this help message
    @echo ""
    @echo "Available commands:"
    @echo ""
    @grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
    @echo ""

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

shell: ## Open Flask shell with app context
    $(ACTIVATE) && \
        export FLASK_APP=logexp.app:create_app && \
        flask shell

db-migrate: ## Create a new database migration
    $(ACTIVATE) && \
        export FLASK_APP=logexp.app:create_app && \
        flask db migrate

db-upgrade: ## Apply database migrations
    $(ACTIVATE) && \
        export FLASK_APP=logexp.app:create_app && \
        flask db upgrade

check-env: ## Validate required environment variables for parity with CI
    @echo ">>> Checking environment variable parity..."
    $(ACTIVATE) && python scripts/check_env_parity.py

# =============================================================================
# Logging & Analytics Utilities
# =============================================================================

log-demo: ## Emit a single structured log line for debugging logging setup
    $(ACTIVATE) && PYTHONPATH=. python scripts/log_demo.py

analytics-demo: ## Run analytics demo script
    $(ACTIVATE) && PYTHONPATH=. python scripts/analytics_demo.py
