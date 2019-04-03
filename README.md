# notifications-functional-tests
Functional tests for Notification applications

# Running the tests

## On a local dev machine

The majority of tests that are used in local development and also run on master build on Jenkins (running against preview environment) are Selenium web driver tests.

There is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

In the main suite there are also tests that that directly use the [python client](https://github.com/alphagov/notifications-python-client) for the notifications api. The client tests require an existing user, service, api key and both email and sms templates.

To run locally you need to populate a `.gitignore` and `environment.sh` file with the relevant values. On Jenkins the environment variables are set in the build settings page.

Note: Your local celery must be run with `ANTIVIRUS_ENABLED=1` set in the environment for the test_view_precompiled_letter_message_log_virus_scan_failed test to work

## Local environment file

- Make sure `Notifications Admin`, `Notifications Template Preview`, `Notifications API`, `Notifications API celery` and `Document Download API` are running locally.
- to run locally, `source environment_local.sh`
- To run against preview, staging, or live, grab the environment files found in credentials repo in `credentials/functional-tests/{env_name}`, and save them locally to a separate file that you can source separately. `environment_staging.sh`

To populate the local database run

```shell
  psql notification_api -f db_setup_fixtures.sql
```

The app uses Selenium to run web automation tests which requires ChromeDriver. Install using the following command. Chromedriver must be version 2.32 or higher to fix a bug where it fails to send the '3' character.

```shell
    brew install chromedriver
```

Running the tests

```shell
    source environment_local.sh
    # source environment_preview.sh # etc etc
    ./scripts/run_functional_tests.sh
```

## Tests running on Jenkins docker containers


### Preview

The same suite as local development runs on PRs against preview environment env [https://www.notify.works](https://www.notify.works)

All the relevant environment variables are setup in the build settings on Jenkins for this repo.


### Staging and Live builds

To run against staging and live environments a seeded user account on each of those environments has been created. In addition a service for the user has been created as well as an email and sms template created.

To run against those instances of Notify, additional environment variables for all of SMS_TEMPLATE_ID, EMAIL_TEMPLATE_ID and SERVICE_ID. These have already been set up on the Jenkins build using the settings page.

The [notifications-api](https://github.com/alphagov/notifications-api) and [notifications-admin](https://github.com/alphagov/notifications-admin) merge into master
will trigger the [notifications-functional-test](https://github.com/alphagov/notifications-functional-tests) build.

Note on Jenkins environment variables are prefixed 'preview', 'staging' and 'live'

## What we want to test here and what we do not want to test here
We do not want to test contents of the page beyond a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.

These test are not intended to be used for load testing, however, some performance tolerances could be added.

Currently the test will fail if the sms is not delivered in a minute, which is too long to wait but it is unclear what a valid wait time should be.

Testing headers is possible and a good idea to add to these tests.

Tests should be added when new features are added to the Notifications Admin app, and ideally the local dev functional tests should be run before each PR on the Admin, and API if a code change is likely to affect the provider delivery.
