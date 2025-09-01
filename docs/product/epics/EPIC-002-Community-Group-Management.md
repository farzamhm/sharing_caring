# Epic 2: Community Group Management System

**Epic ID:** EPIC-002  
**Status:** Planned  
**Priority:** Critical  
**Estimated Duration:** 6 weeks  
**Team:** Community Features Team  

## 🎯 Epic Goal

Create a sophisticated group management system with admin controls, member lifecycle management, pseudonym-based privacy protection, and single bot instance enforcement for Telegram group-based food sharing.

## 📊 Business Value

- **Privacy Protection**: Pseudonymous system protects user identity across groups
- **Group Governance**: Clear admin structure prevents conflicts and ensures quality
- **Scalability**: Each group is self-contained and self-managed
- **Legal Protection**: Disclaimer system reduces platform liability
- **User Trust**: Controlled environment builds confidence in food sharing

## 🏗️ Technical Architecture

### Core Components
```
📱 Telegram Group
├── 🤖 Single Bot Instance (enforced)
├── 👑 Admin (first starter, permanent)
├── 📋 Group Profile (custom name + description)
├── 👥 Members (pseudonymous participation)
│   ├── ✅ Disclaimer accepted → Bot enabled
│   └── ❌ Disclaimer declined → Bot disabled
└── 🍕 Food Posts (visible to group members)
```

### Database Schema
```sql
-- Enhanced community groups
CREATE TABLE community_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_group_id BIGINT UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    privacy_level VARCHAR(20) DEFAULT 'semi_private',
    max_members INTEGER DEFAULT 1000,
    admin_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Member disclaimer and status tracking
CREATE TABLE group_member_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES community_groups(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pseudonym VARCHAR(50) NOT NULL,
    disclaimer_accepted BOOLEAN DEFAULT false,
    disclaimer_version VARCHAR(10) DEFAULT '1.0',
    accepted_at TIMESTAMP NULL,
    bot_access_enabled BOOLEAN DEFAULT false,
    member_role VARCHAR(20) DEFAULT 'member', -- admin/moderator/member
    joined_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    UNIQUE(group_id, user_id),
    UNIQUE(group_id, pseudonym)
);

-- Bot instance control
CREATE TABLE group_bot_instances (
    telegram_group_id BIGINT PRIMARY KEY,
    group_id UUID REFERENCES community_groups(id) ON DELETE CASCADE,
    admin_user_id UUID REFERENCES users(id),
    bot_status VARCHAR(20) DEFAULT 'active',
    instance_token VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_heartbeat TIMESTAMP DEFAULT NOW()
);
```

## 📋 User Stories

### Story 2.1: Group Creation & Admin Assignment
**As a** Telegram group member  
**I want to** start the food sharing bot for the first time in my group  
**So that** I become the group admin and set up food sharing for my community  

**Acceptance Criteria:**
- [ ] First user to run /start becomes permanent admin
- [ ] Bot creates group profile with default settings
- [ ] Admin gets access to admin dashboard
- [ ] Bot instance prevents duplicate setups

### Story 2.2: Member Disclaimer System
**As a** new group member  
**I want to** receive and accept the food sharing disclaimer  
**So that** I can access bot features while understanding the risks  

**Disclaimer Flow:**
```
User joins group → Bot detects → Shows disclaimer
                                     ↓
                          "⚠️ FOOD SHARING DISCLAIMER ⚠️
                          
By using this bot, you acknowledge:
• You share food at your own risk
• Platform is not liable for food safety
• You verify food quality before consuming
• You coordinate pickups directly with sharers
• Group admins set community guidelines
• Report issues through proper channels

Type 'ACCEPT' to continue or 'DECLINE' to opt out"
                                     ↓
           ACCEPT → User enabled    DECLINE → User blocked
```

### Story 2.3: Pseudonym Generation & Privacy
**As a** group member  
**I want** an automatically generated pseudonym  
**So that** my real identity is protected while participating in food sharing  

**Pseudonym Algorithm:**
```python
def generate_group_pseudonym(username: str, group_name: str) -> str:
    user_prefix = username[:3].lower()
    group_prefix = group_name.replace(" ", "")[:3].lower()
    
    # Generate deterministic but private suffix
    hash_input = f"{username}-{group_name}-{SECRET_SALT}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:4]
    
    return f"{user_prefix}{group_prefix}{hash_suffix}"
    
# Example: Username: "john_doe", Group: "Office Foodies" 
# → Pseudonym: "johoff3a2b"
```

### Story 2.4: Single Bot Instance Enforcement
**As a** Telegram group  
**I want** only one food-sharing bot instance per group  
**So that** there's consistent group management and no conflicts  

**Enforcement Logic:**
- Check existing bot instances before creation
- Redirect subsequent /start commands to existing instance
- Show existing admin and creation date
- Prevent bot fragmentation and confusion

### Story 2.5: Admin Dashboard & Controls
**As a** group admin  
**I want** comprehensive tools to manage my group  
**So that** I can maintain a healthy food sharing community  

**Admin Features:**
- Member status overview
- Pending disclaimer approvals
- Group activity statistics  
- Content moderation tools
- Member management (warnings, removal)

### Story 2.6: Member Lifecycle Management
**As a** group admin  
**I want to** manage member access and behavior  
**So that** I can maintain group quality and handle issues  

**Lifecycle Events:**
- Member joins → disclaimer required
- Member accepts → pseudonym generated, access enabled
- Member declines → access blocked, can't use features
- Member removed → cleanup all associated data

## 🎛️ Admin Interface Design

### Admin Dashboard Layout
```
👥 MEMBER MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━

📊 MEMBER OVERVIEW
┌─────────────────────────────┐
│ Total Members: 45           │
│ Active Members: 38          │
│ Pending Disclaimers: 3      │
│ Inactive (7d+): 4          │
└─────────────────────────────┘

⚠️  PENDING DISCLAIMERS
• alex_doe23 (joined 2 days ago)
• mary_smith11 (joined 1 day ago)
• john_wilson99 (joined 3 hours ago)

[Send Reminder] [Bulk Actions]

🚨 REPORTED MEMBERS
• bobfoo1a2b (spam reports: 2)
• carbar3c4d (safety concern: 1)

[Review Reports] [Member Actions]
```

### Admin Commands
```python
/admin_dashboard  # Main admin interface
/member_list      # View all members and status
/pending_users    # See users who haven't accepted disclaimer
/group_stats      # Group activity statistics
/member_action    # Warn, restrict, or remove members
/group_settings   # Modify group configuration
```

## 🧪 Testing Strategy

### Test Scenarios
1. **Bot Instance Control**
   - Verify single bot per group enforcement
   - Test admin assignment to first user
   - Confirm subsequent users can't create new instances

2. **Disclaimer Process**
   - Auto-detection of new group members
   - Proper disclaimer presentation
   - Accept/decline functionality
   - Access control based on disclaimer status

3. **Pseudonym System**
   - Unique pseudonyms per user-group combination
   - Consistency across sessions
   - Privacy protection (no reverse engineering)

4. **Admin Functions**
   - Admin dashboard accessibility
   - Member management capabilities
   - Permission enforcement

## 📈 Success Metrics

- **Disclaimer Acceptance Rate**: >85% of new members accept disclaimer
- **Admin Engagement**: >70% of group admins use dashboard monthly
- **Bot Instance Conflicts**: 0% groups with multiple bot instances
- **Privacy Protection**: 0% incidents of identity exposure
- **Member Satisfaction**: >4.5/5 rating for group management experience

## 🚧 Implementation Plan

### Phase 1: Core Infrastructure (Weeks 1-2)
- [ ] Group creation and bot instance control
- [ ] Admin assignment and basic dashboard
- [ ] Database schema implementation

### Phase 2: Member Management (Weeks 3-4)
- [ ] Disclaimer system implementation
- [ ] Pseudonym generation and storage
- [ ] Member status tracking

### Phase 3: Admin Tools (Weeks 5-6)
- [ ] Comprehensive admin dashboard
- [ ] Member management actions
- [ ] Group analytics and reporting

## 🔗 Dependencies

- **Epic 1**: Dual-mode platform foundation must be completed
- **Telegram Bot Framework**: Enhanced callback handling
- **Database Team**: Schema optimization for group queries
- **Security Team**: Pseudonym privacy validation

## ⚠️ Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|---------|------------|------------|
| Pseudonym collisions | Medium | Low | Robust hashing algorithm, collision detection |
| Disclaimer legal issues | High | Low | Legal team review, regular updates |
| Admin abuse of power | Medium | Medium | Audit logging, reporting mechanisms |
| Bot performance in large groups | High | Medium | Optimize database queries, implement caching |

## 🔒 Privacy & Security Considerations

- **Pseudonym Security**: No reverse engineering possible
- **Data Minimization**: Store only necessary member data
- **Admin Transparency**: Log all admin actions
- **Member Rights**: Clear disclaimer, easy opt-out

## 📚 Related Documents

- [Community Group Technical Specification](../technical/community-groups.md)
- [Pseudonym Privacy Analysis](../security/pseudonym-privacy.md)
- [Admin Dashboard UI/UX](../design/admin-dashboard.md)
- [Legal Disclaimer Requirements](../legal/disclaimer-requirements.md)

---

**Epic Owner:** Community Product Manager  
**Technical Lead:** Senior Full-Stack Developer  
**Created:** 2025-01-01  
**Last Updated:** 2025-01-01