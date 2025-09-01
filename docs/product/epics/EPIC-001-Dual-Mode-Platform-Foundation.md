# Epic 1: Dual-Mode Platform Foundation

**Epic ID:** EPIC-001  
**Status:** Planned  
**Priority:** Critical  
**Estimated Duration:** 8 weeks  
**Team:** Core Platform Team  

## 🎯 Epic Goal

Transform the single-mode neighborhood-based platform into a flexible dual-mode architecture that enables users to choose between Neighborhood Mode (high verification) and Community Mode (social verification) based on their community type and trust preferences.

## 📊 Business Value

- **Market Expansion**: Increases addressable market from building residents to any Telegram group
- **User Choice**: Provides flexibility in verification levels and community types
- **Competitive Advantage**: First platform to offer both high-trust and casual sharing modes
- **Scalability**: Foundation for exponential growth through group-based adoption

## 🏗️ Technical Architecture

### Event-Driven Dual-Mode Architecture
```python
# Valkey Streams configuration for dual-mode events
DUAL_MODE_STREAMS = {
    'user.mode.transitions': {
        'description': 'User switching between neighborhood/community modes',
        'consumers': ['reputation_service', 'notification_service', 'analytics_service'],
        'retention': '30d',
        'max_length': 100000
    },
    'group.mode.activities': {
        'description': 'Group-specific activities by mode type',
        'consumers': ['food_discovery_service', 'partnership_service'],
        'retention': '7d',
        'max_length': 50000
    },
    'verification.events': {
        'description': 'Verification completion events by mode',
        'consumers': ['user_service', 'trust_service', 'admin_service'],
        'retention': '90d',
        'max_length': 200000
    }
}

class DualModeEventPublisher:
    """Publishes dual-mode related events to Valkey streams."""
    
    async def publish_mode_transition(self, user_id: UUID, from_mode: str, to_mode: str):
        """Publish user mode transition event."""
        event_data = {
            'user_id': str(user_id),
            'from_mode': from_mode,
            'to_mode': to_mode,
            'timestamp': int(time.time()),
            'requires_reverification': to_mode == 'neighborhood'
        }
        
        stream_id = await self.valkey.xadd(
            'user.mode.transitions',
            event_data,
            maxlen=100000,
            approximate=True
        )
        
        # Store local reference for audit trail
        await self.store_transition_event(user_id, from_mode, to_mode, stream_id)
        
        return stream_id
```

### Mode Comparison Framework
| Aspect | Neighborhood Mode | Community Mode |
|--------|------------------|----------------|
| **Target Users** | Building residents, local neighbors | Friends, online communities, hobby groups |
| **Verification** | High (SMS, location, apartment) | Light (Telegram group membership) |
| **Trust Model** | Location-based verification | Social group-based trust |
| **Discovery** | Building-specific | Telegram group-specific |
| **Pickup** | Same building/area | User-coordinated locations |
| **Moderation** | Building admin + platform | Group admin + platform |

### Database Schema Changes
```sql
-- Add mode support to users table
ALTER TABLE users ADD COLUMN sharing_mode VARCHAR(20) DEFAULT 'neighborhood';
ALTER TABLE users ADD COLUMN verification_level VARCHAR(20) DEFAULT 'full';

-- Create community groups table (extends buildings concept)
CREATE TABLE community_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_group_id BIGINT UNIQUE,
    name VARCHAR(255) NOT NULL,
    group_type VARCHAR(20) NOT NULL, -- 'neighborhood' or 'community'
    verification_required BOOLEAN DEFAULT false,
    admin_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Event stream configuration for dual-mode events
CREATE TABLE mode_transition_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    from_mode VARCHAR(20),
    to_mode VARCHAR(20),
    reason TEXT,
    stream_id VARCHAR(100), -- Valkey stream message ID
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 📋 User Stories

### Story 1.1: Mode Selection During Registration
**As a** new user  
**I want to** choose between Neighborhood Mode and Community Mode during registration  
**So that** I can join the appropriate community type for my needs  

**Acceptance Criteria:**
- [ ] Bot presents clear mode selection with explanations
- [ ] Users can switch modes later (with re-verification if needed)
- [ ] Mode choice affects verification requirements
- [ ] Mode is stored in user profile

### Story 1.2: Flexible Verification Levels
**As a** user selecting my community type  
**I want** appropriate verification based on my chosen mode  
**So that** I have the right balance of security and convenience  

**Verification Matrix:**
- **Neighborhood Mode**: SMS verification + building address + apartment number
- **Community Mode**: Telegram group membership + optional location sharing

### Story 1.3: Mode-Appropriate Discovery
**As a** user in either mode  
**I want to** browse food shared within my community scope  
**So that** I can access relevant food sharing opportunities  

**Discovery Logic:**
- **Neighborhood Mode**: Shows food from same building + nearby verified buildings
- **Community Mode**: Shows food from joined Telegram groups only

### Story 1.4: Cross-Mode Compatibility
**As a** platform user  
**I want** both modes to function independently without interference  
**So that** users can have consistent experiences regardless of mode choice  

### Story 1.5: Existing User Migration
**As an** existing neighborhood mode user  
**I want** my account and data preserved during the dual-mode implementation  
**So that** I can continue using the platform without disruption  

## 🔄 User Journey Flows

### Event-Driven Mode Selection Flow
```
Bot Start → Welcome → Mode Selection
                        ↙         ↘
            🏠 Neighborhood Mode   👥 Community Mode
                   ↓                      ↓
            Full Verification      Light Verification
            (SMS + Location)       (Group Membership)
                   ↓                      ↓
         [mode.selected] → Valkey Stream ← [mode.selected]
                               ↓
                    Fan-out to Services:
                    ├── User Service (profile update)
                    ├── Reputation Service (mode context)
                    ├── Food Service (discovery rules)
                    └── Analytics Service (mode metrics)
                   ↓                      ↓
            Building Discovery     Group Discovery
```

### Onboarding Variations

#### Neighborhood Mode Onboarding
1. Phone number (SMS verification)
2. Building address verification
3. Apartment number confirmation
4. Profile completion with dietary preferences
5. Welcome bonus: 10 starter credits

#### Community Mode Onboarding
1. Telegram group membership verification
2. Optional general area for pickup coordination
3. Profile completion (recommended)
4. Welcome bonus: 10 starter credits

## 🧪 Testing Strategy

### Test Scenarios
1. **Mode Selection Testing**
   - Verify mode selection interface appears
   - Test switching between modes
   - Validate mode-specific verification flows

2. **Isolation Testing**
   - Confirm neighborhood users don't see community posts
   - Verify community users don't see neighborhood posts
   - Test admin functions work independently

3. **Migration Testing**
   - Existing users continue functioning
   - Data integrity maintained
   - Performance not degraded

## 📈 Success Metrics

- **User Adoption**: 30% of new users choose Community Mode within first month
- **Retention**: No decrease in existing user retention during migration
- **Performance**: <2 second response times for mode selection and verification
- **Error Rate**: <1% error rate in mode-specific functionality

## 🚧 Implementation Plan

### Phase 1: Core Infrastructure (Weeks 1-3)
- [ ] Database schema updates
- [ ] Mode selection interface
- [ ] Basic dual-mode routing logic

### Phase 2: Verification Systems (Weeks 4-5)
- [ ] Community mode verification (light)
- [ ] Maintain neighborhood mode verification (full)
- [ ] Verification level management

### Phase 3: Discovery & Features (Weeks 6-7)
- [ ] Mode-appropriate food discovery
- [ ] Admin tools for both modes
- [ ] Cross-mode compatibility testing

### Phase 4: Migration & Launch (Week 8)
- [ ] Existing user migration
- [ ] Performance optimization
- [ ] Launch preparation and rollout

## 🔗 Dependencies

- **Database Team**: Schema migration and optimization
- **Bot Development**: Telegram integration updates
- **UI/UX Team**: Mode selection interface design
- **QA Team**: Comprehensive testing of both modes

## ⚠️ Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|---------|------------|------------|
| User confusion between modes | High | Medium | Clear UI/UX design, comprehensive onboarding |
| Data migration issues | High | Low | Extensive testing, rollback procedures |
| Performance degradation | Medium | Medium | Load testing, database optimization |
| Feature complexity | Medium | High | Phased rollout, feature flags |

## 📚 Related Documents

- [Technical Architecture Specification](../technical/dual-mode-architecture.md)
- [User Experience Guidelines](../design/dual-mode-ux.md)
- [Migration Plan](../operations/dual-mode-migration.md)
- [Testing Strategy](../testing/dual-mode-testing.md)

---

**Epic Owner:** Product Manager  
**Technical Lead:** Senior Backend Developer  
**Created:** 2025-01-01  
**Last Updated:** 2025-01-01