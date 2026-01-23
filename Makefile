# filename: Makefile — LogExp (canonical, deterministic)

PYTHON := python3.10
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

GREEN := \033[1;32m
BLUE := \033[1;34m
YELLOW := \033[1;33m
RED := \033[1;31m
RESET := \033[0m

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
# Bootstrap
# =============================================================================

bootstrap:
	$(call timed,"Bootstrapping development environment", \
		$(PYTHON) -m venv $(VENV) && \
		$(ACTIVATE) && pip install --upgrade pip && \
		pip install -e . && pip install -r requirements.txt && \
		PYTHONPATH=. python scripts/ci_diagnostics.py \
	)

# =============================================================================
# CI (standard)
# =============================================================================

ci:
	$(call timed,"CI: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -e . && pip install -r requirements.txt)
	$(call timed,"CI: Environment parity check", $(ACTIVATE) && PYTHONPATH=. python scripts/check_env_parity.py)
	$(call timed,"CI: Diagnostics", $(ACTIVATE) && PYTHONPATH=. python scripts/ci_diagnostics.py)
	$(call timed,"CI: Database migrations", \
		rm -f ci.db && \
		$(ACTIVATE) && \
		env \
			SQLALCHEMY_DATABASE_URI=sqlite:///ci.db \
			FLASK_APP=logexp.app:create_app \
			flask db upgrade \
	)
	$(call timed,"CI: Running pytest", \
		$(ACTIVATE) && \
		env \
			SQLALCHEMY_DATABASE_URI=sqlite:///ci.db \
			PYTHONPATH=. \
			pytest -vv \
	)

ci-local: ci

# =============================================================================
# CI-CLEAN
# =============================================================================

ci-clean:
	$(call timed,"CI-CLEAN: git clean -xdf", git clean -xdf)
	$(call timed,"CI-CLEAN: Removing Python bytecode caches", \
		find logexp -name "*.pyc" -delete && \
		find logexp -name "__pycache__" -type d -exec rm -rf {} + \
	)
	$(call timed,"CI-CLEAN: Removing virtual environment", rm -rf $(VENV))
	$(call timed,"CI-CLEAN: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI-CLEAN: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -e . && pip install -r requirements.txt)
	$(call timed,"CI-CLEAN: Environment parity check", $(ACTIVATE) && PYTHONPATH=. python scripts/check_env_parity.py)
	$(call timed,"CI-CLEAN: Diagnostics", $(ACTIVATE) && PYTHONPATH=. python scripts/ci_diagnostics.py)
	$(call timed,"CI-CLEAN: Database migrations", \
		rm -f ci.db && \
		$(ACTIVATE) && \
		env \
			SQLALCHEMY_DATABASE_URI=sqlite:///ci.db \
			FLASK_APP=logexp.app:create_app \
			flask db upgrade \
	)
	$(call timed,"CI-CLEAN: Running pytest", \
		$(ACTIVATE) && \
		env \
			SQLALCHEMY_DATABASE_URI=sqlite:///ci.db \
			PYTHONPATH=. \
			pytest -vv \
	)

# =============================================================================
# CI-HARD (canonical, deterministic)
# =============================================================================

ci-hard:
	$(call timed,"CI-HARD: git clean -xdf", git clean -xdf)
	$(call timed,"CI-HARD: Removing Python bytecode caches", \
		find logexp -name "*.pyc" -delete && \
		find logexp -name "__pycache__" -type d -exec rm -rf {} + \
	)
	$(call timed,"CI-HARD: Removing virtual environment", rm -rf $(VENV))
	$(call timed,"CI-HARD: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI-HARD: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -e . && pip install -r requirements.txt)

	$(call timed,"CI-HARD: Environment parity check", \
		$(ACTIVATE) && \
		env \
			LOCAL_TIMEZONE=UTC \
			PYTHONPATH=. \
			python scripts/check_env_parity.py \
	)

	$(call timed,"CI-HARD: Diagnostics", \
		$(ACTIVATE) && \
		env \
			LOCAL_TIMEZONE=UTC \
			PYTHONPATH=. \
			python scripts/ci_diagnostics.py \
	)

	$(call timed,"CI-HARD: Database migrations", \
		rm -f ci.db && \
		$(ACTIVATE) && \
		env \
			LOCAL_TIMEZONE=UTC \
			SQLALCHEMY_DATABASE_URI=sqlite:///ci.db \
			FLASK_APP=logexp.app:create_app \
			flask db upgrade \
	)

	$(call timed,"CI-HARD: Ruff lint", $(ACTIVATE) && ruff check .)
	$(call timed,"CI-HARD: Black format check", $(ACTIVATE) && black --check .)
	$(call timed,"CI-HARD: Mypy strict typecheck", $(ACTIVATE) && mypy --strict .)

	$(call timed,"CI-HARD: Running pytest", \
		$(ACTIVATE) && \
		env \
			LOCAL_TIMEZONE=UTC \
			SQLALCHEMY_DATABASE_URI=sqlite:///ci.db \
			PYTHONPATH=. \
			pytest -vv \
	)

# =============================================================================
# Development
# =============================================================================

dev:
	$(call timed,"Starting Flask development server", \
		$(ACTIVATE) && \
		env \
			FLASK_APP=logexp.app:create_app \
			FLASK_ENV=development \
			flask run --reload \
	)

dev-fast:
	$(call timed,"Starting Flask (fast mode)", \
		$(ACTIVATE) && \
		env FLASK_APP=logexp.app:create_app flask run --reload \
	)

shell:
	$(call timed,"Opening Flask shell", \
		$(ACTIVATE) && env FLASK_APP=logexp.app:create_app flask shell \
	)

# =============================================================================
# Database
# =============================================================================

db-reset:
	$(call timed,"Resetting development DB", \
		rm -f logexp/app/data/readings.db && \
		$(ACTIVATE) && env FLASK_APP=logexp.app:create_app flask db upgrade \
	)

test-db:
	$(call timed,"Rebuilding test DB", \
		$(ACTIVATE) && PYTHONPATH=. python scripts/rebuild_test_db.py \
	)

db-migrate:
	$(call timed,"Creating migration", \
		$(ACTIVATE) && env FLASK_APP=logexp.app:create_app flask db migrate \
	)

db-upgrade:
	$(call timed,"Applying migrations", \
		$(ACTIVATE) && env FLASK_APP=logexp.app:create_app flask db upgrade \
	)

# =============================================================================
# Testing
# =============================================================================

test-clean:
	$(call timed,"Cleaning __pycache__", find logexp -type d -name "__pycache__" -exec rm -rf {} +)
	$(call timed,"git clean -xdf", git clean -xdf)
	$(call timed,"Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -e . && pip install -r requirements.txt)
	$(call timed,"Rebuilding test DB", $(ACTIVATE) && PYTHONPATH=. python scripts/rebuild_test_db.py)
	$(call timed,"Running pytest", $(ACTIVATE) && PYTHONPATH=. pytest -vv)

test-architecture:
	$(call timed,"Architecture tests", $(ACTIVATE) && pytest tests/architecture -q)

test-smart:
	$(call timed,"Smart pytest", $(ACTIVATE) && pytest --lf --ff -q)

# =============================================================================
# Utilities
# =============================================================================

doctor:
	$(call timed,"Doctor checks", \
		$(PYTHON) --version && \
		(test -d $(VENV) && echo "Venv OK" || echo "Venv missing") && \
		$(ACTIVATE) && python -c "import flask; print('Flask OK')" && \
		(if lsof -i :5000 >/dev/null 2>&1; then echo 'Port 5000 in use'; else echo 'Port 5000 free'; fi) \
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

test-all:
	$(call timed,"Ruff lint", $(ACTIVATE) && ruff check .)
	$(call timed,"Black format check", $(ACTIVATE) && black --check .)
	$(call timed,"Mypy strict typecheck", $(ACTIVATE) && mypy --strict .)
	$(call timed,"Pytest full suite", $(ACTIVATE) && pytest -vv)

	@echo ""
	@echo "$(YELLOW)Reminder: run 'v' to activate your environment$(RESET)"
	@echo ""

.PHONY: update-snapshots
update-snapshots:
	pytest --snapshot-update
