# notifications-functional-tests

The tests are:

- Selenium web driver tests of the Notify user interface (notifications.service.gov.uk)
- Selenium web driver tests of the Document user interface (documents.service.gov.uk)
- Tests of the API using the [python API client](https://github.com/alphagov/notifications-python-client).

These tests are run against preview, staging and production using Concourse. We run a full set of tests on preview but only a smaller set of tests, also known as smoke tests, on staging and production.

The Concourse jobs are defined in our [infrastructure repo](https://github.com/alphagov/notifications-aws/blob/master/concourse/templates/functional-tests.yml.j2).

## Installation

```shell
brew install --cask chromedriver # needs to be >= v2.32
```

## Running tests

Note, there is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

### Running the tests against your local development environment

Populate the local database with fixture data:

```shell
psql notification_api -f db_setup_fixtures.sql
```

Now run the following in other tabs / windows:

- If you're testing the Notify user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api):
    - Flask app (run `export ANTIVIRUS_ENABLED=1 first`)
    - Celery
  - [notifications-template-preview](https://github.com/alphagov/notifications-template-preview):
    - Flask app
    - Celery
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
  - [notifications-antivirus](https://github.com/alphagov/notifications-antivirus)

- If you're testing the Document user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api) (Flask app only)
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
  - [document-download-api](https://github.com/alphagov/document-download-api)
  - [document-download-frontend](https://github.com/alphagov/document-download-frontend)

Then source the environment and run the tests:

```
source environment_local.sh

./scripts/run_functional_tests.sh # or
pytest document_download
```

### Running the tests against preview, staging or production

Users with the required services and templates have already been set up for each of these environments. The details for these are found in our credentials repo, under `credentials/functional-tests/{env_name}`. Decrypt one and paste it locally in a separate file e.g. `environment_staging.sh`. Then:

```
source environment_{env_name}.sh

./scripts/run_functional_tests.sh # or
pytest document_download
```

## What we want to test here and what we do not want to test here
We do not want to test contents of the page beyond a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.

These test are not intended to be used for load testing.
