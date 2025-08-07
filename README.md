# notifications-functional-tests

The tests are:

- `notifications/`: tests of the Notify user interface and API (notifications.service.gov.uk)
- `document_download/`: tests of the Documents user interface and API (documents.service.gov.uk)
- `provider_delivery/`: tests for delivery of notifications (Staging and Production only)

These tests are run against staging and production using Concourse. We run a full set of tests on staging but only a smaller set of tests, also known as smoke tests, on production.

The Concourse jobs are defined in our [infrastructure repo](https://github.com/alphagov/notifications-aws/blob/master/concourse/templates/functional-tests.yml.j2).

## Uses

These tests are not intended to be used for load testing.

## Installation

```shell
brew install --cask chromedriver # needs to be >= v2.32
brew install zbar  # Used for QR code reading

# https://github.com/npinchot/zbar/issues/3
mkdir -p ~/lib
ln -s $(brew --prefix zbar)/lib/libzbar.dylib ~/lib/libzbar.dylib

make bootstrap # install dependencies, etc.
```

Note: when you run the tests for the first time on a Mac, **you may need to authorise `chromedriver` in your security settings** ("System Preferences > Security & Privacy > General").

## Running tests

Note, there is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

### Running the tests against your local development environment

**Note: this is currently only supported for `notifications/` and `document_download/` tests.** See the next section if you want to run the `provider_delivery/` tests locally.

If you are running Notify locally using docker-compose via [notifications-local](https://www.github.com/alphagov/notifications-local), then you need to set the following environment variables:

```shell
export FUNCTIONAL_TESTS_API_HOST=http://notify-api.localhost:6011
export FUNCTIONAL_TESTS_ADMIN_HOST=http://notify.localhost:6012
```

Populate the local database with fixture data using the make target, this will call database fixtures located in notifications-api:

```shell
make generate-local-dev-db-fixtures
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
    - Flask app
  - [notifications-antivirus](https://github.com/alphagov/notifications-antivirus)
    - Celery

- If you're testing the Documents user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api) (Flask app only)
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
  - [document-download-api](https://github.com/alphagov/document-download-api)
  - [document-download-frontend](https://github.com/alphagov/document-download-frontend)

Fetch the required environment variables from `notifications-credentials`:

```
pass credentials/functional-tests/local-functional > environment_local.sh
```

Then source this script and run the tests:

```
source environment_local.sh

# run all the tests
make test

# run a specific test
pytest tests/notifications/functional_tests/test_seeded_user.py

# run a specific test without headless
pytest tests/notifications/functional_tests/test_seeded_user.py --no-headless
```

### Running the tests from your local machine against a dev environment or staging

- Choose a target environment:
  ```sh
  ENVIRONMENT="staging" # or dev-a, etc.
  ```
- Find the AWS account ID of the target account, either with `gds aws notify-${ENVIRONMENT} -d` or:
  ```sh
  AWS_ACCOUNT_ID=$(gds aws notify-${ENVIRONMENT} -- aws sts get-caller-identity --query Account --output text)
  ```
- Fetch the environment setup script from SSM:
  ```sh
  gds aws notify-${ENVIRONMENT}-admin -- aws ssm get-parameter \
    --with-decryption \
    --name "arn:aws:ssm:eu-west-1:${AWS_ACCOUNT_ID}:parameter/notify/${ENVIRONMENT}/functional-tests/generated/environment" | \
  jq -r .Parameter.Value > \
  environment_${ENVIRONMENT}.sh
  ```
- Source the environment setup script, then run the tests:
  ```sh
  source environment_${ENVIRONMENT}.sh

  # run specific tests, for example:
  pytest tests/document_download/functional_tests
  ```

### Running tests in parallel

We can reduce the duration of the test suite by running some tests in parallel.

We use the pytest [x-dist plugin](https://pypi.org/project/pytest-xdist/) to support running tests in parallel automatically. The number of test runners is determined automatically using the `pytest -n auto` option. This will be set to the number of CPUs available on the test machine.

Each test runner launches a separate selenium/chromedriver instance so browser state is isolated between runners.

#### Defining parallel groups

We execute tests in parallel groups using the `pytest --dist loadgroup` option. This allows us to group tests by the authenticated user type or other logical domain - this is useful for functional tests that rely on a particular state of a real user environment during execution.

Parallel tests executed using the same user type can cause race conditions and interfere with other tests. Tests belonging to different groups are executed in parallel. Each test within the same group is executed sequentially by the same test runner.

We use the following annotations on test methods to define the groups:

```python
@pytest.mark.xdist_group(name="registration-flow")
@pytest.mark.xdist_group(name="api-client")
@pytest.mark.xdist_group(name="seeded-email")
@pytest.mark.xdist_group(name="api-letters")
```

More groups generally equals better parallelisation (limited by test runner count). However, in the case of functional tests, increased parallelisation increases the risk of side effects and race conditions in the shared environment unless grouped carefully.

## Database fixtures

For the functional tests to pass in any environment, they require certain database fixtures to exist.

For your local environment, dev environments, and staging, these fixtures are now generated using the custom flask command functional-test-fixtures (defined in [notifications-api/app/functional_tests_fixtures/__init__.py](https://github.com/alphagov/notifications-api/blob/main/app/functional_tests_fixtures/__init__.py)). The command will create all the database rows required for the funcitonal tests in an idempotent way and output an environment file the functional tests can use to execute against the environment. There are [instructions on how to update the local database fixtures](docs/update-local-db-fixtures.md).

For our production environment, these fixtures are not yet stored in code, but were put in place manually by our developers.


## Database cleanup in non-production environments

> **Warning**: These steps were originally designed to be run in preview. They have been updated to theoretically be suitable to run against staging or a dev environment, but have **not yet been tested**.

To purge test data from a non-production environment (i.e. staging):

1. Take the snapshot of notify-db in rds and also take database dump locally. See [DB-Commands](https://github.com/alphagov/notifications-manuals/wiki/DB-Commands) for the database dump and restore.
2. Pause deployment pipeline for the environment.
3. ssh into ecs `api-web` service.
4. Run `flask command purge-functional-test-data -u notify-tests-preview` to delete user data objects. 
  * note: takes a while! multiple hours!
5. Manually delete organisation 'Functional Test Org'.
6. Unpause the pipeline and manually trigger `start-deploy` - as part of the deploy, the functional test fixtures should be recreated.

To revert the process, restore the database from your local dump. If that does not work then follow [these steps](https://docs.publishing.service.gov.uk/manual/howto-backup-and-restore-in-aws-rds.html) to restore from an RDS snapshot.


## Pre-commit

We use [pre-commit](https://pre-commit.com/) to ensure that committed code meets basic standards for formatting, and will make basic fixes for you to save time and aggravation.

Install pre-commit system-wide with, eg `brew install pre-commit`. Then, install the hooks in this repository with `pre-commit install --install-hooks`.


## Further documentation

- [Updating local database fixtures](docs/update-local-db-fixtures.md)
- [Style guide](docs/style-guide.md)
