#!/bin/bash
#
# Run project tests
#
# NOTE: This script expects to be run from the project root with
# ./scripts/run_tests.sh

# Use default environment vars for localhost if not already set

set -o pipefail

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

if [ ! $VIRTUAL_ENV ]; then
  source ./venv/bin/activate
fi

# get status page for env under tests and spit out to console
function display_status {
  python -c "
import requests
from config import config, setup_shared_config
setup_shared_config()
print('Build info:')
print(requests.get(config['notify_admin_url'] + '/_status').json())
"
}

# remove any previous errors
if [ -d logs ]; then
  echo 'Removing old test logs'
  rm -rfv logs
fi
mkdir logs

echo "Running $ENVIRONMENT tests"
display_status $ENVIRONMENT

py.test -k 'test_send_precompiled_letter_with_virus_notification_via_api or test_document_download' -x -v

display_result $? 3 "Antivirus tests"
