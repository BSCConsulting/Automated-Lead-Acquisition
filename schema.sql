-- ============================================================================
-- Supabase / PostgreSQL Database Schema for Cosmetics Distribution Platform
-- ============================================================================

-- Enable pgcrypto extension for gen_random_uuid() if not enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. Leads Master Table (Phase 1 & 2)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leads_master (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name TEXT NOT NULL,
    segment TEXT NOT NULL, -- e.g., 'Salons', 'Spas', 'Kirana', 'Pharmacies', 'Women Hostel', 'College'
    state TEXT NOT NULL,   -- e.g., 'Andhra Pradesh', 'Telangana'
    pincode VARCHAR(10) NOT NULL,
    address_raw TEXT,
    primary_phone VARCHAR(20),
    phone_is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    website TEXT,
    google_maps_url TEXT,
    social_profiles JSONB DEFAULT '{}'::jsonb,
    acquisition_source TEXT DEFAULT 'harvester',
    lead_status TEXT NOT NULL DEFAULT 'New', -- 'New', 'Contacted', 'Qualified', 'Converted', 'Rejected'
    dedup_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA-256 hash of business_name + primary_phone (or pincode)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Leads Master
CREATE INDEX IF NOT EXISTS idx_leads_pincode ON leads_master(pincode);
CREATE INDEX IF NOT EXISTS idx_leads_segment ON leads_master(segment);
CREATE INDEX IF NOT EXISTS idx_leads_state ON leads_master(state);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads_master(lead_status);
CREATE INDEX IF NOT EXISTS idx_leads_dedup_hash ON leads_master(dedup_hash);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_leads_updated_at ON leads_master;
CREATE TRIGGER set_leads_updated_at
    BEFORE UPDATE ON leads_master
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 2. Catalog Items Table (Phase 0: CatalogGenius Vision Ingestion)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_name TEXT NOT NULL,
    canonical_title TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    variant_size TEXT,
    mrp NUMERIC(10, 2),
    wholesale_cost NUMERIC(10, 2),
    b2b_trade_price NUMERIC(10, 2),
    extracted_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_catalog_category ON catalog_items(category);
CREATE INDEX IF NOT EXISTS idx_catalog_brand ON catalog_items(brand);

-- ----------------------------------------------------------------------------
-- 3. Social Posts Table (Phase 3: Social Media Automation Agent)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_type TEXT NOT NULL CHECK (campaign_type IN ('D2C', 'B2B')),
    visual_asset_prompt TEXT NOT NULL,
    copy_english TEXT NOT NULL,
    copy_telugu TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending Approval' CHECK (status IN ('Pending Approval', 'Approved', 'Published', 'Rejected')),
    scheduled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posts_type ON social_posts(campaign_type);

DROP TRIGGER IF EXISTS set_social_updated_at ON social_posts;
CREATE TRIGGER set_social_updated_at
    BEFORE UPDATE ON social_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
