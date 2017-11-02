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
    NOTIFY_RESEARCH_MODE_EMAIL
    NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD
    NOTIFY_RESEARCH_SERVICE_ID
    NOTIFY_RESEARCH_SERVICE_API_KEY
    JENKINS_BUILD_EMAIL_TEMPLATE_ID
    JENKINS_BUILD_SMS_TEMPLATE_ID
    NOTIFY_RESEARCH_SERVICE_NAME
    NOTIFY_RESEARCH_EMAIL_REPLY_TO
)

for env_var in "${env_vars[@]}"; do
    echo "${ENVIRONMENT}_${env_var}=${!env_var}" >> docker.env
done

echo "BUILD_ID=$BUILD_ID" >> docker.env
