#!/bin/bash
#
# Run project tests
#
# NOTE: This script expects to be run from the project root with
# ./scripts/run_tests.sh

# Use default environment vars for localhost if not already set

set -o pipefail
source environment.sh 2> /dev/null

function display_result {
  RESULT=$1
  EXIT_STATUS=$2
  TEST=$3

  if [ $RESULT -ne 0 ]; then
    echo -e "\033[31m$TEST failed\033[0m"
    exit $EXIT_STATUS
  else
    echo -e "\033[32m$TEST passed\033[0m"
  fi
}

pep8 .
display_result $? 1 "Code style check"

# default env to master (i.e. preview)
environment=${ENVIRONMENT:=master}
export ENVIRONMENT=$environment


# get status page for env under tests and spit out to console
function display_status {
  url=$ENVIRONMENT'_NOTIFY_ADMIN_URL'
  curl ${!url}/'_status'
}

case $ENVIRONMENT in
    staging|live)
      echo Running $ENVIRONMENT tests
      display_status $ENVIRONMENT
      py.test -x tests/staging_live/test_send_notifications_from_csv.py
      ;;
    master|*)
      echo 'Default test run - for' $ENVIRONMENT
      display_status $ENVIRONMENT
      py.test -x tests/test_all_the_things.py
      ;;
esac

display_result $? 3 "Unit tests"
