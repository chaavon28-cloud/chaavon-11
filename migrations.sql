-- Institutional Intelligence Platform - Comprehensive Migration
-- Targets: Analyst Enrichment, User Archiving, Cloud Storage

-- 1. ENHANCE INTELLIGENCE REQUESTS TABLE
ALTER TABLE intelligence_requests 
ADD COLUMN IF NOT EXISTS analyst_narrative TEXT,
ADD COLUMN IF NOT EXISTS sanctions_findings TEXT,
ADD COLUMN IF NOT EXISTS ownership_analysis TEXT,
ADD COLUMN IF NOT EXISTS ais_behavior_review TEXT,
ADD COLUMN IF NOT EXISTS risk_indicators JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS shell_company_indicators TEXT,
ADD COLUMN IF NOT EXISTS sts_transfer_observations TEXT,
ADD COLUMN IF NOT EXISTS compliance_recommendation TEXT,
ADD COLUMN IF NOT EXISTS report_storage_url TEXT,
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;

-- 2. ENHANCE USER ACCESS TABLE
ALTER TABLE users_access
ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 3. INDEXING FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_requests_archived ON intelligence_requests(archived);
CREATE INDEX IF NOT EXISTS idx_users_archived ON users_access(is_archived);
CREATE INDEX IF NOT EXISTS idx_requests_status ON intelligence_requests(status);
