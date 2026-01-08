-- Create the database if it doesn't exist
CREATE DATABASE coffee_shop;

-- Connect to the new database
\c coffee_shop

-- Create a user if it doesn't exist and grant privileges
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'postgres') THEN

      CREATE USER coffee_user WITH PASSWORD 'coffee_password';
END IF;
END
$do$;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE coffee_shop TO coffee_user;

-- Grant all privileges on all tables in the public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO coffee_user;

-- Grant all privileges on all sequences in the public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO coffee_user;

-- Make sure the privileges are set for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO coffee_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO coffee_user;