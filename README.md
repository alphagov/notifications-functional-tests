[![Build Status](https://travis-ci.org/alphagov/notifications-functional-tests.svg)](https://travis-ci.org/alphagov/notifications-functional-tests)

# notifications-functional-tests
Functional tests for Notification applications

# Running the tests
## On a local dev machine

- Create a local environment.sh file in the root directory of the project /notifications-functional-tests/environment.sh
This file is included in the .gitignore to prevent the file from being accidentally committed
- Make sure all the apps on running locally.


Contents of the environment.sh file

```shell    
    export TWILIO_ACCOUNT_SID=****
    export TWILIO_AUTH_TOKEN=****
    export TWILIO_TEST_NUMBER="+447*********"
    export FUNCTIONAL_TEST_EMAIL=user_name@***.gov.uk
    export FUNCTIONAL_TEST_PASSWORD=****
    export NOTIFY_ADMIN_URL=http://localhost:6012
```

`TWILIO_ACCOUNT_SID` = account sid for used to read the sms
`TWILIO_AUTH_TOKEN` = auth token for used to make the api calls to read the sms
`TWILIO_TEST_NUMBER` = this can be your mobile phone, tests will read the sms from this number and delete the messages when after the test run
`FUNCTIONAL_TEST_EMAIL` = email to use for the tests, this will need to exist for the sign-in flow to work
`FUNCTIONAL_TEST_PASSWORD` = password for the functional test user created, this will need to exist for the sign-in flow to work
`NOTIFY_ADMIN_URL`  = url of the environment 


Running the tests

```shell
    ./scripts/run_tests.sh
```

## Tests running on Travis

The [notifications-api](https://github.com/alphagov/notifications-api) and [notifications-admin](https://github.com/alphagov/notifications-admin) builds
will trigger the [notifications-functional-test](https://github.com/alphagov/notifications-functional-tests) build, 
as scripted in the [trigger-dependent-build.sh](https://github.com/alphagov/notifications-admin/blob/master/scripts/trigger-dependent-build.sh).

When Travis kicks off the functional tests it will use the encrypted environment variables in the [.travis.yml](https://github.com/alphagov/notifications-functional-tests/blob/master/.travis.yml).
To create/update these variable run the following travis commands, replacing the *** with the values.
```shell
    travis encrypt TWILIO_ACCOUNT_SID=*** --add
    travis encrypt TWILIO_AUTH_TOKEN=*** --add
    travis encrypt TWILIO_TEST_NUMBER=*** --add
    travis encrypt FUNCTIONAL_TEST_EMAIL=*** --add
    travis encrypt FUNCTIONAL_TEST_PASSWORD=*** --add
    travis encrypt NOTIFY_ADMIN_URL=*** --add
```

## About CSRF tokens
Each functional test journey will need to use the Requests.session to retain the notify_admin_session for the requests. 
The CSRF token is needed for each post request, this is obtained using BeautifulSoup to get the token from the hidden field in the form on the previous page. 
A convenience method exists to get the token.

## What we want to test here and what we do not want to test here
We do not want to test contents of the page, but it is useful to check the page title after a GET request to ensure the flow is correct.
These test are not intended to be used for load testing, however, some performance tolerances could be added. 
Currently the test will fail if the sms is not delivered in a minute, which is too long to wait but it is unclear what a valid wait time should be.
Testing headers is possible and a good idea to add to these tests.




