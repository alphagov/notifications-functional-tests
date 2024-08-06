#!/bin/bash

set -eo pipefail

ENVIRONMENT=$1

AWS_REGION="eu-west-1"
export AWS_REGION
AWS_DEFAULT_REGION=$AWS_REGION
export AWS_DEFAULT_REGION

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ -z "$$(ACCOUNT_ID)" ]; then echo "ACCOUNT_ID is empty"; exit 1; fi

PARAMS=$(aws ssm get-parameter --with-decryption --name arn:aws:ssm:eu-west-1:${ACCOUNT_ID}:parameter/notify/${ENVIRONMENT}/functional-tests/generated/environment | jq -r .Parameter.Value)
source /dev/stdin <<< "${PARAMS}"

export API_FIXTURE_APPLIED="true"

# loop through each of our args after the environment
for arg in "${@:2}";
do
    pytest -v $arg -n 4 --dist loadgroup ${FUNCTIONAL_TESTS_EXTRA_PYTEST_ARGS}
done
