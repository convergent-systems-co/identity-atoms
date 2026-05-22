# Defaults
ENV       ?= dev
NPM       ?= npm

.PHONY: help install dev build check preview tf-init tf-plan tf-apply tf-fmt fmt clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## npm ci in the active site
	cd web && $(NPM) ci

dev: ## Run the site's dev server
	cd web && $(NPM) run dev

build: ## Build the active site into web/<site>/dist
	cd web && $(NPM) run build

check: ## Astro check (type + diagnostics) on the active site
	cd web && $(NPM) run check

preview: ## Preview the production build locally
	cd web && $(NPM) run preview

tf-init: ## tofu init for the selected env
	cd infra/terraform/envs/$(ENV) && tofu init

tf-plan: ## tofu plan for the selected env
	cd infra/terraform/envs/$(ENV) && tofu plan

tf-apply: ## tofu apply for the selected env
	cd infra/terraform/envs/$(ENV) && tofu apply

tf-fmt: ## tofu fmt over infra/
	tofu fmt -recursive infra/

fmt: tf-fmt ## Format everything (currently TF only)

clean: ## Remove site build output
	rm -rf web/$(SITE)/dist web/$(SITE)/.astro
