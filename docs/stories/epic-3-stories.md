# Epic 3 Stories: Food Posting & Discovery

## Story 3.1: Food Posting Workflow

### User Story
As a **verified user**,  
I want **to post food I want to share through simple bot commands**,  
So that **neighbors can discover and request my excess food**.

### Acceptance Criteria

**Functional Requirements:**
1. User can initiate food posting with /share command
2. Bot guides through multi-step conversation: food name → portions → photo → pickup time → allergens
3. Photo upload is processed and stored in S3 with compression
4. Food post is created with automatic expiration time (4 hours default)
5. Post is immediately visible to nearby users
6. User receives confirmation with post details and management options

**Integration Requirements:**
7. Photo upload integrates with existing S3 configuration
8. Food post data follows established database schema
9. Post visibility respects user location and verification status

**Quality Requirements:**
10. Photo compression reduces file size while maintaining quality
11. Conversation flow is intuitive with clear prompts
12. Error handling covers upload failures and invalid inputs
13. Post creation is atomic (all-or-nothing operation)

### Technical Implementation
- **Conversation Flow:** ConversationHandler with 5 states (name, portions, photo, time, allergens)
- **Photo Processing:** Automatic compression to <1MB, thumbnail generation
- **Storage:** S3 upload with unique filename and proper MIME type handling
- **Database:** Insert into food_posts table with proper foreign keys

### Definition of Done
- [ ] /share command initiates guided posting workflow
- [ ] Multi-step conversation with validation at each step
- [ ] Photo upload with compression and S3 storage
- [ ] Food post creation with proper expiration time
- [ ] Immediate visibility to nearby users
- [ ] Confirmation message with post management options

---

## Story 3.2: Food Discovery & Browsing

### User Story
As a **hungry community member**,  
I want **to browse available food in my neighborhood**,  
So that **I can find meals that match my preferences**.

### Acceptance Criteria

**Functional Requirements:**
1. User can browse food with /browse command
2. Bot displays available food filtered by location and dietary restrictions
3. Food items show: name, portions, photo, distance, pickup time, allergens
4. Users can filter by food type, dietary restrictions, or time availability
5. Browse results are paginated for easy navigation
6. Real-time availability updates reflect current status

**Integration Requirements:**
7. Location filtering uses existing neighborhood assignment logic
8. Dietary filtering respects user profile preferences
9. Photo display integrates with S3 thumbnail URLs

**Performance Requirements:**
10. Browse results load within 2 seconds
11. Pagination handles large result sets efficiently
12. Real-time updates don't impact bot responsiveness

### Technical Implementation
- **Query Optimization:** Database indexes on location, expiration, and dietary fields
- **Pagination:** Limit 5 items per page with next/previous navigation
- **Real-time Updates:** Cache invalidation when posts are claimed/expired
- **Distance Calculation:** Simple neighborhood-based proximity (same building first)

### Definition of Done
- [ ] /browse command shows available food with full details
- [ ] Location-based filtering shows only nearby food
- [ ] Dietary restriction filtering works correctly
- [ ] Paginated results with smooth navigation
- [ ] Real-time availability updates
- [ ] Performance meets <2 second response time target

---

## Story 3.3: Food Request System

### User Story
As a **food browser**,  
I want **to request specific food items I'm interested in**,  
So that **I can coordinate pickup with the food sharer**.

### Acceptance Criteria

**Functional Requirements:**
1. User can request food directly from browse results
2. Request notifications are sent to food poster via Telegram
3. Food status updates to "pending" when requested
4. Requester receives confirmation with next steps
5. Request includes automatic expiration if not confirmed
6. Multiple requests are handled with first-come-first-served logic

**Integration Requirements:**
7. Request system integrates with credit checking (user must have credits)
8. Notifications use existing Telegram messaging infrastructure
9. Status updates reflect in real-time across all users

**Business Rules:**
10. Users cannot request their own food posts
11. Only verified users can make requests
12. Requests expire after 30 minutes if not confirmed
13. Credit is reserved but not charged until confirmation

### Technical Implementation
- **Request Creation:** Insert into exchange_requests table with pending status
- **Notification System:** Telegram message to food poster with request details
- **Status Management:** Update food_posts status to track request state
- **Credit Reservation:** Temporary hold on requester's credit (released if expired)

### Definition of Done
- [ ] Request functionality accessible from browse results
- [ ] Immediate notification to food poster
- [ ] Food status updates to pending state
- [ ] Requester confirmation with clear next steps
- [ ] Automatic request expiration after 30 minutes
- [ ] First-come-first-served request handling

---

## Story 3.4: Food Post Management

### User Story
As a **food poster**,  
I want **to manage my active food posts (edit, expire, cancel)**,  
So that **I can keep my listings accurate and respond to changing circumstances**.

### Acceptance Criteria

**Functional Requirements:**
1. User can view their active food posts with /myposts command
2. User can edit post details (pickup time, portions, allergens)
3. User can manually expire posts that are no longer available
4. User can cancel posts that have pending requests
5. Posts automatically expire after 4 hours
6. Post status changes are communicated to interested users

**Integration Requirements:**
7. Post management respects existing request status
8. Status changes trigger appropriate notifications
9. Edit operations maintain data integrity

**Business Rules:**
10. Posts with confirmed exchanges cannot be cancelled
11. Expired posts are hidden from browse results immediately
12. Cancelled posts refund any reserved credits
13. Only post owner can manage their posts

### Technical Implementation
- **Post Retrieval:** Query food_posts by user_id with status filtering
- **Edit Operations:** Update operations with optimistic locking
- **Status Management:** State transitions with proper validation
- **Notification System:** Automatic messages when posts are cancelled/expired

### Definition of Done
- [ ] /myposts command shows user's active posts
- [ ] Edit functionality for post details
- [ ] Manual expiration option
- [ ] Cancellation with proper request handling
- [ ] Automatic expiration after 4 hours
- [ ] Notifications for all status changes