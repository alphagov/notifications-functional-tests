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
test: venv ## Run tests
	sh -e /etc/init.d/xvfb start && ./scripts/run_functional_tests.sh

.PHONY: test-providers
test-providers: venv ## Run tests
	sh -e /etc/init.d/xvfb start && ./scripts/run_provider_delivery_tests.sh

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
		-v `pwd`:/var/project \
		-v ${PIP_ACCEL_CACHE}:/var/project/cache/pip-accel \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make build

.PHONY: test-with-docker
test-with-docker: prepare-docker-runner-image generate-env-file ## Run tests inside a Docker container
	docker run -i --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-test" \
		-v `pwd`:/var/project \
		-e ENVIRONMENT=${ENVIRONMENT} \
		-e SELENIUM_DRIVER=${SELENIUM_DRIVER} \
		--env-file docker.env \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make test

.PHONY: test-providers-with-docker
test-providers-with-docker: prepare-docker-runner-image generate-env-file ## Run tests inside a Docker container
	docker run -i --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-test" \
		-v `pwd`:/var/project \
		-e ENVIRONMENT=${ENVIRONMENT} \
		-e SELENIUM_DRIVER=${SELENIUM_DRIVER} \
		--env-file docker.env \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make test-providers

.PHONY: clean-docker-containers
clean-docker-containers: ## Clean up any remaining docker containers
	docker rm -f $(shell docker ps -q -f "name=${DOCKER_CONTAINER_PREFIX}") 2> /dev/null || true

clean:
	rm -rf cache venv
