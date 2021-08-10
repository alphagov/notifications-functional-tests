# notifications-functional-tests

The tests are:

- `functional/`: tests of the Notify user interface and API (notifications.service.gov.uk)
- `document_download/`: tests of the Documents user interface and API (documents.service.gov.uk)
- `provider_delivery/`: tests for delivery of notifications (Staging and Production only)

These tests are run against preview, staging and production using Concourse. We run a full set of tests on preview but only a smaller set of tests, also known as smoke tests, on staging and production.

The Concourse jobs are defined in our [infrastructure repo](https://github.com/alphagov/notifications-aws/blob/master/concourse/templates/functional-tests.yml.j2).

## Uses

These tests are not intended to be used for load testing.

## Installation

```shell
brew install --cask chromedriver # needs to be >= v2.32

make bootstrap # install dependencies, etc.
```

Note: when you run the tests for the first time on a Mac, **you may need to authorise `chromedriver` in your security settings** ("System Preferences > Security & Privacy > General").

## Running tests

Note, there is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

### Running the tests against your local development environment

**Note: this is currently only supported for `functional/` and `document_download/` tests.** See the next section if you want to run the `provider_delivery/` tests locally.

Populate the local database with fixture data:

```shell
psql notification_api -f db_setup_fixtures.sql
```

Note: If you see any errors (for example a `duplicate key value violates unique constraint` line or similar), that table will not be saved but other following table inserts will still attempt. You'll need to fix the errors for that table (either in your local database or in the fixture script) and run the script again, or open `psql` and just copy-paste the lines from the script that you need.

Now run the following in other tabs / windows:

- If you're testing the Notify user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api):
    - Flask app (run `export ANTIVIRUS_ENABLED=1 first`)
    - Celery
  - [notifications-template-preview](https://github.com/alphagov/notifications-template-preview):
    - Flask app
    - Celery
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
    - Flask app
  - [notifications-antivirus](https://github.com/alphagov/notifications-antivirus)
    - Celery

- If you're testing the Documents user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api) (Flask app only)
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
  - [document-download-api](https://github.com/alphagov/document-download-api)
  - [document-download-frontend](https://github.com/alphagov/document-download-frontend)

Then source the environment and run the tests:

```
source environment_local.sh

# run all the tests
make test

# run a specific test
pytest tests/functional/preview_and_dev/test_seeded_user.py
```

### Running the tests against preview, staging or production

Users with the required services and templates have already been set up for each of these environments. The details for these are found in our credentials repo, under `credentials/functional-tests`. There are different sets of credentials depending on the tests you want to run e.g. `staging-provider`, `staging-functional` . Decrypt the credentials you need and paste them locally in a separate file e.g. `environment_staging.sh`. Then:

```
source environment_{env_name}.sh

# run specific tests
pytest tests/document_download
```

Every 90 days we need to re-validate the email for the `notify-tests-preview+admin_tests` user. You can check if this is the cause of failures using the following query in Kibana:

```
access.agent: selenium AND _type: gorouter AND cf.app: notify-admin AND access.url: "re-validate-email"
```

To re-validate the email, use an Incognito window to sign in to Notify as the service user. As platform admin, you can snoop the 2FA code and verification link from the GOV.UK Notify service.


## Further documentation

- [Updating db_setup_fixtures](docs/update-db_setup_fixtures.md)
- [Style guide](docs/style-guide.md)
