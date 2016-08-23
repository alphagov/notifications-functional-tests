#!/usr/bin/env bash

set -eo pipefail

function exit_with_msg {
    echo $1
    exit $2
}

echo -n "" > docker.env

[ -n "$ENVIRONMENT" ] || exit_with_msg "ENVIRONMENT is not defined, generating empty docker.env" 0

env_vars=(
    TEST_NUMBER
    FUNCTIONAL_TEST_NAME
    FUNCTIONAL_TEST_EMAIL
    FUNCTIONAL_TEST_PASSWORD
    FUNCTIONAL_TEST_EMAIL_PASSWORD
    NOTIFY_ADMIN_URL
    NOTIFY_API_URL
    NOTIFY_SERVICE_ID
    NOTIFY_SERVICE_API_KEY
    SMS_TEMPLATE_ID
    EMAIL_TEMPLATE_ID
    SERVICE_ID
    API_KEY
    DESKPRO_PERSON_EMAIL
    DESKPRO_DEPT_ID
    DESKPRO_ASSIGNED_AGENT_TEAM_ID
    DESKPRO_API_HOST
    DESKPRO_API_KEY
)

for env_var in "${env_vars[@]}"; do
    echo "${ENVIRONMENT}_${env_var}=${!env_var}" >> docker.env
done
