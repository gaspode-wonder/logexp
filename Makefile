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
dev:
	@echo ">>> Starting Flask development server..."
	$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		export FLASK_ENV=development && \
		flask run --reload

# ---------------------------------------------------------------------------
# lint: Run flake8 + black + isort
# ---------------------------------------------------------------------------
lint:
	@echo ">>> Running flake8..."
	$(ACTIVATE) && flake8 logexp

	@echo ">>> Running black..."
	$(ACTIVATE) && black --check logexp

	@echo ">>> Running isort..."
	$(ACTIVATE) && isort --check-only logexp

# ---------------------------------------------------------------------------
# db-reset: Drop + recreate + migrate the database
# ---------------------------------------------------------------------------
db-reset:
	@echo ">>> Resetting database..."
	rm -f logexp/app/data/readings.db
	$(ACTIVATE) && flask db upgrade

# ---------------------------------------------------------------------------
# ci-local: Mirror GitHub Actions locally
# ---------------------------------------------------------------------------
ci-local:
	@echo ">>> Running CI-local workflow..."
	$(ACTIVATE) && \
		pip install --upgrade pip && \
		pip install -r requirements.txt && \
		pytest -vv

# ---------------------------------------------------------------------------
# test-clean: Reproduce CI locally with a fully clean environment
# ---------------------------------------------------------------------------
test-clean:
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
