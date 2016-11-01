#!/bin/bash
#
# Run a specific test script passed in by the first argument
#
# NOTE: This script expects to be run from the project root with
# ./scripts/run_test_script.sh

# Use default environment vars for localhost if not already set

set -o pipefail
[ "$IGNORE_ENVIRONMENT_SH" = "1" ] || source environment.sh 2> /dev/null

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

if [ -d venv ]; then
  source ./venv/bin/activate
fi

pep8 --exclude=venv .
display_result $? 1 "Code style check"

# default env to master (i.e. preview)
environment=${ENVIRONMENT:=master}
export ENVIRONMENT=$environment


# get status page for env under tests and spit out to console
function display_status {
  url=$ENVIRONMENT'_NOTIFY_ADMIN_URL'
  echo 'Build info:'
  curl -sSL ${!url}/'_status'
  echo
}

# remove any previous screenshots
if [ -d screenshots ]; then
  echo 'Removing old test screenshots'
  rm -rfv screenshots
fi
mkdir screenshots
# remove any previous errors
rm -f browser.log

script=$1
if [[ -n "$script" ]]; then
  echo Running $ENVIRONMENT tests
       display_status $ENVIRONMENT
       py.test -x $script
else
    echo "No test script provided"
fi

display_result $? 3 "Unit tests"
