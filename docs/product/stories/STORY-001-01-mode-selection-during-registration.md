# Story 001.01: Mode Selection During Registration (ENHANCED FOR AI)

**Epic:** EPIC-001 - Dual-Mode Platform Foundation  
**Priority:** 🔴 CRITICAL - FIRST USER-FACING FEATURE  
**Story Points:** 5  
**Sprint:** 1  
**AI Developer Complexity:** MEDIUM - User interface implementation  

---

## 🤖 AI DEVELOPER: READ THIS FIRST

**This story implements the core mode selection feature that enables the dual-mode platform. Users must choose between Neighborhood Mode and Community Mode during registration.**

**CRITICAL FILES TO READ:**
- `/docs/product/epics/EPIC-001-Dual-Mode-Platform-Foundation.md` (mode specifications)
- `/src/bot/handlers/registration.py` (existing registration flow)  
- `/src/models/users.py` (user model with new mode fields)

**DEPENDENCIES:**
- Story 009-02 (Database schema) must be COMPLETE
- Story 009-03 (Valkey streams) must be COMPLETE

---

## User Story
**As a** new user registering for the platform  
**I want to** choose between Neighborhood Mode and Community Mode during registration  
**So that** I can join the appropriate community type that matches my sharing preferences and trust level  

---

## 🎯 EXACT IMPLEMENTATION REQUIREMENTS

### **STEP 1: Update User Registration Flow**

**File to modify:** `src/bot/handlers/registration.py`

```python
# EXACT IMPLEMENTATION - ADD TO EXISTING REGISTRATION FLOW
from src.services.event_publishers import ModeTransitionPublisher
from src.core.streams import ValkeyStreamManager

class RegistrationHandler:
    
    async def handle_mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mode selection during registration."""
        
        user_id = update.effective_user.id
        
        # Create mode selection keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    "🏠 Neighborhood Mode", 
                    callback_data="mode_neighborhood"
                ),
                InlineKeyboardButton(
                    "👥 Community Mode", 
                    callback_data="mode_community"
                )
            ],
            [
                InlineKeyboardButton(
                    "❓ Help Me Choose", 
                    callback_data="mode_help"
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🎉 Welcome to the Food Sharing Platform!

Please choose your sharing mode:

🏠 **Neighborhood Mode**
• High verification (SMS + address)  
• Share with building neighbors
• Maximum trust and security
• Perfect for apartment buildings

👥 **Community Mode**  
• Light verification (group membership)
• Share with Telegram group members
• Flexible and social
• Perfect for friend groups & communities

Your choice affects verification requirements and who you can share food with.

Which mode works best for you?
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_mode_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mode selection callback."""
        
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        if callback_data == "mode_help":
            await self.show_mode_comparison(query)
            return
        
        # Extract selected mode
        if callback_data == "mode_neighborhood":
            selected_mode = "neighborhood"
            verification_level = "full"
            next_step_text = """
✅ **Neighborhood Mode Selected**

Next steps for verification:
1. 📱 SMS phone verification
2. 🏠 Building address confirmation  
3. 🚪 Apartment number verification

This ensures maximum trust and security for building-based food sharing.

Ready to start verification?
            """
        elif callback_data == "mode_community":
            selected_mode = "community" 
            verification_level = "light"
            next_step_text = """
✅ **Community Mode Selected**

Next steps for verification:
1. 👥 Telegram group membership confirmation
2. 📍 Optional location sharing for pickup coordination

This enables flexible sharing with your existing communities.

Ready to start verification?
            """
        else:
            await query.edit_message_text("❌ Invalid selection. Please try again.")
            return
        
        # Store mode selection in database
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            if not user:
                # Create new user with mode selection
                user = User(
                    id=user_id,
                    username=update.effective_user.username,
                    sharing_mode=selected_mode,
                    verification_level=verification_level,
                    credits=10,  # Welcome bonus
                    created_at=datetime.utcnow()
                )
                session.add(user)
            else:
                # Update existing user
                old_mode = user.sharing_mode
                user.sharing_mode = selected_mode
                user.verification_level = verification_level
                
                # Publish mode transition event if mode changed
                if old_mode != selected_mode:
                    await self.publish_mode_transition(
                        user_id, old_mode, selected_mode, "user_selection"
                    )
            
            await session.commit()
        
        # Update message with confirmation
        keyboard = [
            [InlineKeyboardButton(
                "🚀 Start Verification", 
                callback_data=f"verify_{selected_mode}"
            )],
            [InlineKeyboardButton(
                "🔄 Change Mode", 
                callback_data="change_mode"
            )]
        ]
        
        await query.edit_message_text(
            next_step_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # Store context for next step
        context.user_data['selected_mode'] = selected_mode
        context.user_data['verification_level'] = verification_level
    
    async def show_mode_comparison(self, query):
        """Show detailed mode comparison."""
        
        comparison_text = """
📊 **Mode Comparison Guide**

| Feature | 🏠 Neighborhood | 👥 Community |
|---------|----------------|-------------|
| **Verification** | SMS + Address + Apt | Group Membership |
| **Who You Share With** | Building Neighbors | Group Members |
| **Pickup Location** | Same Building | User Coordinated |
| **Trust Level** | Highest | Social-Based |
| **Best For** | Apartments/Condos | Friends/Hobby Groups |

**🏠 Choose Neighborhood Mode if you:**
• Live in an apartment building or condo
• Want maximum verification and trust
• Prefer sharing with immediate neighbors  
• Value security over convenience

**👥 Choose Community Mode if you:**
• Are part of Telegram groups/communities
• Want flexible, social-based sharing
• Prefer lighter verification requirements
• Value convenience and social connections

Which sounds right for your situation?
        """
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "🏠 Neighborhood Mode", 
                    callback_data="mode_neighborhood"
                ),
                InlineKeyboardButton(
                    "👥 Community Mode", 
                    callback_data="mode_community"
                )
            ]
        ]
        
        await query.edit_message_text(
            comparison_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def publish_mode_transition(self, user_id: int, from_mode: str, to_mode: str, reason: str):
        """Publish mode transition event to streams."""
        
        stream_manager = ValkeyStreamManager(get_valkey_client())
        mode_publisher = ModeTransitionPublisher(stream_manager)
        
        try:
            await mode_publisher.publish_mode_transition(
                UUID(str(user_id)), from_mode, to_mode, reason
            )
        except Exception as e:
            # Log error but don't fail registration
            logger.error(f"Failed to publish mode transition event: {e}")
```

### **STEP 2: Update Database Models**

**File to verify:** `src/models/users.py`

```python
# VERIFY THESE FIELDS EXIST IN USER MODEL (from Story 009-02)
class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    username = Column(String(255))
    
    # NEW FIELDS FOR DUAL-MODE (verify these exist)
    sharing_mode = Column(String(20), default='neighborhood')  # 'neighborhood' or 'community'
    verification_level = Column(String(20), default='full')    # 'full' or 'light'
    
    # Existing fields
    phone_number = Column(String(20))
    building_id = Column(UUID, ForeignKey('buildings.id'))
    credits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### **STEP 3: Add Bot Command Handlers**

**File to modify:** `src/bot/main.py`

```python
# ADD THESE HANDLERS TO EXISTING BOT SETUP
def setup_handlers(application: Application):
    # Existing handlers...
    
    # NEW MODE SELECTION HANDLERS
    application.add_handler(CallbackQueryHandler(
        registration_handler.handle_mode_callback,
        pattern="^mode_"
    ))
    
    application.add_handler(CallbackQueryHandler(
        registration_handler.handle_mode_callback,
        pattern="^verify_"
    ))
    
    application.add_handler(CallbackQueryHandler(
        registration_handler.handle_mode_callback, 
        pattern="^change_mode$"
    ))
    
    # Update existing /start command to include mode selection
    application.add_handler(CommandHandler(
        "start", 
        registration_handler.handle_start_with_mode_selection
    ))
```

### **STEP 4: Update Start Command**

**File to modify:** `src/bot/handlers/registration.py`

```python
async def handle_start_with_mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced start command with mode selection for new users."""
    
    user_id = update.effective_user.id
    
    # Check if user already exists and has selected mode
    async with get_db_session() as session:
        user = await session.get(User, user_id)
        
        if user and user.sharing_mode:
            # Existing user - show current mode and options
            await self.show_existing_user_welcome(update, user)
            return
    
    # New user - show mode selection
    await self.handle_mode_selection(update, context)

async def show_existing_user_welcome(self, update: Update, user: User):
    """Show welcome message for existing users."""
    
    mode_emoji = "🏠" if user.sharing_mode == "neighborhood" else "👥"
    mode_name = "Neighborhood Mode" if user.sharing_mode == "neighborhood" else "Community Mode"
    
    welcome_text = f"""
👋 Welcome back!

**Current Mode:** {mode_emoji} {mode_name}
**Credits:** 💰 {user.credits}
**Trust Level:** ⭐ {user.reputation.trust_level if user.reputation else 'New'}

What would you like to do?
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🍕 Share Food", callback_data="share_food"),
            InlineKeyboardButton("🔍 Browse Food", callback_data="browse_food")
        ],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton("🔄 Change Mode", callback_data="change_mode")
        ]
    ]
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
```

---

## ✅ ACCEPTANCE CRITERIA (ALL MUST BE MET)

### **User Interface:**
- [ ] Mode selection appears immediately after /start command for new users
- [ ] Two clear mode options with emoji indicators (🏠 Neighborhood, 👥 Community)
- [ ] Help button provides detailed mode comparison table
- [ ] Selected mode is visually confirmed before proceeding
- [ ] Users can change their selection before confirming

### **Data Storage:**
- [ ] Mode selection stored in `users.sharing_mode` field
- [ ] Verification level stored in `users.verification_level` field  
- [ ] Mode transitions published to `user.mode.transitions` stream
- [ ] Welcome credits (10) awarded upon mode selection

### **User Experience:**
- [ ] Clear explanations of each mode's requirements and benefits
- [ ] Intuitive interface that doesn't confuse users
- [ ] Responsive buttons and immediate feedback
- [ ] Help/comparison easily accessible during decision

### **Technical Integration:**
- [ ] Event publishing to Valkey streams working correctly
- [ ] Database updates transactional and error-handled
- [ ] Bot conversation flow handles errors gracefully
- [ ] Mode selection affects subsequent verification flow

---

## 🧪 TESTING REQUIREMENTS

### **Manual Testing Script:**
```bash
# Test new user registration flow
1. Send /start to bot as new user
2. Verify mode selection appears
3. Click "Help Me Choose" - verify comparison appears
4. Select "🏠 Neighborhood Mode" - verify confirmation
5. Verify database shows sharing_mode='neighborhood'
6. Verify stream event published

# Test existing user
1. Send /start as existing user  
2. Verify personalized welcome appears
3. Verify current mode displayed correctly
```

### **Automated Testing:**
```python
# Test mode selection handler
async def test_mode_selection():
    # Mock telegram update with callback
    update = create_mock_callback_update("mode_neighborhood")
    
    await registration_handler.handle_mode_callback(update, context)
    
    # Verify database updated
    user = await get_user(update.effective_user.id)
    assert user.sharing_mode == "neighborhood"
    
    # Verify stream event published
    assert mock_stream_publisher.called
```

---

## 🚨 CRITICAL WARNINGS FOR AI DEVELOPERS

❌ **DO NOT:**
- Skip the mode selection step in registration
- Use different mode names than "neighborhood" and "community"  
- Forget to publish mode transition events
- Make mode selection optional (it's required)

✅ **MUST DO:**
- Show clear comparison between modes
- Store exact mode values in database
- Handle all error cases gracefully  
- Test with both new and existing users

⚠️ **CRITICAL:**
This is the foundation for the entire dual-mode system. If mode selection fails, users cannot proceed with registration.

---

## 📋 COMPLETION CHECKLIST

**Before marking story complete:**
- [ ] Mode selection interface working in Telegram bot
- [ ] Database fields updated correctly for both modes
- [ ] Stream events published successfully  
- [ ] Help/comparison feature working
- [ ] Error handling implemented for all edge cases
- [ ] Existing user welcome flow updated
- [ ] All manual testing scenarios pass
- [ ] Automated tests pass

**Story is complete when:** New users can successfully select either Neighborhood Mode or Community Mode during registration, with the selection properly stored and published to event streams.