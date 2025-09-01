# Epic 4: Global Reputation System

**Epic ID:** EPIC-004  
**Status:** Planned  
**Priority:** Critical  
**Estimated Duration:** 7 weeks  
**Team:** Trust & Safety Team  

## 🎯 Epic Goal

Implement a comprehensive global reputation system that follows users across all groups, creating accountability and trust while maintaining pseudonymity. Users become mindful of their platform-wide reputation, encouraging responsible behavior and enabling trust portability across communities.

## 📊 Business Value

- **Trust Building**: Global reputation creates accountability across all groups
- **User Retention**: Reputation investment keeps users engaged long-term
- **Quality Assurance**: Higher reputation members improve community quality
- **Network Effects**: Trusted users attract others and seed new communities
- **Scalability**: Self-regulating system reduces moderation overhead

## 🏗️ Technical Architecture

### Event-Driven Reputation Architecture
```python
# Valkey Streams for reputation event processing
REPUTATION_STREAMS = {
    'reputation.events': {
        'description': 'All reputation-affecting events across the platform',
        'consumers': ['reputation_calculator', 'trust_level_updater', 'analytics_service'],
        'partitions': 8,  # Distribute load across multiple streams
        'retention': '1y',  # Keep full reputation history
        'max_length': 1000000
    },
    'reputation.aggregates': {
        'description': 'Processed reputation scores and trust levels',
        'consumers': ['notification_service', 'privilege_manager', 'credit_service'],
        'retention': '90d',
        'max_length': 100000
    },
    'trust.violations': {
        'description': 'Trust violations requiring immediate attention',
        'consumers': ['admin_service', 'moderation_service', 'alert_service'],
        'retention': '2y',  # Legal/compliance retention
        'max_length': 50000
    }
}

class ReputationEventStreamer:
    """Manages reputation events through Valkey streams."""
    
    async def publish_reputation_event(self, event: ReputationEvent) -> str:
        """Publish reputation event to appropriate stream partition."""
        
        # Use user_id for partitioning to ensure ordered processing per user
        partition = hash(str(event.user_id)) % 8
        stream_name = f"reputation.events:{partition}"
        
        event_data = {
            'user_id': str(event.user_id),
            'event_type': event.event_type,
            'impact_score': float(event.impact_score),
            'group_id': str(event.group_id) if event.group_id else None,
            'exchange_id': str(event.exchange_id) if event.exchange_id else None,
            'metadata': json.dumps(event.metadata),
            'timestamp': int(time.time()),
            'processing_priority': event.get_priority()
        }
        
        stream_id = await self.valkey.xadd(
            stream_name,
            event_data,
            maxlen=125000,  # Per-partition limit
            approximate=True
        )
        
        # High-priority events get immediate processing trigger
        if event.get_priority() == 'high':
            await self.valkey.publish('reputation.priority.events', stream_name)
        
        return stream_id
```

### Reputation Components
```sql
-- Enhanced user reputation tracking
CREATE TABLE user_global_reputation (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    
    -- Core Reputation Metrics
    overall_score DECIMAL(4,2) DEFAULT 75.00, -- 0-100 scale
    trust_level VARCHAR(20) DEFAULT 'developing', -- new/developing/established/trusted/exemplary
    
    -- Activity Metrics (lifetime)
    total_food_shared INTEGER DEFAULT 0,
    total_food_claimed INTEGER DEFAULT 0,
    total_exchanges_completed INTEGER DEFAULT 0,
    total_groups_participated INTEGER DEFAULT 0,
    
    -- Quality Metrics
    avg_food_rating DECIMAL(3,2) DEFAULT 0.00, -- 1-5 stars
    avg_recipient_rating DECIMAL(3,2) DEFAULT 0.00, -- As food claimer
    reliability_score DECIMAL(4,2) DEFAULT 75.00, -- Pickup/delivery consistency
    
    -- Behavioral Metrics
    reported_incidents INTEGER DEFAULT 0,
    resolved_disputes INTEGER DEFAULT 0,
    community_contributions INTEGER DEFAULT 0, -- Helpful actions
    
    -- Time-based Factors
    account_age_days INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT NOW(),
    reputation_updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Reputation History
    peak_reputation DECIMAL(4,2) DEFAULT 75.00,
    reputation_trend VARCHAR(10) DEFAULT 'stable', -- rising/stable/declining
    
    -- Stream processing metadata
    last_stream_event_id VARCHAR(100),
    stream_lag_seconds INTEGER DEFAULT 0,
    reputation_sync_status VARCHAR(20) DEFAULT 'synced' -- synced/processing/error
);

-- Reputation history tracking with stream integration
CREATE TABLE reputation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    impact_score DECIMAL(5,2) NOT NULL, -- Can be positive or negative
    previous_score DECIMAL(4,2) NOT NULL,
    new_score DECIMAL(4,2) NOT NULL,
    group_id UUID REFERENCES community_groups(id) NULL,
    related_exchange_id UUID NULL,
    description TEXT,
    stream_id VARCHAR(100), -- Valkey stream message ID
    stream_partition INTEGER, -- Stream partition for load balancing
    processed_at TIMESTAMP, -- When stream event was processed
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stream processing checkpoints for reputation consumers
CREATE TABLE reputation_stream_checkpoints (
    consumer_group VARCHAR(100) NOT NULL,
    stream_partition INTEGER NOT NULL,
    last_processed_id VARCHAR(50) NOT NULL,
    events_processed INTEGER DEFAULT 0,
    last_checkpoint_at TIMESTAMP DEFAULT NOW(),
    lag_seconds INTEGER DEFAULT 0,
    PRIMARY KEY (consumer_group, stream_partition)
);

-- Group-specific reputation context
CREATE TABLE group_reputation_context (
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES community_groups(id),
    
    -- Group-specific metrics
    local_reputation DECIMAL(4,2) DEFAULT 75.00,
    food_shared_in_group INTEGER DEFAULT 0,
    successful_exchanges INTEGER DEFAULT 0,
    group_tenure_days INTEGER DEFAULT 0,
    
    -- Local behavioral indicators
    group_contributions INTEGER DEFAULT 0,
    local_reports INTEGER DEFAULT 0,
    peer_endorsements INTEGER DEFAULT 0,
    
    -- Visibility settings
    reputation_visible BOOLEAN DEFAULT true,
    detailed_stats_visible BOOLEAN DEFAULT false,
    
    PRIMARY KEY (user_id, group_id)
);
```

### Trust Level System
```python
# Real-time reputation processing with Valkey Streams
class ReputationStreamProcessor:
    """Processes reputation events from Valkey streams in real-time."""
    
    async def start_consumer_group(self, group_name: str, consumer_name: str):
        """Start processing reputation events for a consumer group."""
        
        # Create consumer group if not exists
        for partition in range(8):
            stream_name = f"reputation.events:{partition}"
            try:
                await self.valkey.xgroup_create(
                    stream_name, group_name, id='0', mkstream=True
                )
            except ResponseError:  # Group already exists
                pass
        
        # Start processing loop
        while True:
            try:
                # Read from all partitions with load balancing
                streams = {f"reputation.events:{i}": '>' for i in range(8)}
                
                messages = await self.valkey.xreadgroup(
                    group_name,
                    consumer_name,
                    streams,
                    count=10,
                    block=1000  # 1 second timeout
                )
                
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        await self.process_reputation_event(
                            stream_name, message_id, fields, group_name
                        )
                        
            except Exception as e:
                logger.error(f"Reputation stream processing error: {e}")
                await asyncio.sleep(5)  # Error recovery delay
    
    async def process_reputation_event(
        self, 
        stream_name: str, 
        message_id: str, 
        event_data: Dict,
        consumer_group: str
    ):
        """Process individual reputation event from stream."""
        
        try:
            user_id = UUID(event_data['user_id'])
            event_type = event_data['event_type']
            impact_score = Decimal(event_data['impact_score'])
            
            # Calculate new reputation score
            current_reputation = await self.get_user_reputation(user_id)
            new_score = await self.calculate_new_reputation(
                current_reputation, impact_score, event_type
            )
            
            # Update reputation in database
            await self.update_user_reputation(user_id, new_score, event_data)
            
            # Check for trust level changes
            old_trust_level = current_reputation.trust_level
            new_trust_level = self.calculate_trust_level(new_score)
            
            if old_trust_level != new_trust_level:
                # Publish trust level change event
                await self.publish_trust_level_change(
                    user_id, old_trust_level, new_trust_level
                )
            
            # Acknowledge message processing
            await self.valkey.xack(
                stream_name, consumer_group, message_id
            )
            
            # Update checkpoint
            partition = int(stream_name.split(':')[-1])
            await self.update_processing_checkpoint(
                consumer_group, partition, message_id
            )
            
        except Exception as e:
            logger.error(f"Failed to process reputation event {message_id}: {e}")
            # Dead letter queue for failed messages
            await self.send_to_dead_letter_queue(stream_name, message_id, event_data)

TRUST_LEVELS = {
    'exemplary': {
        'min_score': 90, 
        'color': '🟢', 
        'badge': '🏆 Exemplary',
        'privileges': ['premium_features', 'moderation', 'credit_gifting']
    },
    'trusted': {
        'min_score': 80, 
        'color': '🔵', 
        'badge': '🔵 Trusted',
        'privileges': ['premium_features', 'priority_claims']
    },
    'established': {
        'min_score': 70, 
        'color': '🟡', 
        'badge': '🟡 Established',
        'privileges': ['standard_features']
    },
    'developing': {
        'min_score': 50, 
        'color': '🟠', 
        'badge': '🟠 Developing',
        'privileges': ['basic_features']
    },
    'concerning': {
        'min_score': 0, 
        'color': '🔴', 
        'badge': '🔴 Needs Improvement',
        'privileges': ['restricted_features']
    }
}
```

## 📋 User Stories

### Story 4.1: Cross-Group Reputation Display
**As a** group member  
**I want to** see the global reputation of other members when they post or claim food  
**So that** I can make informed decisions about food sharing interactions  

**Display Format:**
```
🍕 **Homemade Lasagna**
Shared by: johncook1a2b

📊 **Member Reputation**
🔵 Trusted Member (87/100)
🏠 152 successful exchanges across 3 groups  
⭐ 4.8/5.0 average rating
🎯 98% pickup reliability

📅 Available: Today 6-8 PM
📍 Pickup: Building lobby
💰 Cost: 1 credit
```

### Story 4.2: Reputation Transfer to New Groups
**As a** user with established reputation  
**I want** my reputation to be visible when I join new groups  
**So that** I can build trust quickly with new community members  

**New Member Introduction:**
```
👤 **New Member Joined: alicefood2b3c**

📊 **Reputation Overview**
🔵 Trusted Member (82/100)
🏆 Platform experience: 8 months
🤝 Successfully completed 47 exchanges
⭐ Consistently rated 4.7+ stars

🏠 **Previous Communities**
Participated in 2 other groups with excellent standing

Welcome to our community! 🎉
```

### Story 4.3: Reputation-Based Privileges
**As a** high-reputation user  
**I want** access to premium features and privileges  
**So that** my good behavior is rewarded with enhanced experiences  

**Privilege Matrix:**
| Trust Level | Claim Priority | Credit Discount | Premium Features | Moderation |
|-------------|---------------|-----------------|-----------------|------------|
| Exemplary   | ✅ First      | 25% discount    | ✅ All          | ✅ Yes     |
| Trusted     | ✅ Second     | 15% discount    | ✅ Most         | ❌ No      |
| Established | ❌ Standard   | 5% discount     | ❌ None         | ❌ No      |
| Developing  | ❌ Standard   | No discount     | ❌ None         | ❌ No      |
| Concerning  | 🔴 Delayed    | 25% surcharge   | ❌ Restricted   | ❌ No      |

### Story 4.4: Reputation Impact Events
**As a** platform user  
**I want** my actions to appropriately affect my reputation  
**So that** good behavior is rewarded and poor behavior has consequences  

**Reputation Events:**
```python
REPUTATION_EVENTS = {
    # Positive Actions
    'food_shared': {'base_impact': +2.0, 'max_per_day': 10.0},
    'exchange_completed': {'base_impact': +1.5, 'max_per_day': 15.0},
    'highly_rated_food': {'base_impact': +3.0, 'max_per_day': 15.0},
    'reliable_pickup': {'base_impact': +1.0, 'max_per_day': 10.0},
    'community_help': {'base_impact': +2.5, 'max_per_week': 10.0},
    
    # Negative Actions
    'exchange_cancelled': {'base_impact': -1.0, 'max_per_day': -10.0},
    'no_show_pickup': {'base_impact': -3.0, 'max_per_week': -15.0},
    'poor_food_rating': {'base_impact': -2.5, 'max_per_day': -10.0},
    'spam_report': {'base_impact': -5.0, 'max_per_month': -25.0},
    'safety_violation': {'base_impact': -10.0, 'max_per_month': -30.0}
}
```

### Story 4.5: Reputation Rehabilitation
**As a** user with declining reputation  
**I want** clear paths to improve my reputation  
**So that** I can rebuild trust and regain platform privileges  

**Rehabilitation Programs:**
```
💡 **REPUTATION IMPROVEMENT OPPORTUNITIES**

Your current score: 58/100 (Developing)

🎯 **Quick Wins** (1-2 weeks)
• Share 3 food items → Potential +6 points
• Complete 5 reliable pickups → Potential +5 points
• Help moderate group discussions → Potential +4 points

📈 **Long-term Building** (1-2 months)
• Maintain 4.5⭐+ rating for 20 exchanges → Potential +15 points
• Become active contributor in community → Potential +10 points
• Complete dispute resolution training → Potential +5 points

🎓 **Skill Building**
• Food safety guidelines course → +3 points
• Community leadership training → +5 points

[Start Improvement Plan] [View Progress Tracking]
```

### Story 4.6: Reputation Privacy Controls
**As a** user concerned about privacy  
**I want** control over what reputation information is visible  
**So that** I can balance transparency with personal privacy  

**Privacy Settings:**
```
🔒 **REPUTATION PRIVACY SETTINGS**

📊 **Visibility Controls**
☑️ Show overall reputation score
☑️ Show trust level badge
☐ Show detailed exchange statistics
☐ Show group participation history
☐ Show improvement trends
☐ Show rehabilitation status

🎯 **Audience Controls**
☑️ Visible to group members
☑️ Visible to potential food claimers
☐ Visible to group admins only
☐ Visible to platform moderators only

💡 **Note:** Higher visibility generally leads to more trust
and better experiences on the platform.

[Save Settings] [Privacy Help]
```

## 🔄 Reputation Calculation Engine

### Multi-Factor Scoring Algorithm
```python
def calculate_reputation_score(user_id: UUID) -> float:
    """Calculate comprehensive reputation score."""
    
    base_factors = {
        'exchange_success_rate': 0.30,    # 30% weight
        'food_quality_rating': 0.25,     # 25% weight  
        'reliability_score': 0.20,       # 20% weight
        'community_contributions': 0.15,  # 15% weight
        'behavioral_incidents': 0.10      # 10% weight (negative)
    }
    
    # Time decay for older events
    recent_weight = 0.7  # Recent events count more
    historical_weight = 0.3  # Older events count less
    
    # Account age bonus (up to +5 points)
    account_age_bonus = min(5, account_age_months * 0.5)
    
    # Group diversity bonus (up to +3 points)  
    diversity_bonus = min(3, groups_participated * 0.5)
    
    final_score = (
        weighted_factor_score * 0.8 +    # Core factors
        account_age_bonus +              # Maturity bonus
        diversity_bonus -                # Community diversity
        penalty_deductions               # Violations
    )
    
    return max(0, min(100, final_score))
```

### Reputation Decay System
```python
async def apply_reputation_decay():
    """Apply time-based reputation decay to encourage ongoing participation."""
    
    DECAY_RULES = {
        'inactive_30_days': -0.5,    # Small decay for month of inactivity
        'inactive_60_days': -1.0,    # Larger decay for 2 months
        'inactive_90_days': -2.0,    # Significant decay for 3 months
        'inactive_180_days': -5.0,   # Major decay for 6 months
    }
    
    # Apply decay with minimum score protection
    for user in inactive_users:
        min_score = 60 if user.trust_level in ['trusted', 'exemplary'] else 40
        if user.overall_score > min_score:
            await apply_decay(user, appropriate_decay_amount)
```

## 🧪 Testing Strategy

### Test Scenarios
1. **Reputation Calculation**
   - Verify multi-factor scoring accuracy
   - Test edge cases (new users, very active users)
   - Confirm reputation transfer to new groups

2. **Cross-Group Visibility**
   - Test reputation display across different groups
   - Verify privacy controls work correctly
   - Confirm pseudonym protection maintained

3. **Privilege System**
   - Validate privilege assignment by trust level
   - Test privilege enforcement in features
   - Confirm privilege updates with reputation changes

4. **Rehabilitation System**
   - Test improvement opportunity calculations
   - Verify rehabilitation program effectiveness
   - Confirm progress tracking accuracy

## 📈 Success Metrics

- **User Engagement**: 85% of users check their reputation monthly
- **Behavioral Improvement**: 70% reduction in reported incidents
- **Cross-Group Trust**: 60% of users maintain >75 reputation in new groups
- **Privilege Adoption**: 45% of eligible users use premium features
- **Rehabilitation Success**: 40% of users improve from "concerning" to "developing"

## 🚧 Implementation Plan

### Phase 1: Core Reputation Engine (Weeks 1-3)
- [ ] Database schema and reputation calculation engine
- [ ] Basic reputation display and tracking
- [ ] Reputation event system implementation

### Phase 2: Cross-Group Integration (Weeks 4-5)
- [ ] Cross-group reputation visibility
- [ ] Reputation transfer to new groups
- [ ] Privacy controls and settings

### Phase 3: Privilege System (Weeks 6-7)
- [ ] Trust level privileges implementation
- [ ] Rehabilitation programs
- [ ] Admin tools and analytics

## 🔗 Dependencies

- **User Management System**: Core user data and authentication
- **Group Management**: Cross-group reputation display
- **Credit System**: Reputation-credit integration
- **Analytics Platform**: Reputation metrics and reporting

## ⚠️ Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|---------|------------|------------|
| Reputation gaming/manipulation | High | Medium | Multiple validation layers, anomaly detection |
| Privacy concerns with cross-group visibility | Medium | Medium | Granular privacy controls, pseudonym protection |
| Reputation inflation over time | Medium | High | Decay system, recalibration processes |
| User anxiety about reputation scores | Medium | Medium | Educational content, rehabilitation paths |

## 🔒 Privacy & Security Considerations

- **Pseudonym Protection**: Real identities never exposed across groups
- **Data Minimization**: Store only necessary reputation data
- **User Control**: Privacy settings for reputation visibility
- **Audit Trail**: Complete history of reputation changes
- **Anti-Gaming**: Multiple validation layers prevent manipulation

## 📚 Related Documents

- [Reputation Algorithm Specification](../technical/reputation-algorithm.md)
- [Cross-Group Privacy Analysis](../security/cross-group-reputation-privacy.md)
- [Trust Level Privileges Matrix](../product/trust-level-privileges.md)
- [Reputation UI/UX Guidelines](../design/reputation-interface.md)

---

**Epic Owner:** Trust & Safety Product Manager  
**Technical Lead:** Senior Data Engineer  
**Created:** 2025-01-01  
**Last Updated:** 2025-01-01