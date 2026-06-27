-- PostgreSQL initialization script
-- Runs once when the Docker postgres container is first created.
-- Alembic migrations handle all schema creation; this script only sets up
-- database-level configuration and extensions that must exist before migrations run.

-- Enable pgcrypto for gen_random_uuid() (used as default PK values)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enable pg_stat_statements for query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Set timezone to UTC for all connections to this database
ALTER DATABASE bsm SET timezone TO 'UTC';

-- Ensure the app role exists with limited privileges (no SUPERUSER, no CREATEDB)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bsm_app') THEN
        CREATE ROLE bsm_app WITH LOGIN PASSWORD 'changeme_in_production';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE bsm TO bsm_app;
