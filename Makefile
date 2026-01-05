# =============================================================================
# LogExp Makefile
# Deterministic developer workflows with colorized output, timing, and CI parity
# =============================================================================

PYTHON := python3
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

# Resolve site-packages path for the active venv (version‑agnostic)
SITE_PACKAGES := $(shell $(PYTHON) -c "import site; print(site.getsitepackages()[0])")

# ANSI Colors
GREEN := \033[1;32m
BLUE := \033[1;34m
YELLOW := \033[1;33m
RED := \033[1;31m
RESET := \033[0m

# Timing wrapper
define timed
	@start=$$(date +%s); \
	echo -e "$(BLUE)>>> $(1)...$(RESET)"; \
	{ $(2); }; \
	status=$$?; \
	end=$$(date +%s); \
	elapsed=$$((end - start)); \
	if [ $$status -eq 0 ]; then \
		echo -e "$(GREEN)✔ Completed in $${elapsed}s$(RESET)"; \
	else \
		echo -e "$(RED)✘ Failed in $${elapsed}s (exit $$status)$(RESET)"; \
	fi; \
	exit $$status
endef

# =============================================================================
# Bootstrap & CI Parity
# =============================================================================

bootstrap: ## Onboard a new maintainer with a fresh environment
	$(call timed,"Bootstrapping development environment", \
		$(PYTHON) -m venv $(VENV) && \
		$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt && \
		echo "/Users/jebbaugh/git/personal/active/logexp" > $(SITE_PACKAGES)/logexp.pth && \
		PYTHONPATH=. python scripts/ci_diagnostics.py \
	)

ci: ## Mirror GitHub Actions core lane (fast, no nuking)
	$(call timed,"CI: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)
	$(call timed,"CI: Environment parity check", $(ACTIVATE) && PYTHONPATH=. python scripts/check_env_parity.py)
	$(call timed,"CI: Diagnostics", $(ACTIVATE) && PYTHONPATH=. python scripts/ci_diagnostics.py)
	$(call timed,"CI: Database migrations", $(ACTIVATE) && PYTHONPATH=. FLASK_APP=logexp.app:create_app SQLALCHEMY_DATABASE_URI=sqlite:///ci.db flask db upgrade)
	$(call timed,"CI: Running pytest", $(ACTIVATE) && PYTHONPATH=. SQLALCHEMY_DATABASE_URI=sqlite:///ci.db pytest -vv)

ci-local: ci ## Alias for CI parity

ci-clean: ## CI with clean workspace and fresh venv (no lint/typing gates)
	$(call timed,"CI-CLEAN: git clean -xdf", git clean -xdf)
	$(call timed,"CI-CLEAN: Removing virtual environment", rm -rf $(VENV))
	$(call timed,"CI-CLEAN: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI-CLEAN: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)
	$(call timed,"CI-CLEAN: Environment parity check", $(ACTIVATE) && PYTHONPATH=. python scripts/check_env_parity.py)
	$(call timed,"CI-CLEAN: Diagnostics", $(ACTIVATE) && PYTHONPATH=. python scripts/ci_diagnostics.py)
	$(call timed,"CI-CLEAN: Database migrations", $(ACTIVATE) && PYTHONPATH=. FLASK_APP=logexp.app:create_app SQLALCHEMY_DATABASE_URI=sqlite:///ci.db flask db upgrade)
	$(call timed,"CI-CLEAN: Running pytest", $(ACTIVATE) && PYTHONPATH=. SQLALCHEMY_DATABASE_URI=sqlite:///ci.db pytest -vv)

# =============================================================================
# CI-HARD — Full clean-room CI with strict gates
# =============================================================================

ci-hard: ## Full clean-room CI: nuked workspace + strict lint/typing + full pytest
	$(call timed,"CI-HARD: git clean -xdf", git clean -xdf)
	$(call timed,"CI-HARD: Removing virtual environment", rm -rf $(VENV))
	$(call timed,"CI-HARD: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI-HARD: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)

	$(call timed,"CI-HARD: Environment parity check", \
		export ANALYTICS_ENABLED=true && \
		export ANALYTICS_WINDOW_SECONDS=60 && \
		export LOCAL_TIMEZONE=UTC && \
		$(ACTIVATE) && PYTHONPATH=. python scripts/check_env_parity.py \
	)

	$(call timed,"CI-HARD: Diagnostics", \
		export ANALYTICS_ENABLED=true && \
		export ANALYTICS_WINDOW_SECONDS=60 && \
		export LOCAL_TIMEZONE=UTC && \
		$(ACTIVATE) && PYTHONPATH=. python scripts/ci_diagnostics.py \
	)

	$(call timed,"CI-HARD: Database migrations", \
		export ANALYTICS_ENABLED=true && \
		export ANALYTICS_WINDOW_SECONDS=60 && \
		export LOCAL_TIMEZONE=UTC && \
		$(ACTIVATE) && FLASK_APP=logexp.app:create_app SQLALCHEMY_DATABASE_URI=sqlite:///ci.db flask db upgrade \
	)

	$(call timed,"CI-HARD: Ruff lint", $(ACTIVATE) && ruff check .)
	$(call timed,"CI-HARD: Black format check", $(ACTIVATE) && black --check .)
	$(call timed,"CI-HARD: Mypy strict typecheck", $(ACTIVATE) && mypy --strict .)

	$(call timed,"CI-HARD: Running pytest", \
		export ANALYTICS_ENABLED=true && \
		export ANALYTICS_WINDOW_SECONDS=60 && \
		export LOCAL_TIMEZONE=UTC && \
		$(ACTIVATE) && PYTHONPATH=. SQLALCHEMY_DATABASE_URI=sqlite:///ci.db pytest -vv \
	)

# =============================================================================
# Application Development
# =============================================================================

dev: ## Run Flask with full environment setup
	$(call timed,"Starting Flask development server", \
		$(ACTIVATE) && \
		export FLASK_APP=logexp.app:create_app && \
		export FLASK_ENV=development && \
		flask run --reload \
	)

dev-fast: ## Run Flask quickly assuming venv already exists
	$(call timed,"Starting Flask (fast mode)", \
		$(ACTIVATE) && FLASK_APP=logexp.app:create_app flask run --reload \
	)

shell: ## Open Flask shell with app context
	$(call timed,"Opening Flask shell", \
		$(ACTIVATE) && FLASK_APP=logexp.app:create_app flask shell \
	)

# =============================================================================
# Linting, Formatting, Typing
# =============================================================================

lint:
	$(call timed,"flake8", $(ACTIVATE) && flake8 logexp)
	$(call timed,"black --check", $(ACTIVATE) && black --check logexp)
	$(call timed,"isort --check-only", $(ACTIVATE) && isort --check-only logexp)
	$(call timed,"mypy", $(ACTIVATE) && mypy logexp)

format:
	$(call timed,"black", $(ACTIVATE) && black logexp)
	$(call timed,"isort", $(ACTIVATE) && isort logexp)

check-format:
	$(call timed,"black --check", $(ACTIVATE) && black --check .)
	$(call timed,"isort --check-only", $(ACTIVATE) && isort --check-only .)

check-lint:
	$(call timed,"flake8", $(ACTIVATE) && flake8 .)

check-mypy:
	$(call timed,"mypy --strict", $(ACTIVATE) && mypy --strict logexp)

typecheck:
	$(call timed,"mypy", $(ACTIVATE) && mypy .)

# =============================================================================
# Database Management
# =============================================================================

db-reset:
	$(call timed,"Resetting development DB", \
		rm -f logexp/app/data/readings.db && \
		$(ACTIVATE) && FLASK_APP=logexp.app:create_app flask db upgrade \
	)

test-db:
	$(call timed,"Rebuilding test DB", \
		$(ACTIVATE) && PYTHONPATH=. python scripts/rebuild_test_db.py \
	)

db-migrate:
	$(call timed,"Creating migration", \
		$(ACTIVATE) && FLASK_APP=logexp.app:create_app flask db migrate \
	)

db-upgrade:
	$(call timed,"Applying migrations", \
		$(ACTIVATE) && FLASK_APP=logexp.app:create_app flask db upgrade \
	)

# =============================================================================
# Testing
# =============================================================================

test-clean:
	$(call timed,"Cleaning __pycache__", find logexp -type d -name "__pycache__" -exec rm -rf {} +)
	$(call timed,"git clean -xdf", git clean -xdf)
	$(call timed,"Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)
	$(call timed,"Creating logexp.pth", echo "/Users/jebbaugh/git/personal/active/logexp" > $(SITE_PACKAGES)/logexp.pth)
	$(call timed,"Rebuilding test DB", $(ACTIVATE) && PYTHONPATH=. python scripts/rebuild_test_db.py)
	$(call timed,"Running pytest", $(ACTIVATE) && PYTHONPATH=. pytest -vv)

test-architecture:
	$(call timed,"Architecture tests", $(ACTIVATE) && pytest tests/architecture -q)

test-smart:
	$(call timed,"Smart pytest", $(ACTIVATE) && pytest --lf --ff -q)

# =============================================================================
# Developer Utilities
# =============================================================================

doctor:
	$(call timed,"Doctor checks", \
		$(PYTHON) --version && \
		(test -d $(VENV) && echo "Venv OK" || echo "Venv missing") && \
		$(ACTIVATE) && python -c "import flask; print('Flask OK')" && \
		(if lsof -i :5000 >/dev/null 2>&1; then echo 'Port 5000 in use'; else echo 'Port 5000 free'; fi) && \
		(test -f logexp/app/data/readings.db && echo "DB exists" || echo "DB missing") \
	)

check-env:
	$(call timed,"Environment parity", $(ACTIVATE) && python scripts/check_env_parity.py)

log-demo:
	$(call timed,"Log demo", $(ACTIVATE) && PYTHONPATH=. python scripts/log_demo.py)

analytics-demo:
	$(call timed,"Analytics demo", $(ACTIVATE) && PYTHONPATH=. python scripts/analytics_demo.py)

help:
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""

test-all: ## Run linting, typing, and full test suite
	$(call timed,"Ruff lint", $(ACTIVATE) && ruff check .)
	$(call timed,"Black format check", $(ACTIVATE) && black --check .)
	$(call timed,"Mypy strict typecheck", $(ACTIVATE) && mypy --strict .)
	$(call timed,"Pytest full suite", $(ACTIVATE) && pytest -vv)

	@echo ""
	@echo "$(YELLOW)Reminder: run 'v' to activate your environment$(RESET)"
	@echo ""
