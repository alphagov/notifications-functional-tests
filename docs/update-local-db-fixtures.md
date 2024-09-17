# Updating local database fixtures

Sometimes we need to add new fixtures to our functional tests setup. When we do that, it is good to update db_fixtures/local.sql with those new fixtures.
We do this work so that it's easier for new devs to set up and so we can maintain consistency across local environments.

Below please find a step-by-step guide for updating db_fixtures/local.sql:

1. Back up your local database with `pg_dump --format=t notification_api > ~/Downloads/my_local_db_backup.tar`
2. Drop your local db with `dropdb notification_api`
3. Run `make bootstrap` in the notifications-api repo to set up the database.
4. Update the function apply_fixtures() in [notifications-api/app/functional_tests_fixtures/__init__.py](https://github.com/alphagov/notifications-api/blob/main/app/functional_tests_fixtures/__init__.py) to make changes to the fixtures. Fixtures should be added using the API in an idempotent way.
5. Apply the updated fixtures using `make generate-local-dev-db-fixtures`.

If you need to copy some fixtures to the preview environment, you can dump the local database using `pg_dump --format=p --data-only notification_api > temp_db_setup_fixtures.sql` and extract individual database entries, for example:

```sql
--log into preview
--open psql session

--copy a line that you need, for example:
COPY permissions (id, service_id, user_id, permission, created_at) FROM stdin;
307aaac1-66b0-48b1-aff1-7029be941a03	8e1d56fa-12a8-4d00-bed2-db47180bed0a	1048af40-45f6-4249-a670-df72ba3352d7	approve_broadcasts	2021-07-14 14:53:00.409891

```
