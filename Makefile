.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

PIP_ACCEL_CACHE ?= ${CURDIR}/cache/pip-accel
APP_VERSION_FILE = app/version.py

DOCKER_BUILDER_IMAGE_NAME = govuk/notify-func-tests-runner

BUILD_TAG ?= notifications-func-tests-manual

DOCKER_CONTAINER_PREFIX = ${USER}-${BUILD_TAG}

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: venv/bin/activate ## Create virtualenv if it does not exist

venv/bin/activate:
	test -d venv || virtualenv venv
	./venv/bin/pip install pip-accel

.PHONY: check-env-vars
check-env-vars: ## Check mandatory environment variables
	$(if ${DEPLOY_ENV},,$(error Must specify DEPLOY_ENV))
	$(if ${DNS_NAME},,$(error Must specify DNS_NAME))

.PHONY: dependencies
dependencies: venv ## Install build dependencies
	mkdir -p ${PIP_ACCEL_CACHE}
	PIP_ACCEL_CACHE=${PIP_ACCEL_CACHE} ./venv/bin/pip-accel install -r requirements.txt

.PHONY: build
build: dependencies ## Build project

.PHONY: test
test: venv ## Run functional tests - preview, staging, func test repo PRs and merges post deploy and local dev
	su -c '/var/project/scripts/run_functional_tests.sh' hostuser

.PHONY: test-admin
test-admin: venv ## Run admin tests - live smoke tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/test_admin.py' hostuser

.PHONY: test-notify-api-email
test-notify-api-email: venv ## Run notify-api email tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/notify_api/test_notify_api_email.py' hostuser

.PHONY: test-notify-api-sms
test-notify-api-sms: venv ## Run notify-api sms tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/functional/staging_and_prod/notify_api/test_notify_api_sms.py' hostuser

.PHONY: test-provider-email-delivery
test-provider-email-delivery: venv ## Run provider delivery email tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/test_provider_delivery_email.py' hostuser

.PHONY: test-provider-sms-delivery
test-provider-sms-delivery: venv ## Run provider delivery sms tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/test_provider_delivery_sms.py' hostuser

.PHONY: test-providers
test-providers: venv ## Run tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/provider_delivery/' hostuser

.PHONY: test-document-download
test-document-download: venv ## Run documnet-download-api tests
	su -c '/var/project/scripts/run_test_script.sh /var/project/tests/document_download/' hostuser

.PHONY: generate-env-file
generate-env-file: ## Generate the environment file for running the tests inside a Docker container
	scripts/generate_docker_env.sh

.PHONY: prepare-docker-runner-image
prepare-docker-runner-image: ## Prepare the Docker builder image
	mkdir -p ${PIP_ACCEL_CACHE}
	make -C docker build

.PHONY: build-with-docker
build-with-docker: prepare-docker-runner-image ## Build inside a Docker container
	docker run -i --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-build" \
		-v "`pwd`:/var/project" \
		-v /dev/urandom:/dev/random \
		-v "${PIP_ACCEL_CACHE}:/var/project/cache/pip-accel" \
		-e UID=$(shell id -u) \
		-e GID=$(shell id -g) \
		-e http_proxy="${HTTP_PROXY}" \
		-e HTTP_PROXY="${HTTP_PROXY}" \
		-e https_proxy="${HTTPS_PROXY}" \
		-e HTTPS_PROXY="${HTTPS_PROXY}" \
		-e NO_PROXY="${NO_PROXY}" \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make build

define run_test_container
	make prepare-docker-runner-image generate-env-file
	docker run -i --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-test" \
		--add-host=api.local:192.168.65.1 \
		-v "`pwd`:/var/project" \
		-v /dev/urandom:/dev/random \
		-e ENVIRONMENT=${ENVIRONMENT} \
		-e UID=$(shell id -u) \
		-e GID=$(shell id -g) \
		-e SELENIUM_DRIVER=${SELENIUM_DRIVER} \
		-e http_proxy="${HTTP_PROXY}" \
		-e HTTP_PROXY="${HTTP_PROXY}" \
		-e https_proxy="${HTTPS_PROXY}" \
		-e HTTPS_PROXY="${HTTPS_PROXY}" \
		-e NO_PROXY="${NO_PROXY}" \
		--env-file docker.env \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make ${1}
endef

.PHONY: test-with-docker
test-with-docker: ## Run all tests inside a Docker container
	$(call run_test_container, test)

.PHONY: test-admin-with-docker
test-admin-with-docker: ## Run admin tests inside a Docker container
	$(call run_test_container, test-admin)

.PHONY: test-notify-api-email-with-docker
test-notify-api-email-with-docker: ## Run notify-api email tests inside a Docker container
	$(call run_test_container, test-notify-api-email)

.PHONY: test-notify-api-sms-with-docker
test-notify-api-sms-with-docker: ## Run notify-api sms tests inside a Docker container
	$(call run_test_container, test-notify-api-sms)

.PHONY: test-provider-email-delivery-with-docker
test-provider-email-delivery-with-docker: ## Run provider delivery email tests inside a Docker container
	$(call run_test_container, test-provider-email-delivery)

.PHONY: test-provider-sms-delivery-with-docker
test-provider-sms-delivery-with-docker: ## Run provider delivery sms tests inside a Docker container
	$(call run_test_container, test-provider-sms-delivery)

.PHONY: test-providers-with-docker
test-providers-with-docker: ## Run all provider tests inside a Docker container
	$(call run_test_container, test-providers)

.PHONY: test-document-download-with-docker
test-document-download-with-docker: ## Run all provider tests inside a Docker container
	$(call run_test_container, test-document-download)

.PHONY: clean-docker-containers
clean-docker-containers: ## Clean up any remaining docker containers
	docker rm -f $(shell docker ps -q -f "name=${DOCKER_CONTAINER_PREFIX}") 2> /dev/null || true

clean:
	rm -rf cache venv
