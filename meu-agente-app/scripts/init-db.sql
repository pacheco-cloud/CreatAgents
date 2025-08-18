-- scripts/init-db.sql
-- Database initialization script for PostgreSQL in Docker

-- Create user and database (if not exists)
DO $$
BEGIN
    -- Create user if not exists
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'agente_user') THEN
        CREATE USER agente_user WITH PASSWORD 'agente_pass';
    END IF;
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE agente_db TO agente_user;
    ALTER USER agente_user CREATEDB;
    
    -- Grant schema privileges
    GRANT ALL ON SCHEMA public TO agente_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agente_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agente_user;
    
    -- Set default privileges for future tables
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO agente_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO agente_user;
    
END $$;

-- Enable extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create a simple health check function
CREATE OR REPLACE FUNCTION public.health_check()
RETURNS TEXT AS $$
BEGIN
    RETURN 'Database is healthy!';
END;
$$ LANGUAGE plpgsql;