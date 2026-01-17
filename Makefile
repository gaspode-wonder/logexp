# filename: Makefile
# =============================================================================
# LogExp Makefile — Docker-first, parallel to pi-log
# Deterministic developer workflows with CI parity and Ansible deployment
# =============================================================================

.PHONY: \
	bootstrap ci ci-hard test test-clean lint typecheck format format-check \
	guard-build-context \
	docker-build docker-build-no-cache image-export deploy-image \
	up-pi down image-pipeline \
	preflight provision pipeline deploy logs-pi restart db-shell \
	doctor inventory ping help

PYTHON := python3
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

ANSIBLE_PLAYBOOK_DEPLOY := ansible/playbooks/deploy-logexp.yml
ANSIBLE_PLAYBOOK_PROVISION := ansible/playbooks/provision-pi.yml
INVENTORY := ansible/inventory/hosts.ini

DOCKER_IMAGE := logexp:latest
DOCKERFILE := Dockerfile
BUILD_CONTEXT := .
COMPOSE_PI := docker-compose.pi.yml
IMAGE_TAR := logexp-image.tar

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
# Build Context Guard
# =============================================================================

guard-build-context: ## Ensure Docker build context is large enough (prevents accidental tiny builds)
	@size=$$(du -sk $(BUILD_CONTEXT) | cut -f1); \
	if [ $$size -lt 1024 ]; then \
		echo -e "$(RED)✘ Build context too small ($$size KB).$(RESET)"; \
		echo -e "$(RED)✘ You are building from the wrong directory.$(RESET)"; \
		echo -e "$(YELLOW)Hint: run make from the repo root (clean/).$(RESET)"; \
		exit 1; \
	fi; \
	echo -e "$(GREEN)✔ Build context OK ($$size KB).$(RESET)"

# =============================================================================
# Bootstrap & CI
# =============================================================================

bootstrap: ## Create venv and install development dependencies
	$(call timed,"Bootstrapping development environment", \
		$(PYTHON) -m venv $(VENV) && \
		$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt && \
		black --version \
	)

ci: ## Run full CI pipeline (venv + deps + black + pytest)
	$(call timed,"CI: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)
	$(call timed,"CI: Running Black", $(ACTIVATE) && black --check .)
	$(call timed,"CI: Running pytest", $(ACTIVATE) && pytest -vv)

ci-hard: ## Full clean-room CI: remove venv, recreate, install, format-check, lint, typecheck, pytest
	$(call timed,"CI-HARD: Removing existing venv", rm -rf $(VENV))
	$(call timed,"CI-HARD: Creating fresh venv", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI-HARD: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)
	$(call timed,"CI-HARD: Black format check", $(ACTIVATE) && black --check .)
	$(call timed,"CI-HARD: Ruff lint", $(ACTIVATE) && ruff check .)
	$(call timed,"CI-HARD: Mypy strict typecheck", $(ACTIVATE) && mypy --strict logexp)
	$(call timed,"CI-HARD: Running pytest", $(ACTIVATE) && pytest -vv)

test: ## Run pytest locally
	$(call timed,"Running pytest", $(ACTIVATE) && pytest -vv)

test-clean: ## Remove caches and run pytest cleanly
	$(call timed,"TEST-CLEAN: Removing caches", rm -rf .pytest_cache && find . -name '*.pyc' -delete)
	$(call timed,"TEST-CLEAN: Running pytest", $(ACTIVATE) && pytest -vv)

lint: ## Run Ruff linter
	$(call timed,"Ruff lint", $(ACTIVATE) && ruff check .)

typecheck: ## Run mypy strict typechecking
	$(call timed,"Mypy strict typecheck", $(ACTIVATE) && mypy --strict logexp)

format: ## Run Black autoformatter
	$(call timed,"Black format", $(ACTIVATE) && black .)

format-check: ## Run Black in check-only mode
	$(call timed,"Black format check", $(ACTIVATE) && black --check .)

# =============================================================================
# Docker lifecycle
# =============================================================================

docker-build: guard-build-context ## Build Docker image (cached)
	$(call timed,"Building Docker image", \
		docker build -t $(DOCKER_IMAGE) -f $(BUILD_CONTEXT)/$(DOCKERFILE) $(BUILD_CONTEXT) \
	)

docker-build-no-cache: guard-build-context ## Build Docker image without cache
	$(call timed,"Building Docker image no cache", \
		docker build --no-cache -t $(DOCKER_IMAGE) -f $(BUILD_CONTEXT)/$(DOCKERFILE) $(BUILD_CONTEXT) \
	)

image-export: ## Export Docker image to logexp-image.tar
	$(call timed,"Exporting Docker image to $(IMAGE_TAR)", \
		docker save $(DOCKER_IMAGE) -o $(IMAGE_TAR) \
	)

deploy-image: ## Copy image tarball to KEEP‑0001 and load it
	$(call timed,"Copying image to KEEP-0001", \
		scp -i ~/.ssh/id_ed25519 $(IMAGE_TAR) jeb@keep-0001.local:/opt/logexp/ \
	)
	$(call timed,"Loading image on KEEP-0001", \
		ssh jeb@keep-0001.local "docker load -i /opt/logexp/$(IMAGE_TAR)" \
	)

up-pi: ## Bring up Pi stack via docker compose
	$(call timed,"docker compose up (pi)", docker compose -f $(COMPOSE_PI) up --build)

down: ## Stop Pi docker compose stack
	$(call timed,"Stopping all compose stacks", \
		docker compose -f $(COMPOSE_PI) down || true \
	)

image-pipeline: ## Build → export → deploy-image → restart on KEEP‑0001
	$(call timed,"Pipeline: build image", \
		make docker-build \
	)
	$(call timed,"Pipeline: export image", \
		make image-export \
	)
	$(call timed,"Pipeline: deploy image to KEEP‑0001", \
		make deploy-image \
	)
	$(call timed,"Pipeline: restart LogExp on KEEP‑0001", \
		make restart \
	)

# =============================================================================
# Provisioning
# =============================================================================

preflight: ## Run preflight checks on KEEP‑0001
	$(call timed,"Running preflight checks on KEEP-0001", \
		ansible-playbook $(ANSIBLE_PLAYBOOK_PROVISION) -i $(INVENTORY) --tags preflight \
	)

provision: ## Install Docker + Compose v2 on KEEP‑0001
	$(call timed,"Provisioning KEEP-0001 Docker + Compose v2", \
		ansible-playbook $(ANSIBLE_PLAYBOOK_PROVISION) -i $(INVENTORY) \
	)

pipeline: ## Full pipeline: provision + deploy
	$(call timed,"Full pipeline: provision + deploy", \
		make provision && make deploy \
	)

# =============================================================================
# Deployment
# =============================================================================

deploy: ## Deploy LogExp to KEEP‑0001 via Ansible
	$(call timed,"Deploying LogExp to KEEP-0001", \
		ansible-playbook $(ANSIBLE_PLAYBOOK_DEPLOY) -i $(INVENTORY) \
	)

logs-pi: ## Tail LogExp logs directly from KEEP‑0001
	$(call timed,"Tailing LogExp logs on KEEP-0001", \
		ssh jeb@keep-0001.local "docker logs \$$(docker ps --filter 'name=logexp-logexp' --format '{{.Names}}') --tail 200 -f" \
	)

restart: ## Restart LogExp container on KEEP‑0001
	$(call timed,"Restarting LogExp container on KEEP-0001", \
		ssh jeb@keep-0001.local "docker restart \$$(docker ps --filter 'name=logexp-logexp' --format '{{.Names}}')" \
	)

db-shell: ## Open Postgres shell inside KEEP‑0001's DB container
	$(call timed,"Opening Postgres shell on KEEP-0001", \
		ssh jeb@keep-0001.local "docker exec -it \$$(docker ps --filter 'name=logexp-postgres' --format '{{.Names}}') psql -U logexp" \
	)

# =============================================================================
# Utilities
# =============================================================================

doctor: ## Run environment diagnostics (venv, Python, Docker)
	$(call timed,"Doctor checks", \
		$(PYTHON) --version && \
		(test -d $(VENV) && echo "Venv OK" || echo "Venv missing") && \
		(if docker info >/dev/null 2>&1; then echo 'Docker OK'; else echo 'Docker not running'; fi) \
	)

inventory: ## Show resolved Ansible inventory
	$(call timed,"Showing resolved Ansible inventory", \
		ansible-inventory -i $(INVENTORY) --list \
	)

ping: ## Ping KEEP‑0001 via Ansible
	$(call timed,"Pinging KEEP-0001 via Ansible", \
		ansible -i $(INVENTORY) all -m ping \
	)

help: ## Show this help message
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""
