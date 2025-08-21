-- Development database initialization script
-- Executed automatically on first PostgreSQL container startup

-- Create useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create test user (optional)
-- CREATE USER testuser WITH PASSWORD 'testpass';
-- GRANT ALL PRIVILEGES ON DATABASE botdb_dev TO testuser;

-- Initialization log
DO $$
BEGIN
DO $
BEGIN
    RAISE NOTICE 'Database % initialized successfully!', current_database();
    RAISE NOTICE 'User: %', current_user;
    RAISE NOTICE 'Extensions installed: %',
      (SELECT string_agg(extname, ', ') FROM pg_extension);
END $;
END $$;
