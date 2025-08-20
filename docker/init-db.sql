-- Database initialization script
-- This runs when the PostgreSQL container first starts

-- Create the main database if it doesn't exist
-- (Already created by POSTGRES_DB environment variable)

-- Create a test database for running tests
CREATE DATABASE sharing_platform_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE sharing_platform TO postgres;
GRANT ALL PRIVILEGES ON DATABASE sharing_platform_test TO postgres;

-- Enable required extensions
\c sharing_platform;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c sharing_platform_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Insert some sample data for development (optional)
\c sharing_platform;

-- This will be populated by the application's migration system