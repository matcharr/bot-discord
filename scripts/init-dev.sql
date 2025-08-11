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
    RAISE NOTICE 'Database botdb_dev initialized successfully!';
    RAISE NOTICE 'User: botuser';
    RAISE NOTICE 'Extensions installed: uuid-ossp, pg_trgm';
END $$;