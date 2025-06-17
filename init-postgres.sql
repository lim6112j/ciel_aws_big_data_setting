-- Initialize PostgreSQL database for Telegraf metrics

-- Create schema for metrics if it doesn't exist
CREATE SCHEMA IF NOT EXISTS public;

-- Create telegraf user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'telegraf') THEN
        CREATE USER telegraf WITH PASSWORD 'your-postgres-password';
    END IF;
END
$$;

-- Grant permissions to telegraf user
GRANT ALL PRIVILEGES ON SCHEMA public TO telegraf;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO telegraf;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO telegraf;
GRANT ALL PRIVILEGES ON DATABASE metrics TO telegraf;

-- Grant default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO telegraf;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO telegraf;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO telegraf;

-- Enable JSONB extension for better JSON support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a sample table structure that Telegraf will use
-- Note: Telegraf will auto-create tables, but this shows the expected structure
CREATE TABLE IF NOT EXISTS sample_metrics (
    time TIMESTAMPTZ NOT NULL,
    tags JSONB,
    fields JSONB,
    name VARCHAR(255) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sample_metrics_time ON sample_metrics(time);
CREATE INDEX IF NOT EXISTS idx_sample_metrics_name ON sample_metrics(name);
CREATE INDEX IF NOT EXISTS idx_sample_metrics_tags ON sample_metrics USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_sample_metrics_fields ON sample_metrics USING GIN(fields);

-- Create a view for easier querying of metrics
CREATE OR REPLACE VIEW metrics_view AS
SELECT 
    time,
    name as measurement,
    tags,
    fields,
    tags->>'host' as host,
    tags->>'region' as region
FROM sample_metrics
ORDER BY time DESC;
