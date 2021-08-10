# Updating db_setup_fixtures.sql

Sometimes we need to add new fixtures to our functional tests setup. When we do that, it is good to update db_setup_fixtures.sql with those new fixtures.
We do this work so that it's easier for new devs to set up and so we can maintain consistency across local environments.

Below please find a step-by-step guide for updating db_setup_fixtures.sql:

1. Back up your local database with `pg_dump --format=t notification_api > ~/Downloads/my_local_db_backup.tar`
2. Drop your local db with `dropdb notification_api`
3. Run `make bootstrap` in the notifications-api repo to set up the database.
4. Run `psql notification_api --file=db_setup_fixtures.sql` to get existing db objects from the db_setup_fixtures file.
5. Make changes to your local that you want in the fixture. Note, you'll need to log in as one of the functional test users if you want to use the interface. You might need to tempoarily go into the database and make them a platform admin depending on what you are doing.
6. Back up your new functional test data with `pg_dump --format=p --data-only notification_api > temp_db_setup_fixtures.sql`
7. Compare the new fixtures file with the existing one and remove any extra rows that people won't want to re-add to their database. For example, Notify service templates, any notifications you might have sent while making the changes, etc.
8. (Optional) revert your local to its previous state with `dropdb notification_api` then recreate with `createdb notification_api` and restore your data with `pg_restore -Ft -d notification_api < ~/Downloads/my_local_db_backup.tar`; Then apply the `temp_db_setup_fixtures.sql` you just updated (you may have to tackle quite a few errors), or open `psql` and just copy-paste the lines from the script that you need.
9. When tests using the new fixtures are ready, add the new db rows to preview environment by copying the lines you need from the db_setup_fixtures.sql, for example:

```sql
--log into preview
--open psql session

--copy a line that you need, for example:
COPY permissions (id, service_id, user_id, permission, created_at) FROM stdin;
307aaac1-66b0-48b1-aff1-7029be941a03	8e1d56fa-12a8-4d00-bed2-db47180bed0a	1048af40-45f6-4249-a670-df72ba3352d7	approve_broadcasts	2021-07-14 14:53:00.409891

```
