.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: dependencies
dependencies: ## Install build dependencies
	./venv/bin/pip install -r requirements.txt

.PHONY: build
build: dependencies ## Build project

.PHONY: test
test: ## Run functional tests - preview, staging, func test repo PRs and merges post deploy and local dev
	su -c '/var/project/scripts/run_functional_tests.sh' hostuser
