.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: venv/bin/activate ## Create virtualenv if it does not exist

venv/bin/activate:
	test -d venv || virtualenv venv

.PHONY: check-env-vars
check-env-vars: ## Check mandatory environment variables
	$(if ${DEPLOY_ENV},,$(error Must specify DEPLOY_ENV))
	$(if ${DNS_NAME},,$(error Must specify DNS_NAME))

.PHONY: dependencies
dependencies: venv ## Install build dependencies
	./venv/bin/pip install -r requirements.txt

.PHONY: build
build: dependencies ## Build project

.PHONY: test
test: venv ## Run functional tests - preview, staging, func test repo PRs and merges post deploy and local dev
	su -c '/var/project/scripts/run_functional_tests.sh' hostuser

.PHONY: test-antivirus
test-antivirus: venv # Test antivirus during deploy
	su -c '/var/project/scripts/run_antivirus_functional_test.sh' hostuser

.PHONY: test-admin
test-admin: venv ## Run admin tests - live smoke tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/test_admin.py' hostuser

.PHONY: test-notify-api-email
test-notify-api-email: venv ## Run notify-api email tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/notify_api/test_notify_api_email.py' hostuser

.PHONY: test-notify-api-sms
test-notify-api-sms: venv ## Run notify-api sms tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/notify_api/test_notify_api_sms.py' hostuser

.PHONY: test-notify-api-letter
test-notify-api-letter: venv ## Run notify-api letter tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/notify_api/test_notify_api_letter.py' hostuser

.PHONY: test-provider-email-delivery
test-provider-email-delivery: venv ## Run provider delivery email tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/test_provider_delivery_email.py' hostuser

.PHONY: test-provider-sms-delivery
test-provider-sms-delivery: venv ## Run provider delivery sms tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/test_provider_delivery_sms.py' hostuser

.PHONY: test-provider-inbound-sms
test-provider-inbound-sms: venv ## Run provider delivery sms tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/test_provider_inbound_sms.py' hostuser

.PHONY: test-providers
test-providers: venv ## Run tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/' hostuser

.PHONY: test-document-download
test-document-download: venv ## Run document-download-api tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/document_download/' hostuser

clean:
	rm -rf cache venv
