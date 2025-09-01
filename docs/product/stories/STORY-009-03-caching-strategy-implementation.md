# Story 009.03: Valkey Streams Infrastructure Implementation (ENHANCED FOR AI)

**Epic:** EPIC-009 - Platform Scalability & Performance  
**Priority:** 🔴 CRITICAL - COMPLETE AFTER DATABASE (Story 009-02)  
**Story Points:** 7  
**Sprint:** 1  
**AI Developer Complexity:** HIGH - Event-driven architecture foundation  

---

## 🤖 AI DEVELOPER: READ THIS FIRST

**This story implements the Valkey streams event-driven architecture that ALL reputation, analytics, and admin features depend on.**

**CRITICAL FILES TO READ:**
- `/docs/product/epics/EPIC-009-Platform-Scalability-Performance.md` (Valkey architecture)
- `/docs/product/epics/EPIC-004-Global-Reputation-System.md` (reputation events)  
- `/docs/product/epics/EPIC-001-Dual-Mode-Platform-Foundation.md` (mode transition events)
- `/valkey.conf` (exact configuration file)

---

## User Story
**As a** platform user  
**I want** real-time system responses and instant updates across all features  
**So that** reputation changes, notifications, and analytics happen immediately  

---

## 🎯 EXACT IMPLEMENTATION REQUIREMENTS

### **STEP 1: Valkey Streams Configuration**

**File to create:** `src/core/streams.py`

```python
# EXACT STREAM CONFIGURATION - DO NOT MODIFY NAMES
VALKEY_STREAMS = {
    # Reputation events (8 partitions for load distribution)
    'reputation.events': {
        'partitions': 8,
        'retention': '365d',  # 1 year retention
        'max_length': 1000000,  # Per partition limit: 125,000
        'consumers': ['reputation_calculator', 'trust_level_updater', 'analytics_service'],
        'priority': 'high'
    },
    
    # User mode transitions  
    'user.mode.transitions': {
        'partitions': 1,
        'retention': '30d',
        'max_length': 100000,
        'consumers': ['reputation_service', 'notification_service', 'analytics_service'],
        'priority': 'high'
    },
    
    # Group mode activities
    'group.mode.activities': {
        'partitions': 4,
        'retention': '7d', 
        'max_length': 50000,
        'consumers': ['food_discovery_service', 'partnership_service'],
        'priority': 'medium'
    },
    
    # Verification completion events
    'verification.events': {
        'partitions': 2,
        'retention': '90d',
        'max_length': 200000,
        'consumers': ['user_service', 'trust_service', 'admin_service'],
        'priority': 'high'
    },
    
    # Analytics events (privacy-compliant)
    'analytics.user.behavior': {
        'partitions': 4,
        'retention': '30d',
        'max_length': 500000,
        'consumers': ['behavior_analyzer', 'recommendation_engine', 'retention_calculator'],
        'priority': 'low'
    },
    
    # Business events for revenue tracking
    'analytics.business.events': {
        'partitions': 8,
        'retention': '365d',
        'max_length': 1000000,
        'consumers': ['revenue_tracker', 'growth_analyzer', 'forecast_engine'],
        'priority': 'medium'
    },
    
    # Platform performance metrics
    'analytics.platform.metrics': {
        'partitions': 2,
        'retention': '7d',
        'max_length': 100000,
        'consumers': ['performance_monitor', 'capacity_planner', 'alert_manager'],
        'priority': 'high'
    }
}

class ValkeyStreamManager:
    """Manages all Valkey streams for the platform."""
    
    def __init__(self, valkey_client):
        self.valkey = valkey_client
        self.initialized = False
    
    async def initialize_streams(self):
        """Create all streams and consumer groups."""
        for stream_base_name, config in VALKEY_STREAMS.items():
            partitions = config['partitions']
            
            for partition in range(partitions):
                if partitions > 1:
                    stream_name = f"{stream_base_name}:{partition}"
                else:
                    stream_name = stream_base_name
                
                # Create stream if doesn't exist
                try:
                    await self.valkey.xadd(
                        stream_name, 
                        {'_init': 'stream_created'}, 
                        maxlen=1
                    )
                    # Remove init message
                    await self.valkey.xtrim(stream_name, maxlen=0)
                except Exception as e:
                    print(f"Stream {stream_name} creation failed: {e}")
                
                # Create consumer groups
                for consumer in config['consumers']:
                    try:
                        await self.valkey.xgroup_create(
                            stream_name, 
                            consumer, 
                            id='0', 
                            mkstream=True
                        )
                    except ResponseError:
                        # Group already exists
                        pass
        
        self.initialized = True
    
    async def publish_event(self, stream_name: str, event_data: dict, partition_key: str = None):
        """Publish event to appropriate stream partition."""
        if not self.initialized:
            await self.initialize_streams()
        
        config = VALKEY_STREAMS.get(stream_name)
        if not config:
            raise ValueError(f"Unknown stream: {stream_name}")
        
        # Determine partition
        if config['partitions'] > 1:
            if partition_key:
                partition = hash(partition_key) % config['partitions']
            else:
                partition = 0  # Default partition
            full_stream_name = f"{stream_name}:{partition}"
        else:
            full_stream_name = stream_name
        
        # Add timestamp and metadata
        enriched_data = {
            **event_data,
            'timestamp': int(time.time()),
            'stream_name': stream_name,
            'partition': partition if config['partitions'] > 1 else 0,
            'priority': config['priority']
        }
        
        # Publish to stream
        stream_id = await self.valkey.xadd(
            full_stream_name,
            enriched_data,
            maxlen=config['max_length'] // config['partitions'],
            approximate=True
        )
        
        # High-priority events get immediate processing trigger
        if config['priority'] == 'high':
            await self.valkey.publish(
                'priority.events',
                json.dumps({
                    'stream': full_stream_name,
                    'id': stream_id,
                    'priority': 'high'
                })
            )
        
        return stream_id
```

### **STEP 2: Event Publishers for Each Domain**

**File to create:** `src/services/event_publishers.py`

```python
class ReputationEventPublisher:
    """Publishes reputation events to streams."""
    
    def __init__(self, stream_manager: ValkeyStreamManager):
        self.streams = stream_manager
    
    async def publish_reputation_change(
        self, 
        user_id: UUID, 
        event_type: str, 
        impact_score: float,
        group_id: UUID = None,
        exchange_id: UUID = None,
        description: str = None
    ):
        """Publish reputation change event."""
        event_data = {
            'user_id': str(user_id),
            'event_type': event_type,
            'impact_score': float(impact_score),
            'group_id': str(group_id) if group_id else None,
            'exchange_id': str(exchange_id) if exchange_id else None,
            'description': description,
            'processing_priority': 'high' if abs(impact_score) > 5.0 else 'normal'
        }
        
        return await self.streams.publish_event(
            'reputation.events',
            event_data,
            partition_key=str(user_id)  # Ensure ordered processing per user
        )

class ModeTransitionPublisher:
    """Publishes mode transition events."""
    
    def __init__(self, stream_manager: ValkeyStreamManager):
        self.streams = stream_manager
    
    async def publish_mode_transition(
        self, 
        user_id: UUID, 
        from_mode: str, 
        to_mode: str,
        reason: str = None
    ):
        """Publish user mode transition event."""
        event_data = {
            'user_id': str(user_id),
            'from_mode': from_mode,
            'to_mode': to_mode,
            'reason': reason,
            'requires_reverification': to_mode == 'neighborhood'
        }
        
        return await self.streams.publish_event(
            'user.mode.transitions',
            event_data,
            partition_key=str(user_id)
        )

class AnalyticsEventPublisher:
    """Publishes analytics events (privacy-compliant)."""
    
    def __init__(self, stream_manager: ValkeyStreamManager):
        self.streams = stream_manager
    
    async def publish_user_behavior(
        self,
        user_hash: str,  # Hashed user ID for privacy
        event_type: str,
        event_category: str,
        properties: dict,
        session_hash: str = None
    ):
        """Publish user behavior event."""
        event_data = {
            'user_hash': user_hash,
            'event_type': event_type,
            'event_category': event_category,
            'properties': json.dumps(properties),
            'session_hash': session_hash,
            'platform': 'telegram'  # Default platform
        }
        
        return await self.streams.publish_event(
            'analytics.user.behavior',
            event_data,
            partition_key=user_hash
        )
```

### **STEP 3: Stream Consumers Framework**

**File to create:** `src/services/stream_consumers.py`

```python
import asyncio
from typing import Dict, Callable, List
import logging

class StreamConsumer:
    """Base class for stream consumers."""
    
    def __init__(
        self, 
        valkey_client,
        consumer_group: str,
        consumer_name: str,
        stream_names: List[str],
        batch_size: int = 10
    ):
        self.valkey = valkey_client
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.stream_names = stream_names
        self.batch_size = batch_size
        self.running = False
        self.handlers = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for specific event type."""
        self.handlers[event_type] = handler
    
    async def start_consuming(self):
        """Start consuming messages from streams."""
        # Create consumer groups if don't exist
        for stream_name in self.stream_names:
            try:
                await self.valkey.xgroup_create(
                    stream_name,
                    self.consumer_group,
                    id='0',
                    mkstream=True
                )
            except:
                pass  # Group already exists
        
        self.running = True
        
        while self.running:
            try:
                # Build stream dict for xreadgroup
                streams = {name: '>' for name in self.stream_names}
                
                messages = await self.valkey.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    streams,
                    count=self.batch_size,
                    block=1000  # 1 second timeout
                )
                
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        await self.process_message(
                            stream_name, message_id, fields
                        )
                        
            except Exception as e:
                logging.error(f"Stream consumer error: {e}")
                await asyncio.sleep(5)  # Error recovery delay
    
    async def process_message(self, stream_name: str, message_id: str, fields: dict):
        """Process individual message from stream."""
        try:
            event_type = fields.get('event_type', 'unknown')
            
            if event_type in self.handlers:
                await self.handlers[event_type](fields)
            else:
                logging.warning(f"No handler for event_type: {event_type}")
            
            # Acknowledge message
            await self.valkey.xack(
                stream_name, self.consumer_group, message_id
            )
            
        except Exception as e:
            logging.error(f"Failed to process message {message_id}: {e}")
            # Message will remain in pending list for retry
    
    def stop(self):
        """Stop consuming messages."""
        self.running = False
```

### **STEP 4: Caching Layer Integration**

**File to create:** `src/services/cache_manager.py`

```python
class CacheManager:
    """Multi-level cache manager with event-driven invalidation."""
    
    def __init__(self, valkey_client):
        self.valkey = valkey_client
        self.cache_configs = {
            'user_profiles': {'ttl': 3600, 'prefix': 'user:'},
            'reputation_scores': {'ttl': 300, 'prefix': 'rep:'},
            'group_activity': {'ttl': 900, 'prefix': 'group:'},
            'food_discovery': {'ttl': 60, 'prefix': 'food:'}
        }
    
    async def get(self, cache_type: str, key: str):
        """Get cached value."""
        config = self.cache_configs[cache_type]
        full_key = f"{config['prefix']}{key}"
        
        value = await self.valkey.get(full_key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, cache_type: str, key: str, value: any, ttl: int = None):
        """Set cached value."""
        config = self.cache_configs[cache_type]
        full_key = f"{config['prefix']}{key}"
        ttl = ttl or config['ttl']
        
        await self.valkey.setex(
            full_key, 
            ttl, 
            json.dumps(value, default=str)
        )
    
    async def invalidate(self, cache_type: str, key: str):
        """Invalidate specific cache key."""
        config = self.cache_configs[cache_type]
        full_key = f"{config['prefix']}{key}"
        await self.valkey.delete(full_key)
```

---

## ✅ ACCEPTANCE CRITERIA (ALL MUST BE MET)

### **Stream Infrastructure:**
- [ ] All 7 stream types configured with exact names and partitions
- [ ] Consumer groups created for all streams
- [ ] Stream partitioning working correctly (load distributed)
- [ ] Event publishing working for all event types

### **Event Processing:**
- [ ] Reputation events processed in real-time (<1 second latency)
- [ ] Mode transition events trigger appropriate service updates
- [ ] Analytics events collected without blocking user operations
- [ ] Stream consumers handle errors gracefully with retry logic

### **Performance Requirements:**
- [ ] Stream publishing <10ms average latency
- [ ] Consumer processing <100ms per message average
- [ ] Stream lag monitoring showing <30 second delays
- [ ] Cache hit rates >85% for hot data

### **Reliability:**
- [ ] Consumer groups maintain processing state correctly  
- [ ] Failed messages get retried appropriately
- [ ] Stream checkpoints track processing progress
- [ ] System recovers automatically from stream consumer failures

---

## 🧪 TESTING REQUIREMENTS

### **Stream Testing:**
```bash
# EXACT TEST COMMANDS
python -m pytest tests/test_valkey_streams.py
python -m src.scripts.test_stream_performance.py --events 1000 --max-latency 10ms
```

### **Integration Testing:**
```bash
# Test with real event publishing
python -m src.scripts.integration_test_streams.py --reputation-events 100 --mode-transitions 10
```

### **Load Testing:**
```python
# Test consumer processing under load
async def test_consumer_load():
    # Should process 1000 events in <30 seconds
    await publish_test_events(1000)
    assert await verify_processing_complete() < 30
```

---

## 🚨 CRITICAL WARNINGS FOR AI DEVELOPERS

❌ **ABSOLUTELY DO NOT:**
- Change any stream names from the specification
- Modify partition counts without understanding the implications
- Skip creating any consumer groups
- Use different retention periods than specified

✅ **MUST DO:**
- Follow exact stream naming conventions
- Implement all event publishers as specified
- Test stream processing performance thoroughly
- Verify consumer group recovery after failures

⚠️ **CRITICAL DEPENDENCY:**
This story MUST be completed before any reputation, analytics, or admin features can be implemented.

---

## 📋 COMPLETION CHECKLIST

**Before marking story complete:**
- [ ] All 7 stream types created with correct configurations
- [ ] Event publishers working for reputation, mode transitions, analytics
- [ ] Stream consumers processing messages successfully
- [ ] Performance benchmarks met (<10ms publish, <100ms process)
- [ ] Error handling and recovery mechanisms tested
- [ ] Integration with existing codebase verified
- [ ] All unit and integration tests passing

**Story is complete when:** All stream infrastructure is operational and processing events in real-time with the specified performance requirements.