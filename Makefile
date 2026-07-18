# ITNEXT Global Careers — modular monolith
# Local dev uses docker-compose; deploy targets push to Azure Container Apps.

SHELL := /bin/bash
COMPOSE := docker compose
API := $(COMPOSE) exec api1

# --- Azure deploy config (override on the command line or in the CI env) ---
ACR_NAME        ?= itnextacr
IMAGE_NAME      ?= itnext-api
IMAGE_TAG       ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo latest)
IMAGE           := $(ACR_NAME).azurecr.io/$(IMAGE_NAME):$(IMAGE_TAG)
RESOURCE_GROUP  ?= itnext-rg
CONTAINER_APP   ?= itnext-api
ENV_NAME        ?= itnext-env

.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------
##@ General
.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make \033[36m<target>\033[0m\n"} \
	/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } \
	/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

# ----------------------------------------------------------------------------
##@ Local development
.PHONY: init
init: ## First-time setup: copy .env and build images
	@test -f .env || cp .env.example .env
	$(COMPOSE) build

.PHONY: up
up: ## Start the stack (db, redis, 3x api behind nginx, web) in the background
	$(COMPOSE) up -d

.PHONY: down
down: ## Stop the stack
	$(COMPOSE) down

.PHONY: logs
logs: ## Tail API logs (all replicas)
	$(COMPOSE) logs -f api1 api2 api3

.PHONY: ps
ps: ## Show running containers
	$(COMPOSE) ps

.PHONY: shell
shell: ## Open a shell in the API container
	$(API) bash

.PHONY: db-shell
db-shell: ## Open a psql shell
	$(COMPOSE) exec db psql -U itnext -d itnext

# ----------------------------------------------------------------------------
##@ Database
.PHONY: migration
migration: ## Autogenerate a migration:  make migration m="add users"
	$(API) alembic revision --autogenerate -m "$(m)"

.PHONY: migrate
migrate: ## Apply all pending migrations
	$(API) alembic upgrade head

.PHONY: downgrade
downgrade: ## Roll back one migration
	$(API) alembic downgrade -1

.PHONY: seed
seed: ## Seed the package tiers
	$(API) python -m app.seed

.PHONY: promote-admin
promote-admin: ## Grant admin access to an existing user:  make promote-admin EMAIL=you@example.com
	$(API) python -m app.promote_admin "$(EMAIL)"

# ----------------------------------------------------------------------------
##@ Quality
.PHONY: test
test: ## Run tests
	$(API) pytest -q

.PHONY: lint
lint: ## Lint with ruff
	$(API) ruff check app

.PHONY: format
format: ## Format with ruff
	$(API) ruff format app

# ----------------------------------------------------------------------------
##@ Deploy (Azure Container Apps)
.PHONY: azure-login
azure-login: ## Log in to Azure and the container registry
	az login
	az acr login --name $(ACR_NAME)

.PHONY: build
build: ## Build the production image locally
	docker build -t $(IMAGE) ./backend

.PHONY: push
push: ## Push the image to Azure Container Registry
	docker push $(IMAGE)

.PHONY: release
release: build push ## Build + push in one step

.PHONY: deploy
deploy: ## Roll the new image onto the Container App (runs migrations first)
	az containerapp exec -n $(CONTAINER_APP) -g $(RESOURCE_GROUP) \
		--command "alembic upgrade head" || true
	az containerapp update \
		-n $(CONTAINER_APP) -g $(RESOURCE_GROUP) \
		--image $(IMAGE)
	@echo "Deployed $(IMAGE) to $(CONTAINER_APP)"

.PHONY: ship
ship: release deploy ## Full pipeline: build, push, migrate, deploy

.PHONY: provision
provision: ## One-time: create the Container App env + app (scales 1..5 replicas)
	az containerapp env create -n $(ENV_NAME) -g $(RESOURCE_GROUP)
	az containerapp create \
		-n $(CONTAINER_APP) -g $(RESOURCE_GROUP) \
		--environment $(ENV_NAME) \
		--image $(IMAGE) \
		--target-port 8000 --ingress external \
		--min-replicas 1 --max-replicas 5 \
		--cpu 0.5 --memory 1.0Gi
	@echo "Provisioned. Container Apps load-balances across the replicas automatically."

# ----------------------------------------------------------------------------
##@ Cleanup
.PHONY: clean
clean: ## Stop stack and remove volumes (DESTROYS local data)
	$(COMPOSE) down -v
