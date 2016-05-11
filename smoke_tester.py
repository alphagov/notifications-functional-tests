#!/usr/bin/env python

import os
import json
import requests


data = {"request":
        {"branch": "master",
         "config":
            {"env":
                {"global": ["TEST_SUITE=smoketest"]},
                "script": "./scripts/run_smoke_tests.sh"
             }
         }
        }


headers = {'Content-Type': 'application/json',
           'Accept': 'application/json',
           'Travis-API-Version': '3',
           'Authorization': 'token ' + os.environ['TRAVIS_AUTH_TOKEN']
           }
url = "https://api.travis-ci.org/repo/alphagov%2Fnotifications-functional-tests/requests"
resp = requests.post(url, data=json.dumps(data), headers=headers)

print(resp.status_code)
print(resp.json())
