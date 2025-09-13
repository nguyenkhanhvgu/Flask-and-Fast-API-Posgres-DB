-- Initial database setup for Web Frameworks Tutorial
-- This file will be executed when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial tables (basic structure)
-- Full schema will be created by Alembic migrations

-- Verify database setup
SELECT 'Database initialized successfully' as status;