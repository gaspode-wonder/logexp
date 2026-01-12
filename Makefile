# filename: Makefile
# =============================================================================
# LogExp Makefile — Docker-first, parallel to pi-log
# Deterministic developer workflows with CI parity and Ansible deployment
# =============================================================================

PYTHON := python3
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

ANSIBLE_PLAYBOOK_DEPLOY := ansible/playbooks/deploy-logexp.yml
ANSIBLE_PLAYBOOK_PROVISION := ansible/playbooks/provision-pi.yml
INVENTORY := ansible/inventory/hosts.ini

DOCKER_IMAGE := logexp:latest
COMPOSE_PI := docker-compose.pi.yml

# ANSI Colors
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
# Bootstrap & CI
# =============================================================================

bootstrap:
	$(call timed,"Bootstrapping development environment", \
		$(PYTHON) -m venv $(VENV) && \
		$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt \
	)

ci:
	$(call timed,"CI: Creating virtual environment", $(PYTHON) -m venv $(VENV))
	$(call timed,"CI: Installing dependencies", $(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt)
	$(call timed,"CI: Running pytest", $(ACTIVATE) && pytest -vv)

test:
	$(call timed,"Running pytest", $(ACTIVATE) && pytest -vv)

lint:
	$(call timed,"Ruff lint", $(ACTIVATE) && ruff check .)

typecheck:
	$(call timed,"Mypy strict typecheck", $(ACTIVATE) && mypy --strict logexp)

# =============================================================================
# Docker lifecycle
# =============================================================================

docker-build:
	$(call timed,"Building Docker image", docker build -t $(DOCKER_IMAGE) .)

up-pi:
	$(call timed,"docker compose up (pi)", docker compose -f $(COMPOSE_PI) up --build)

down:
	$(call timed,"Stopping all compose stacks", \
		docker compose -f $(COMPOSE_PI) down || true \
	)

# =============================================================================
# Provisioning (new)
# =============================================================================

preflight:
	$(call timed,"Running preflight checks on KEEP-0001", \
		ansible-playbook $(ANSIBLE_PLAYBOOK_PROVISION) -i $(INVENTORY) --tags preflight \
	)

provision:
	$(call timed,"Provisioning KEEP-0001 Docker + Compose v2", \
		ansible-playbook $(ANSIBLE_PLAYBOOK_PROVISION) -i $(INVENTORY) \
	)

pipeline:
	$(call timed,"Full pipeline: provision + deploy", \
		make provision && make deploy \
	)

# =============================================================================
# Deployment
# =============================================================================

deploy:
	$(call timed,"Deploying LogExp to KEEP-0001", \
		ansible-playbook $(ANSIBLE_PLAYBOOK_DEPLOY) -i $(INVENTORY) \
	)

logs:
	$(call timed,"Tailing LogExp logs on KEEP-0001", \
		ssh jeb@keep-0001.local "docker logs \$$(docker ps --filter 'name=logexp-logexp' --format '{{.Names}}') --tail 200 -f" \
	)

restart:
	$(call timed,"Restarting LogExp container on KEEP-0001", \
		ssh jeb@keep-0001.local "docker restart \$$(docker ps --filter 'name=logexp-logexp' --format '{{.Names}}')" \
	)

# =============================================================================
# Utilities
# =============================================================================

doctor:
	$(call timed,"Doctor checks", \
		$(PYTHON) --version && \
		(test -d $(VENV) && echo "Venv OK" || echo "Venv missing") && \
		(if docker info >/dev/null 2>&1; then echo 'Docker OK'; else echo 'Docker not running'; fi) \
	)

inventory:
	$(call timed,"Showing resolved Ansible inventory", \
		ansible-inventory -i $(INVENTORY) --list \
	)

ping:
	$(call timed,"Pinging KEEP-0001 via Ansible", \
		ansible -i $(INVENTORY) all -m ping \
	)

help:
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""
