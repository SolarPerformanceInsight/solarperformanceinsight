This folder contains the database migrations to support the API. Migrations are
written in `/migrations` to use [dbmate](https://github.com/amacneil/dbmate).
Tests of the SQL procedures are found in the `/tests` folder.
The `schema.sql` file contains the entire up to data schema for the tables and
procedures after migrations have been applied. Before committing changes, make
sure to run `dbmate up` on a test database so `schema.sql` is properly updated.
