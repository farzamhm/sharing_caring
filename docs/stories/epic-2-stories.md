# Epic 2 Stories: User Registration & Verification

## Story 2.1: Telegram Bot Registration Flow

### User Story
As a **new community member**,  
I want **to register for the neighborhood sharing platform through Telegram**,  
So that **I can start sharing and receiving food in my building**.

### Acceptance Criteria

**Functional Requirements:**
1. User can start registration with /start command
2. Bot collects preferred name and apartment number through guided conversation  
3. User data is validated and stored in PostgreSQL users table
4. Bot provides clear next steps for phone verification
5. Registration state is maintained across conversation steps
6. Input validation prevents invalid apartment numbers/names

**Integration Requirements:**
7. Registration data follows existing user model schema
8. Database operations use established async SQLAlchemy patterns
9. Error handling follows existing bot error handling patterns

**Quality Requirements:**
10. Registration conversation is intuitive and user-friendly
11. Input validation provides helpful error messages
12. Registration state persists across bot restarts
13. Performance impact is minimal on bot response time

### Technical Implementation
- **Database:** Insert into users table with initial status 'pending_verification'
- **Bot Framework:** Use ConversationHandler with states for name/apartment collection
- **Validation:** Regex validation for apartment numbers, length limits for names
- **State Management:** Redis-backed conversation state storage

### Definition of Done
- [ ] /start command initiates registration flow
- [ ] Multi-step conversation collects name and apartment
- [ ] Input validation with user-friendly error messages
- [ ] User record created in database with correct schema
- [ ] Clear progression to phone verification step
- [ ] State management handles interruptions gracefully

---

## Story 2.2: Phone Number Verification  

### User Story
As a **registering user**,  
I want **to verify my phone number via SMS**,  
So that **the platform can confirm I'm a real person and enable notifications**.

### Acceptance Criteria

**Functional Requirements:**
1. Bot requests phone number using Telegram's native contact sharing
2. SMS verification code is sent via external SMS service
3. User can enter verification code through bot conversation
4. Phone verification status is stored in user profile
5. Failed verification attempts are rate-limited
6. Users can request new verification codes with cooldown period

**Integration Requirements:**
7. SMS service integration follows existing external API patterns
8. Phone number storage uses encryption for privacy protection
9. Rate limiting uses existing Redis-based limiting infrastructure

**Security Requirements:**
10. Phone numbers are encrypted before database storage
11. Verification codes expire after 10 minutes
12. Maximum 5 verification attempts per hour per user
13. Verification codes are cryptographically secure random

### Technical Implementation
- **SMS Service:** Integration with Twilio/AWS SNS for SMS delivery
- **Encryption:** Phone numbers encrypted with application secret key
- **Rate Limiting:** Redis-based attempt tracking with TTL
- **Code Generation:** 6-digit numeric codes with crypto.random

### Definition of Done
- [ ] Phone number collection via Telegram contact sharing
- [ ] SMS verification code delivery working reliably
- [ ] Code verification with attempt limiting
- [ ] Phone verification status updated in user profile
- [ ] Rate limiting prevents abuse
- [ ] Encrypted phone number storage

---

## Story 2.3: Location Verification

### User Story
As a **phone-verified user**,  
I want **to confirm my apartment location**,  
So that **I can only see and share food within my immediate neighborhood**.

### Acceptance Criteria

**Functional Requirements:**
1. Bot requests building address confirmation
2. User location is validated against configured service area
3. User is assigned to appropriate neighborhood/building group
4. Location verification status enables food sharing features
5. Bot explains proximity-based food sharing rules
6. Location data is stored securely with privacy protections

**Integration Requirements:**
7. Location data follows existing address schema in user table
8. Neighborhood assignment uses existing geographic grouping logic
9. Verification status gates access to food sharing commands

**Privacy Requirements:**
10. Exact coordinates are not stored, only neighborhood/building assignment
11. Location data access is logged for audit purposes
12. Users can update location through support if needed

### Technical Implementation
- **Geographic Validation:** Point-in-polygon check against service area boundaries
- **Neighborhood Assignment:** Assign to building/block group for proximity matching
- **Privacy Protection:** Store neighborhood ID, not exact coordinates
- **Access Control:** Location verification required for /share and /browse commands

### Definition of Done
- [ ] Building address confirmation process
- [ ] Service area validation with clear error messages
- [ ] Neighborhood/building group assignment
- [ ] Location verification status enables food features
- [ ] Privacy-preserving location data storage
- [ ] Clear explanation of proximity-based sharing

---

## Story 2.4: User Profile Completion

### User Story
As a **verified user**,  
I want **to set my dietary preferences and sharing preferences**,  
So that **I receive relevant food recommendations and can participate effectively**.

### Acceptance Criteria

**Functional Requirements:**
1. Bot collects dietary restrictions (vegetarian, gluten-free, etc.)
2. User can set notification preferences for food availability
3. User can specify sharing time preferences (morning/evening)
4. Profile is marked as complete, enabling full platform features
5. User receives welcome message with platform overview
6. Bot explains credit system and how to earn initial credits

**Integration Requirements:**
7. Preference data stored in existing user profile schema
8. Dietary restrictions integrate with food filtering system
9. Notification preferences configure message delivery settings

**User Experience Requirements:**
10. Profile setup is optional but recommended
11. Users can skip sections and complete later
12. Clear explanation of how preferences improve experience

### Technical Implementation
- **Dietary Restrictions:** Multi-select from predefined list (vegetarian, vegan, gluten-free, etc.)
- **Notification Settings:** Time-based preferences for food availability alerts
- **Welcome Credits:** Automatic credit assignment upon profile completion
- **Feature Gating:** Profile completion unlocks advanced features

### Definition of Done
- [ ] Dietary restriction selection with multi-choice interface
- [ ] Notification preference configuration
- [ ] Sharing time preference setting
- [ ] Profile completion status tracking
- [ ] Welcome message with credit system explanation
- [ ] Initial credit allocation for new users