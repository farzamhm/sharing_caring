# Epic 4 Stories: Exchange Coordination & Credit System

## Story 4.1: Exchange Request & Confirmation

### User Story
As a **food sharer**,  
I want **to confirm food requests and coordinate pickup details**,  
So that **I can ensure successful food transfers to neighbors**.

### Acceptance Criteria

**Functional Requirements:**
1. Food poster receives request notifications with requester details
2. Poster can confirm or decline requests through bot interface
3. Confirmed exchanges automatically update both parties
4. Pickup time and location details are shared with both parties
5. Exchange status is tracked throughout lifecycle
6. Declined requests notify requester and restore food availability

**Integration Requirements:**
7. Request handling integrates with existing notification system
8. Confirmation process follows established bot conversation patterns
9. Status updates propagate to all relevant systems (food posts, user notifications)

**Business Rules:**
10. Only food poster can confirm/decline requests
11. First confirmed request wins (others auto-declined)
12. Credits are charged to requester upon confirmation
13. Confirmation must happen within 30 minutes of request

### Technical Implementation
- **State Management:** Exchange state transitions (requested → confirmed/declined)
- **Notification System:** Real-time updates via Telegram to both parties
- **Credit Operations:** Atomic credit deduction on confirmation
- **Database Updates:** Coordinated updates to food_posts and exchange_requests tables

### Definition of Done
- [ ] Request notifications with full context
- [ ] Confirm/decline interface through bot
- [ ] Automatic status updates for both parties
- [ ] Pickup coordination information sharing
- [ ] Exchange lifecycle tracking
- [ ] Proper handling of declined requests

---

## Story 4.2: Pickup Coordination

### User Story
As **participants in a confirmed food exchange**,  
I want **to coordinate specific pickup details**,  
So that **we can successfully complete the food transfer**.

### Acceptance Criteria

**Functional Requirements:**
1. Both parties receive pickup coordination message with contact info
2. Pickup reminders are sent 30 minutes before scheduled time
3. Exchange status updates when pickup window begins
4. Participants can send messages through bot for coordination
5. Late pickup notifications are sent if pickup window is missed
6. Exchange can be cancelled by either party with notification

**Integration Requirements:**
7. Pickup coordination uses existing scheduled notification system
8. Message relay integrates with Telegram's messaging capabilities
9. Time-based triggers coordinate with system scheduler

**User Experience Requirements:**
10. Pickup instructions are clear and actionable
11. Contact information sharing respects privacy preferences
12. Reminder timing is configurable per user preferences

### Technical Implementation
- **Scheduling System:** Redis-based job scheduling for pickup reminders
- **Message Relay:** Bot-mediated messaging between participants
- **Status Tracking:** Time-based status updates (in_progress, overdue)
- **Contact Sharing:** Controlled sharing of apartment numbers/preferred contact methods

### Definition of Done
- [ ] Pickup coordination messages with all necessary details
- [ ] Automated reminders before pickup window
- [ ] Exchange status tracking during pickup window
- [ ] Message relay system between participants
- [ ] Late pickup handling and notifications
- [ ] Cancellation option with appropriate notifications

---

## Story 4.3: Exchange Completion & Rating

### User Story
As **exchange participants**,  
I want **to confirm completion and rate the experience**,  
So that **credits are awarded and community trust is maintained**.

### Acceptance Criteria

**Functional Requirements:**
1. Either party can confirm exchange completion through bot
2. Both parties are prompted to rate the exchange (1-5 stars)
3. Optional comment can be provided with rating
4. Completed exchanges trigger credit transactions
5. Ratings contribute to user reputation scores
6. Exchange history is maintained for both parties

**Integration Requirements:**
7. Completion confirmation integrates with credit system
8. Rating system feeds into user reputation calculations
9. Exchange history integrates with user profile systems

**Quality Requirements:**
10. Rating prompts are sent within 1 hour of completion
11. Credit awards are processed immediately upon completion
12. Exchange history is permanently maintained for trust building

### Technical Implementation
- **Completion Verification:** Either party can mark complete, both parties notified
- **Rating System:** 5-star rating with optional text comments
- **Credit Processing:** Automatic credit award to food sharer upon completion
- **Reputation System:** Aggregate ratings for user trust scores

### Definition of Done
- [ ] Exchange completion confirmation from either party
- [ ] 5-star rating system with optional comments
- [ ] Credit award processing on completion
- [ ] User reputation score updates
- [ ] Permanent exchange history maintenance
- [ ] Rating prompts within 1 hour of completion

---

## Story 4.4: Credit System Implementation

### User Story
As a **platform participant**,  
I want **to earn credits for sharing food and spend credits for receiving food**,  
So that **there's a fair incentive system encouraging community participation**.

### Acceptance Criteria

**Functional Requirements:**
1. Users earn 1 credit for each completed food share
2. Users spend 1 credit for each food request (charged on confirmation)
3. New users receive 3 welcome credits to bootstrap participation
4. Credit balance is visible through /credits command
5. Insufficient credits prevent food requests with helpful message
6. Credit transaction history is maintained and viewable

**Integration Requirements:**
7. Credit operations are atomic and transaction-safe
8. Credit checks integrate with food request system
9. Credit history integrates with user profile systems

**Business Rules:**
10. Credits cannot go negative (hard limit at 0)
11. Maximum credit balance of 50 to encourage circulation
12. Welcome credits are awarded only once per user
13. Credit transactions are immutable once created

### Technical Implementation
- **Transaction Safety:** Database transactions ensure atomicity of credit operations
- **Balance Checking:** Real-time balance verification before operations
- **Audit Trail:** Complete transaction log with timestamps and reasons
- **Welcome Credits:** Automatic assignment on profile completion

### Definition of Done
- [ ] Credit earning system (+1 per completed share)
- [ ] Credit spending system (-1 per confirmed request)
- [ ] Welcome credit allocation for new users
- [ ] /credits command showing balance and history
- [ ] Credit requirement enforcement for requests
- [ ] Complete transaction history with audit trail