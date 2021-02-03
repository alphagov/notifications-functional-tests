# notifications-functional-tests

The tests are:

- Selenium web driver tests of the Notify user interface
- tests of the API using the [python API client](https://github.com/alphagov/notifications-python-client).

## Running the tests from your local dev machine

```shell
brew install --cask chromedriver # needs to be >= v2.32
```

To run locally you need to populate a `.gitignore` and `environment.sh` file with the relevant values.

- To run locally, `source environment_local.sh`
- To run against preview, staging, or live, grab the environment files found in credentials repo in `credentials/functional-tests/{env_name}`, and save them locally to a separate file that you can source separately. `environment_staging.sh`

Running the tests

```shell
source environment_local.sh
# source environment_preview.sh # etc etc
./scripts/run_functional_tests.sh
```

Note, there is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

## Running the tests against your local development environment

To populate the local database run

```shell
psql notification_api -f db_setup_fixtures.sql
```

Run the following in other tabs / windows:

- [notifications-api](https://github.com/alphagov/notifications-api):
  - Flask app (run `export ANTIVIRUS_ENABLED=1 first`)
  - Celery

- [notifications-template-preview](https://github.com/alphagov/notifications-template-preview):
  - Flask app
  - Celery

- [notifications-admin](https://github.com/alphagov/notifications-admin)
- [notifications-antivirus](https://github.com/alphagov/notifications-antivirus)

## Tests running on Concourse

These tests are run against preview, staging and production using Concourse. We run a full set of tests on preview but only a smaller set of tests, also known as smoke tests, on staging and production.

The Concourse jobs are defined in our [infrastructure repo](https://github.com/alphagov/notifications-aws/blob/master/concourse/templates/functional-tests.yml.j2).

Users with the required services and templates have already been set up for each of those environments. The details for these are found in our credentials repo. Note credentials containing the needed environment variables are prefixed 'preview', 'staging' and 'live'.


## What we want to test here and what we do not want to test here
We do not want to test contents of the page beyond a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.

These test are not intended to be used for load testing.

