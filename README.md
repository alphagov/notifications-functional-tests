# notifications-functional-tests
Functional tests for Notification applications

# Running the tests

## On a local dev machine

The majority of tests that are used in local development and also run on master build on Jenkins (running against preview environment) are Selenium web driver tests.

There is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

In the main suite there are also tests that that directly use the [python client](https://github.com/alphagov/notifications-python-client) for the notifications api. The client tests require an existing user, service, api key and both email and sms templates.

To run locally you need to populate a `.gitignore` and `environment.sh` file with the relevant values. On Jenkins the environment variables are set in the build settings page.

## Local environment file

- Create a local `environment.sh` file in the root directory of the project.
This file is included in the `.gitignore` to prevent the environment file from being accidentally committed
- Make sure all the `Notifications Admin`, `Notifications API` and `Notifications celery` are running locally.

<details>
    <summary>Contents of the environment.sh file</summary>

```shell
export ENVIRONMENT=dev  # for local environments use dev
export dev_TEST_NUMBER= [use your own number]
export dev_FUNCTIONAL_TEST_EMAIL=[some gmail account @digital.cabinet-office.gov.uk]
export dev_FUNCTIONAL_TEST_PASSWORD=xxx # password for gmail account and user account created in test
export dev_NOTIFY_ADMIN_URL=http://localhost:6012
export dev_NOTIFY_API_URL=http://localhost:6011
export dev_NOTIFY_SERVICE_ID=d6aa2c68-a2d9-4437-ab19-3ae8eb202553
export dev_NOTIFY_SERVICE_API_KEY=xxx  # create an api key for the GOV.UK Notify service via the admin app
export dev_NOTIFY_RESEARCH_SERVICE_ID=xxx # create a service in research mode via the admin app and copy the service id here
export dev_NOTIFY_RESEARCH_SERVICE_API_KEY=xxx # create an api key for the Research service via the admin app
export dev_NOTIFY_RESEARCH_MODE_EMAIL=[some other gmail account @digital.cabinet-office.gov.uk]
export dev_NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD=xxx # password for gmail account and user account created in test
export dev_JENKINS_BUILD_SMS_TEMPLATE_ID=xxx # SMS template id created in research service, contents detailed below
export dev_JENKINS_BUILD_EMAIL_TEMPLATE_ID=xxx # Email template id created in research service, contents detailed below
    
```
</details>

<details>
    <summary>The Email template will need to be created with the following content</summary>


Template name = `Functional Tests - CSV Email Template with Jenkins Build ID`

Subject = `Functional Tests - CSV Email`

Message = `The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).`

</details>

<details>
    <summary>The SMS template will need to be created with the following content</summary>


Template name = `Functional Tests - CSV SMS Template with Jenkins Build ID`

Message = `The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).`

</details>

The app uses Selenium to run web automation tests which requires ChromeDriver. Install using the following command.

```shell
    brew install chromedriver
```

Running the tests

```shell
    ./scripts/run_functional_tests.sh
```

## Tests running on Jenkins docker containers


### Preview - tests against master

The same suite as local development runs master code deployed on preview environment env [https://www.notify.works](https://www.notify.works)

All the relevant environment variables are setup in the build settings on Jenkins for this repo.


### Staging and Live builds - test against staging and live branches respectively

To run against staging and live environments a seeded user account on each of those environments has been created. In addition a service for the user has been created as well as an email and sms template created.

To run against those instances of Notify, additional environment variables for all of SMS_TEMPLATE_ID, EMAIL_TEMPLATE_ID and SERVICE_ID. These have already been set up on the Jenkins build using the settings page.

The [notifications-api](https://github.com/alphagov/notifications-api) and [notifications-admin](https://github.com/alphagov/notifications-admin) merge into master
will trigger the [notifications-functional-test](https://github.com/alphagov/notifications-functional-tests) build.

Note on Jenkins environment variables are prefixed 'master', 'preview', 'staging' and 'live'

## What we want to test here and what we do not want to test here
We do not want to test contents of the page beyond a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.

These test are not intended to be used for load testing, however, some performance tolerances could be added.

Currently the test will fail if the sms is not delivered in a minute, which is too long to wait but it is unclear what a valid wait time should be.

Testing headers is possible and a good idea to add to these tests.

Tests should be added when new features are added to the Notifications Admin app, and ideally the local dev functional tests should be run before each PR on the Admin, and API if a code change is likely to affect the provider delivery.
