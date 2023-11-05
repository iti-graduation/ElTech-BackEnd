# Eltech-app-api

ElTech API Project



to create a local postgres db and user:

psql -U postgres

CREATE USER eltechuser WITH PASSWORD 'eltechpassword';

CREATE DATABASE eltechdb;

GRANT ALL PRIVILEGES ON DATABASE eltechdb TO eltechuser;
GRANT ALL PRIVILEGES ON SCHEMA public TO eltechuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eltechuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eltechuser;
ALTER USER eltechuser CREATEDB;
