# notifications-functional-tests

The tests are:

- `functional/`: tests of the Notify user interface and API (notifications.service.gov.uk)
- `document_download/`: tests of the Documents user interface and API (documents.service.gov.uk)
- `provider_delivery/`: tests for delivery of notifications (Staging and Production only)

These tests are run against preview, staging and production using Concourse. We run a full set of tests on preview but only a smaller set of tests, also known as smoke tests, on staging and production.

The Concourse jobs are defined in our [infrastructure repo](https://github.com/alphagov/notifications-aws/blob/master/concourse/templates/functional-tests.yml.j2).

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

## What we want to test here and what we do not want to test here

We do not want to test contents of the page beyond a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.

These test are not intended to be used for load testing.

## Updating db_setup_fixtures.sql

1. Back up your local database with `pg_dump --format=t notification_api > ~/Downloads/my_local_db_backup.tar`
2. Drop your local db with `dropdb notification_api`
3. Run `make bootstrap` in the notifications-api repo to set up the database.
4. Run `psql notification_api --file=db_setup_fixtures.sql` to get existing db objects from the db_setup_fixtures file.
5. Make changes to your local that you want in the fixture. Note, you'll need to log in as one of the functional test users if you want to use the interface. You might need to tempoarily go into the database and make them a platform admin depending on what you are doing.
6. Back up your new functional test data with `pg_dump --format=p --data-only notification_api > temp_db_setup_fixtures.sql`
7. Compare the new fixtures file with the existing one and remove any extra rows that people won't want to re-add to their database. For example, Notify service templates, any notifications you might have sent while making the changes, etc.
8. (Optional) revert your local to its previous state with `dropdb notification_api` then recreate with `createdb notification_api` and restore your data with `pg_restore -Ft -d notification_api < ~/Downloads/my_local_db_backup.tar`; Then apply the `temp_db_setup_fixtures.sql` you just updated (you may have to tackle quite a few errors), or open `psql` and just copy-paste the lines from the script that you need.
