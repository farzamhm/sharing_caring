# Story 009.02: Database Performance Optimization (ENHANCED FOR AI)

**Epic:** EPIC-009 - Platform Scalability & Performance  
**Priority:** 🔴 CRITICAL - MUST COMPLETE FIRST  
**Story Points:** 8  
**Sprint:** 1  
**AI Developer Complexity:** HIGH - Follow exact specifications  

---

## 🤖 AI DEVELOPER: READ THIS FIRST

**This story implements the database foundation for the dual-mode platform. ALL other stories depend on this being completed correctly.**

**CRITICAL FILES TO READ:**
- `/docs/product/epics/EPIC-001-Dual-Mode-Platform-Foundation.md` (database schema)
- `/docs/product/epics/EPIC-004-Global-Reputation-System.md` (reputation tables)  
- `/docs/product/epics/EPIC-009-Platform-Scalability-Performance.md` (performance specs)

---

## User Story
**As a** user of the platform  
**I want** fast data retrieval and updates (sub-2 second response times)  
**So that** I can quickly browse food, make claims, and interact with the community  

---

## 🎯 EXACT IMPLEMENTATION REQUIREMENTS

### **STEP 1: Execute Database Schema Changes**

**File to create:** `alembic/versions/001_dual_mode_foundation.py`

```sql
-- EXACT SQL - DO NOT MODIFY
-- Add mode support to users table
ALTER TABLE users ADD COLUMN sharing_mode VARCHAR(20) DEFAULT 'neighborhood';
ALTER TABLE users ADD COLUMN verification_level VARCHAR(20) DEFAULT 'full';

-- Create community groups table
CREATE TABLE community_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_group_id BIGINT UNIQUE,
    name VARCHAR(255) NOT NULL,
    group_type VARCHAR(20) NOT NULL, -- 'neighborhood' or 'community'
    verification_required BOOLEAN DEFAULT false,
    admin_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create global reputation table
CREATE TABLE user_global_reputation (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    overall_score DECIMAL(4,2) DEFAULT 75.00,
    trust_level VARCHAR(20) DEFAULT 'developing',
    total_food_shared INTEGER DEFAULT 0,
    total_food_claimed INTEGER DEFAULT 0,
    total_exchanges_completed INTEGER DEFAULT 0,
    total_groups_participated INTEGER DEFAULT 0,
    avg_food_rating DECIMAL(3,2) DEFAULT 0.00,
    avg_recipient_rating DECIMAL(3,2) DEFAULT 0.00,
    reliability_score DECIMAL(4,2) DEFAULT 75.00,
    reported_incidents INTEGER DEFAULT 0,
    resolved_disputes INTEGER DEFAULT 0,
    community_contributions INTEGER DEFAULT 0,
    account_age_days INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT NOW(),
    reputation_updated_at TIMESTAMP DEFAULT NOW(),
    peak_reputation DECIMAL(4,2) DEFAULT 75.00,
    reputation_trend VARCHAR(10) DEFAULT 'stable',
    last_stream_event_id VARCHAR(100),
    stream_lag_seconds INTEGER DEFAULT 0,
    reputation_sync_status VARCHAR(20) DEFAULT 'synced'
);

-- Create reputation events table with stream integration
CREATE TABLE reputation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    impact_score DECIMAL(5,2) NOT NULL,
    previous_score DECIMAL(4,2) NOT NULL,
    new_score DECIMAL(4,2) NOT NULL,
    group_id UUID REFERENCES community_groups(id) NULL,
    related_exchange_id UUID NULL,
    description TEXT,
    stream_id VARCHAR(100),
    stream_partition INTEGER,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Event stream configuration for dual-mode events
CREATE TABLE mode_transition_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    from_mode VARCHAR(20),
    to_mode VARCHAR(20),
    reason TEXT,
    stream_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stream processing checkpoints
CREATE TABLE event_stream_checkpoints (
    consumer_group VARCHAR(100) NOT NULL,
    stream_name VARCHAR(100) NOT NULL,
    last_processed_id VARCHAR(50) NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW(),
    lag_seconds INTEGER DEFAULT 0,
    PRIMARY KEY (consumer_group, stream_name)
);
```

### **STEP 2: Create EXACT Performance Indexes**

**File to create:** `alembic/versions/002_performance_indexes.py`

```sql
-- CRITICAL PERFORMANCE INDEXES - IMPLEMENT ALL OF THESE
CREATE INDEX CONCURRENTLY idx_food_posts_active_location 
ON food_posts (status, pickup_time, group_id) 
WHERE status = 'available' AND pickup_time > NOW();

CREATE INDEX CONCURRENTLY idx_users_reputation_active
ON user_global_reputation (trust_level, overall_score, last_activity)
WHERE last_activity > NOW() - INTERVAL '30 days';

CREATE INDEX CONCURRENTLY idx_users_sharing_mode
ON users (sharing_mode, verification_level, created_at);

CREATE INDEX CONCURRENTLY idx_community_groups_telegram
ON community_groups (telegram_group_id, group_type, admin_user_id);

CREATE INDEX CONCURRENTLY idx_reputation_events_user_recent
ON reputation_events (user_id, created_at DESC)
WHERE created_at > NOW() - INTERVAL '90 days';

CREATE INDEX CONCURRENTLY idx_reputation_events_stream
ON reputation_events (stream_partition, stream_id, processed_at);

CREATE INDEX CONCURRENTLY idx_exchanges_group_status
ON exchanges (food_id, status, created_at)
WHERE status IN ('pending', 'confirmed', 'completed');

-- Composite index for food discovery by mode
CREATE INDEX CONCURRENTLY idx_food_posts_discovery
ON food_posts (group_id, status, pickup_time, created_at)
WHERE status = 'available';
```

### **STEP 3: Create Materialized Views**

**File to create:** `src/models/materialized_views.py`

```sql
-- Materialized view for group activity summary
CREATE MATERIALIZED VIEW group_activity_summary AS
SELECT 
    g.id as group_id,
    g.name as group_name,
    g.group_type,
    COUNT(DISTINCT u.id) as active_members,
    COUNT(DISTINCT fp.id) as food_posts_30d,
    AVG(r.stars) as avg_rating,
    COUNT(DISTINCT e.id) as successful_exchanges_30d,
    MAX(fp.created_at) as last_food_post
FROM community_groups g
LEFT JOIN users u ON u.sharing_mode = 'community'
LEFT JOIN food_posts fp ON g.id = fp.group_id AND fp.created_at > NOW() - INTERVAL '30 days'
LEFT JOIN exchanges e ON fp.id = e.food_id AND e.status = 'completed' 
    AND e.created_at > NOW() - INTERVAL '30 days'
LEFT JOIN ratings r ON e.id = r.exchange_id AND r.created_at > NOW() - INTERVAL '30 days'
GROUP BY g.id, g.name, g.group_type;

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_group_activity_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY group_activity_summary;
END;
$$ LANGUAGE plpgsql;

-- Schedule hourly refresh (implement in cron or scheduler)
```

### **STEP 4: Implement Connection Pooling**

**File to create:** `src/core/database.py` (enhance existing)

```python
# EXACT CONFIGURATION - DO NOT CHANGE THESE VALUES
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "pool_pre_ping": True,
    "echo": False,  # Set to True only for debugging
}

# Read replica configuration
READ_REPLICA_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "pool_pre_ping": True,
}
```

---

## ✅ ACCEPTANCE CRITERIA (ALL MUST BE MET)

### **Database Schema:**
- [ ] All tables created with exact column names and types as specified
- [ ] All indexes created with exact names and definitions
- [ ] Foreign key relationships properly established
- [ ] Default values set correctly for all columns

### **Performance Benchmarks:**
- [ ] Food post queries execute in <200ms (average)
- [ ] User reputation lookups execute in <100ms (average)  
- [ ] Group discovery queries execute in <300ms (average)
- [ ] Database connection pool maintains 90%+ efficiency

### **Indexes Verification:**
- [ ] All 8 performance indexes created successfully
- [ ] Query execution plans show index usage for critical queries
- [ ] No full table scans on large tables (>1000 rows)

### **Materialized Views:**
- [ ] Group activity summary view refreshes successfully
- [ ] View queries execute in <50ms
- [ ] Automated refresh mechanism working

---

## 🧪 TESTING REQUIREMENTS

### **Migration Testing:**
```bash
# EXACT COMMANDS TO RUN
alembic upgrade head
python -m pytest tests/test_database_migrations.py
python -m src.scripts.verify_schema.py
```

### **Performance Testing:**
```bash
# Load test with exact criteria
python -m src.scripts.performance_test.py --queries 1000 --max-time 200ms
```

### **Index Verification:**
```sql
-- Run these queries to verify indexes work
EXPLAIN ANALYZE SELECT * FROM food_posts 
WHERE status = 'available' AND pickup_time > NOW() 
AND group_id = 'some-uuid';

-- Should show "Index Scan" not "Seq Scan"
```

---

## 🚨 CRITICAL WARNINGS FOR AI DEVELOPERS

❌ **ABSOLUTELY DO NOT:**
- Change any column names or types from the specification
- Skip any of the 8 required indexes  
- Use different default values than specified
- Modify the materialized view query structure

✅ **MUST DO:**
- Run all migration scripts in order
- Verify every index is created successfully
- Test all performance benchmarks pass
- Confirm foreign key relationships work

⚠️ **IF THIS FAILS:**
All other stories in the backlog will fail because they depend on this exact database structure.

---

## 📋 COMPLETION CHECKLIST

**Before marking story complete:**
- [ ] Database migration runs without errors
- [ ] All 8 indexes created and verified  
- [ ] Materialized views refresh successfully
- [ ] Performance benchmarks meet requirements (<200ms avg query time)
- [ ] Connection pooling configuration active
- [ ] All tests pass (unit + integration)
- [ ] Schema matches epic specifications exactly

**Story is complete when:** All checkboxes above are checked and verified by running the test suite successfully.