[![Build Status](https://travis-ci.org/alphagov/notifications-functional-tests.svg)](https://travis-ci.org/alphagov/notifications-functional-tests)

# notifications-functional-tests
Functional tests for Notification applications

# Running the tests
## On a local dev machine

There are two types of test in this repo. Those using selenium webdriver which test user registration, sending of sms notifications and sending of email notifications.

There is an ordering dependency in these tests. The registration test must run before any of the other tests as the user account created is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

In addition there are tests of the python client for the notifications api. For the moment, the client tests require an existing user, service and both email and sms templates. The setup of this account is a bit long winded but the client tests have not yet been adapted to do their own setup.

Therefore to run all of the tests in this suite locally you will need to seed a user using the notify. See the config below for FUNCTIONAL_TEST_EMAIL, FUNCTIONAL_TEST_PASSWORD, TEMPLATE_ID, SERVICE_ID.


- Create a local environment.sh file in the root directory of the project /notifications-functional-tests/environment.sh

This file is included in the .gitignore to prevent the file from being accidentally committed
- Make sure all the apps on running locally.


Contents of the environment.sh file

```shell
    export ENVIRONMENT=preview
    export preview_TWILIO_ACCOUNT_SID=****
    export preview_TWILIO_AUTH_TOKEN=****
    export preview_TWILIO_TEST_NUMBER="+447*********"
    export preview_FUNCTIONAL_TEST_EMAIL=[use the notify tests preview email account]
    export preview_FUNCTIONAL_TEST_PASSWORD=*****
    export preview_NOTIFY_ADMIN_URL=http://localhost:6012
    export preview_SMS_TEMPLATE_ID=***
    export preview_EMAIL_TEMPLATE_ID=***
    export preview_SERVICE_ID=****
```

`preview_TWILIO_ACCOUNT_SID` = account sid for used to read the sms #
`preview_TWILIO_AUTH_TOKEN` = auth token for used to make the api calls to read the sms
`preview_TWILIO_TEST_NUMBER` = for the moment use the preview twilio number - ask for help
`preview_FUNCTIONAL_TEST_EMAIL` = email to use for the tests, this will need to exist for the sign-in flow to work
`preview_FUNCTIONAL_TEST_PASSWORD` = password for the functional test user created, this will need to exist for the sign-in flow to work
`preview_SMS_TEMPLATE_ID` = the id of a test sms template you need to have created for test user and service
`preview_EMAIL_TEMPLATE_ID` = the id of a test email template you need to have created for test user and service
`NOTIFY_ADMIN_URL`  = url of the environment


- Note: to run locally create a test user account on your local apps using the email and password that matches the values for FUNCTIONAL_TEST_EMAIL and FUNCTIONAL_TEST_PASSWORD in environment.sh


Running the tests

```shell
    ./scripts/run_tests.sh
```

## Tests running on Travis

The [notifications-api](https://github.com/alphagov/notifications-api) and [notifications-admin](https://github.com/alphagov/notifications-admin) builds
will trigger the [notifications-functional-test](https://github.com/alphagov/notifications-functional-tests) build,
as scripted in the [trigger-dependent-build.sh](https://github.com/alphagov/notifications-admin/blob/master/scripts/trigger-dependent-build.sh).

When Travis kicks off the functional tests it will use the encrypted environment variables in the [.travis.yml](https://github.com/alphagov/notifications-functional-tests/blob/master/.travis.yml).

Note on travis environment variables are prefixed 'preview'

To create/update these variable run the following travis commands, replacing the *** with the values.
```shell
    travis encrypt preview_TWILIO_ACCOUNT_SID=*** --add
    travis encrypt preview_TWILIO_AUTH_TOKEN=*** --add
    travis encrypt preview_TWILIO_TEST_NUMBER=*** --add
    travis encrypt preview_FUNCTIONAL_TEST_EMAIL=*** --add
    travis encrypt preview_FUNCTIONAL_TEST_PASSWORD=*** --add
    travis encrypt preview_NOTIFY_ADMIN_URL=*** --add
    travis encrypt preview_SMS_TEMPLATE_ID=*** --add
    travis encrypt preview_EMAIL_TEMPLATE_ID=*** --add
    travis encrypt preview_SERVICE_ID=*** --add
```

## What we want to test here and what we do not want to test here
We do not want to test contents of the page beyond a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.

These test are not intended to be used for load testing, however, some performance tolerances could be added.
Currently the test will fail if the sms is not delivered in a minute, which is too long to wait but it is unclear what a valid wait time should be.
Testing headers is possible and a good idea to add to these tests.




