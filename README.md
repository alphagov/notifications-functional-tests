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
- Make sure `Notifications Admin`, `Notifications Template Preview`, `Notifications API`, `Notifications API celery` and `Document Download API` are running locally.
- To run against preview, staging, or live, grab the environment files found in credentials repo in `credentials/functional-tests/{env_name}`, and save them locally to a separate file that you can source separately. `environment_staging.sh`

<details>
    <summary>Contents of the environment.sh file</summary>

```shell
export ENVIRONMENT=dev  # for local environments use dev
export TEST_NUMBER= [use your own number or a TV block number like 07700900001]
export FUNCTIONAL_TEST_EMAIL= # the account to create new users for in test_registration
export FUNCTIONAL_TEST_PASSWORD=xxx # password for user account above (created automatically in test)
export NOTIFY_SERVICE_API_KEY=xxx  # create an api key for the GOV.UK Notify service via the admin app
export NOTIFY_RESEARCH_SERVICE_NAME=xxx # See seeded service section below for details of the seeded research service.
export NOTIFY_RESEARCH_SERVICE_ID=xxx # create a service in research mode via the admin app and copy the service id here
export NOTIFY_RESEARCH_SERVICE_API_KEY=xxx # create an api key for the Research service via the admin app
export NOTIFY_RESEARCH_SERVICE_API_TEST_KEY=xxx # create a test api key for the Research service via the admin app
export NOTIFY_RESEARCH_EMAIL_REPLY_TO=[a gov email] # this is the second email in the list when the you go to the send email to one recipient screen i.e. not the default but the second one added
export NOTIFY_RESEARCH_MODE_EMAIL= # a seeded account you have created that can only access NOTIFY_RESEARCH_SERVICE_ID
export NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD=xxx # password for the above account
export NOTIFY_RESEARCH_SERVICE_EMAIL_AUTH_ACCOUNT= # a seeded account you have created that can only access NOTIFY_RESEARCH_SERVICE_ID, doesn't need any permissions and must use email auth
export NOTIFY_RESEARCH_ORGANISATION_ID=xxx # id of organisation that seeded service belongs to
export NOTIFY_RESEARCH_SERVICE_INBOUND_NUMBER=07700900500 # dev tests won't actually send any messages to this number
export JENKINS_BUILD_SMS_TEMPLATE_ID=xxx # SMS template id created in research service, contents detailed below
export JENKINS_BUILD_EMAIL_TEMPLATE_ID=xxx # Email template id created in research service, contents detailed below
export JENKINS_BUILD_LETTER_TEMPLATE_ID=xxx # Letter template id created in research service, contents detailed below
export MMG_INBOUND_SMS_USERNAME=username
export MMG_INBOUND_SMS_AUTH=testkey

export DOCUMENT_DOWNLOAD_API_HOST=http://localhost:7000
export DOCUMENT_DOWNLOAD_API_KEY=auth-token # document-download-api auth token

```
</details>

<details>
    <summary>The seeded research mode service will need to be created as follows: </summary>

* Create a service.
  - Store its name in `NOTIFY_RESEARCH_SERVICE_NAME` and its id in `NOTIFY_RESEARCH_SERVICE_ID`
  - set it into research mode
  - grant it the email auth permission ("Allow editing user auth")
  - grant it the precompiled letters permission ("Allow to send precompiled letters")
* Create an organisation
  - Assign the research mode functional test service to this organisation
  - store the organisation's id in `NOTIFY_RESEARCH_ORGANISATION_ID`
  - invite the seeded user (`NOTIFY_RESEARCH_MODE_EMAIL`) to the organisation
* create a test mode API key for it, store that in `NOTIFY_RESEARCH_SERVICE_API_KEY`
* Two email reply-to addresses will have to be added. One default email, the name of which doesn't matter, and a second non-default email, the name of which you should save in `NOTIFY_RESEARCH_EMAIL_REPLY_TO`.
* You will need two Text message senders, one that is the default and another that has a value of "func tests'.
* A seeded user will have to be created and invited to it with the following details:
  - email_address: `NOTIFY_RESEARCH_MODE_EMAIL`
  - phone_number: `TEST_NUMBER`
  - password: `NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD`
  - all permissions for the seeded service.
  - the user should also accept the invite from the seeded organisation
  - sms auth
* A second seeded user will have to be invited with the following details
  - email_address: `NOTIFY_RESEARCH_SERVICE_EMAIL_AUTH_ACCOUNT`, this can be set to `notify-tests-preview+email-auth@digital.cabinet-office.gov.uk` to send auth emails to a test email account.
  - no permissions required
  - email auth
  - The password should be set the same as above - see `NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD`.
* Create a fake inbound number (see notify-api's `flask command insert-inbound-numbers` for more details), and associate it with your seeded service.


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

<details>
    <summary>The Letter template will need to be created with the following content</summary>


Template name = `Functional Tests - CSV Letter Template with Jenkins Build ID`

Main heading = `Functional Tests - CSV Letter`

Message = `The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).`

</details>

The app uses Selenium to run web automation tests which requires ChromeDriver. Install using the following command. Chromedriver must be version 2.32 or higher to fix a bug where it fails to send the '3' character.

```shell
    brew install chromedriver
```

Running the tests

```shell
    source environment.sh
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
