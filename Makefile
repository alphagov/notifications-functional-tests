.DEFAULT_GOAL := help
SHELL := /bin/bash

NOTIFY_CREDENTIALS ?= ~/.notify-credentials

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Install build dependencies
	mkdir -p logs screenshots
	uv pip install -r requirements_for_test.txt

.PHONY: freeze-requirements
freeze-requirements: ## create static requirements_for_test.txt
	python -c "from notifications_utils.version_tools import copy_config; copy_config()"
	uv pip compile requirements_for_test.in -o requirements_for_test.txt

.PHONY: clean
clean: ## Remove temporary files
	rm -rf screenshots/*
	rm -rf logs/*

.PHONY: $(filter-out dev%,$(MAKECMDGOALS))
dev%:
	$(eval export ENVIRONMENT=$@)
	@true

.PHONY: preview
preview:
	$(eval export ENVIRONMENT=preview)
	@true

.PHONY: staging
staging:
	$(eval export ENVIRONMENT=staging)
	@true

.PHONY: prod
prod:
	$(eval export ENVIRONMENT=prod)
	@true

env-environment-check:
	@test -n "${ENVIRONMENT}" || (echo "ENVIRONMENT variable is not set"; exit 1)

.PHONY: env-functional-tests
env-functional-tests: env-environment-check
	@./scripts/env-test.sh "${ENVIRONMENT}" tests/functional/preview_and_dev tests/document_download/preview_and_dev

.PHONY: env-smoke-tests
env-smoke-tests: env-environment-check
	@./scripts/env-test.sh "${ENVIRONMENT}" tests/functional/staging_and_prod tests/document_download/staging_and_prod

.PHONY: env-provider-tests
env-provider-tests: env-environment-check
	@./scripts/env-test.sh "${ENVIRONMENT}" tests/provider_delivery/test_provider_delivery_email.py tests/provider_delivery/test_provider_delivery_sms.py

.PHONY: test
test: clean ## Run functional tests against local environment
	ruff check .
	black --check .
	pytest tests/functional/preview_and_dev -n auto --dist loadgroup ${FUNCTIONAL_TESTS_EXTRA_PYTEST_ARGS}
	pytest tests/document_download/preview_and_dev ${FUNCTIONAL_TESTS_EXTRA_PYTEST_ARGS}

.PHONY: generate-staging-db-fixtures
generate-staging-db-fixtures: ## Generates DB fixtures for the staging database
	$(if $(shell which gpg2), $(eval export GPG=gpg2), $(eval export GPG=gpg))
	$(if ${GPG_PASSPHRASE_TXT}, $(eval export DECRYPT_CMD=echo -n $$$${GPG_PASSPHRASE_TXT} | ${GPG} --quiet --batch --passphrase-fd 0 --pinentry-mode loopback -d), $(eval export DECRYPT_CMD=${GPG} --quiet --batch -d))

	@jinja2 --strict db_fixtures/staging.sql.j2 \
	    --format=json \
	    -o db_fixtures/staging.sql \
	    <(${DECRYPT_CMD} ${NOTIFY_CREDENTIALS}/credentials/functional-tests/staging-functional-db-fixtures.gpg) 2>&1

.PHONY: generate-local-dev-db-fixtures
generate-local-dev-db-fixtures:
	$(MAKE) -C ../notifications-local generate-local-dev-db-fixtures

.PHONY: bump-utils
bump-utils:  # Bump notifications-utils package to latest version
	python -c "from notifications_utils.version_tools import upgrade_version; upgrade_version()"
