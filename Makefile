.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Install build dependencies
	pip install -r requirements.txt

.PHONY: clean
clean: ## Remove temporary files
	rm -rf screenshots/*
	rm -rf logs/*

.PHONY: test
test: clean ## Run functional tests against local environment
	flake8 .
	pytest -v tests/functional/preview_and_dev
	pytest -v tests/document_download
