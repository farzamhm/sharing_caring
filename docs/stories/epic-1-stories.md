# Epic 1 Stories: Admin Dashboard

## Story 1.1: Admin Authentication & Basic Dashboard Shell

### Story Title
Admin Authentication & Basic Dashboard Shell - Brownfield Addition

### User Story
As a **platform administrator**,  
I want **secure web-based admin access with a basic dashboard showing system health**,  
So that **I can monitor the platform's operational status without requiring direct system access**.

### Story Context

**Existing System Integration:**
- Integrates with: FastAPI backend, existing /health endpoint, JWT authentication patterns
- Technology: Python/FastAPI, Jinja2 templates, existing auth middleware
- Follows pattern: Existing API authentication and route patterns
- Touch points: /health endpoint, database connections, Redis sessions

### Acceptance Criteria

**Functional Requirements:**
1. Admin can login with secure credentials and receive JWT session token
2. Admin dashboard displays system health status from existing /health endpoint
3. Dashboard shows navigation menu with placeholders for future admin sections

**Integration Requirements:**
4. Existing API authentication patterns continue to work unchanged
5. New admin routes follow existing FastAPI route structure and async patterns
6. Integration with /health endpoint maintains current endpoint behavior

**Quality Requirements:**
7. Admin authentication is covered by security tests and rate limiting
8. Admin dashboard documentation added to deployment guide
9. No regression in existing bot or API functionality verified

### Technical Notes
- **Integration Approach:** New admin routes in separate admin.py module, reuses existing auth patterns
- **Existing Pattern Reference:** Follow existing FastAPI route decorators and JWT middleware patterns
- **Key Constraints:** Admin access must be isolated from user-facing functionality

### Definition of Done
- [ ] Admin login page with secure authentication
- [ ] JWT session management for admin users  
- [ ] Basic dashboard template with system health display
- [ ] Navigation structure for future admin features
- [ ] Security tests for admin authentication
- [ ] No impact on existing bot/API functionality

---

## Story 1.2: Business Metrics Visualization

### Story Title
Business Metrics Visualization Dashboard - Brownfield Addition

### User Story
As a **platform administrator**,  
I want **visual dashboards showing key business metrics from our existing data**,  
So that **I can monitor platform usage, food exchanges, and user engagement trends**.

### Story Context

**Existing System Integration:**
- Integrates with: Elasticsearch business metrics indices, existing metrics collection
- Technology: FastAPI backend, Chart.js/similar for visualization, Elasticsearch queries
- Follows pattern: Existing async Elasticsearch query patterns from architecture
- Touch points: Business metrics indices, existing metrics collection code

### Acceptance Criteria

**Functional Requirements:**
1. Dashboard displays daily active user trends from Elasticsearch business metrics
2. Food exchange volume and success rates shown with simple charts
3. Real-time refresh capability to update metrics without page reload

**Integration Requirements:**
4. Existing business metrics collection continues unchanged
5. New Elasticsearch queries follow existing async query patterns
6. Integration with metrics indices maintains current data structure

**Quality Requirements:**
7. Metrics queries are optimized and cached appropriately
8. Dashboard performance does not impact existing system performance
9. No changes to existing business metrics collection verified

### Technical Notes
- **Integration Approach:** Use existing AsyncElasticsearch client patterns for queries
- **Existing Pattern Reference:** Follow business metrics collection code from architecture document
- **Key Constraints:** Read-only access to metrics data, no modification of collection process

### Definition of Done
- [ ] Daily active users chart with 30-day trend
- [ ] Food exchange volume visualization
- [ ] Success rate metrics display
- [ ] Auto-refresh functionality
- [ ] Query performance optimization
- [ ] Existing metrics collection unaffected

---

## Story 1.3: User Report Management Interface

### Story Title  
User Report Management Interface - Brownfield Addition

### User Story
As a **platform administrator**,  
I want **an interface to view and manage user-submitted safety reports**,  
So that **I can respond to community issues and maintain platform safety standards**.

### Story Context

**Existing System Integration:**
- Integrates with: User report data models, existing user lookup APIs
- Technology: FastAPI backend, existing database queries, user management patterns
- Follows pattern: Existing SQLAlchemy async query patterns
- Touch points: User table, report table (from architecture schema), existing user service

### Acceptance Criteria

**Functional Requirements:**
1. Admin can view list of submitted user reports with status filtering
2. Admin can mark reports as "reviewed" or "resolved" with timestamp tracking
3. Basic user lookup capability to see user profile context for reports

**Integration Requirements:**
4. Existing user data access patterns continue unchanged
5. New report management follows existing SQLAlchemy async query patterns  
6. Integration with user service maintains current API behavior

**Quality Requirements:**
7. Report management actions are audit-logged appropriately
8. User privacy protection maintained (minimal PII exposure)
9. No impact on user-facing report submission functionality

### Technical Notes
- **Integration Approach:** Extend existing user service patterns for report queries
- **Existing Pattern Reference:** Follow user data access patterns from architecture service layer
- **Key Constraints:** Admin actions must be audit-logged, respect user privacy boundaries

### Definition of Done
- [ ] Report list view with filtering by status
- [ ] Report detail view with context
- [ ] Status update functionality (reviewed/resolved)
- [ ] Basic user lookup for support context
- [ ] Audit logging of admin actions
- [ ] User privacy protections verified