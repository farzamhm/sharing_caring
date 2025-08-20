# API Specifications - Neighborhood Sharing Platform

**Version:** 1.0  
**Date:** January 2024  
**Environment:** MVP Development  

---

## API Overview

### Base Configuration
```python
# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = "https://api.neighborshare.app/bot/webhook"
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL with PostGIS
REDIS_URL = os.getenv("REDIS_URL")  # Redis for caching
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
RATE_LIMIT = "10 requests/minute per user"
```

### Authentication
All API calls authenticated via Telegram user ID and session validation.

---

## Telegram Bot Commands API

### Core Commands

#### `/start` - User Registration
**Description:** Initiates new user registration flow  
**Handler:** `handleStart(ctx)`

**Request Flow:**
```python
# Initial command handler
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user exists
    user = await user_service.get_user_by_telegram_id(user_id)
    
    if user:
        return await send_welcome_back_message(update, context, user)
    else:
        return await initiate_registration(update, context)
```

**Response Example:**
```
Welcome to Neighborhood Sharing! 🏠

To get started, I need to verify you're a real neighbor.
Please share your phone number for verification.

[Share Phone Number] [Learn More] [Skip for Now]
```

**Database Operations:**
```sql
-- Check existing user
SELECT * FROM users WHERE telegram_id = $1;

-- Create new user record
INSERT INTO users (telegram_id, registration_started_at) 
VALUES ($1, NOW()) 
ON CONFLICT (telegram_id) DO NOTHING;
```

#### `/share` - Post Food Offering
**Description:** Creates new food sharing post  
**Handler:** `handleShare(ctx)`

**Multi-step Flow:**
```python
# Share flow state machine
class ShareFlowState(Enum):
    ASK_FOOD_NAME = 1
    ASK_PORTIONS = 2
    REQUEST_PHOTO = 3
    ASK_PICKUP_TIME = 4
    ASK_ALLERGENS = 5
    CONFIRM_POST = 6

# Flow handlers
share_flow_handlers = {
    ShareFlowState.ASK_FOOD_NAME: ask_food_name,
    ShareFlowState.ASK_PORTIONS: ask_portions,
    ShareFlowState.REQUEST_PHOTO: request_photo,
    ShareFlowState.ASK_PICKUP_TIME: ask_pickup_time,
    ShareFlowState.ASK_ALLERGENS: ask_allergens,
    ShareFlowState.CONFIRM_POST: confirm_post
}
```

**Step 1: Food Name**
```
Bot: "What food are you sharing? 🍽️"
User: "Chicken curry"
Session: {step: 2, foodName: "Chicken curry"}
```

**Step 2: Portions**
```
Bot: "How many portions do you have? (1-10)"
User: "3"
Session: {step: 3, foodName: "Chicken curry", portions: 3}
```

**Step 3: Photo Upload**
```
Bot: "Please upload a photo of your food 📸"
User: [uploads photo]
Response: Upload to S3, save URL
Session: {step: 4, ..., photoUrl: "https://s3.../photo.jpg"}
```

**Step 4: Pickup Time**
```
Bot: "When can people pick up? Examples:
• 6-7pm today
• 5:30-6:30pm  
• Available now for 2 hours"
User: "6-7pm today"
Session: {step: 5, ..., pickupWindow: "6-7pm today"}
```

**Step 5: Allergens**
```
Bot: "Does your food contain any of these?
[🥛 Dairy] [🥜 Nuts] [🌾 Gluten] [🥚 Eggs] [✅ None]"
User: Selects "Dairy"
Session: {step: 6, ..., allergens: ["dairy"]}
```

**Step 6: Confirmation**
```
Bot: "Ready to post? 🚀

🍛 Chicken Curry (3 portions)
📸 [Photo attached]
⏰ Pickup: 6-7pm today  
⚠️ Contains: Dairy
📍 From: Apt 4B

[✅ Post Now] [✏️ Edit] [❌ Cancel]"
```

**Database Schema:**
```sql
INSERT INTO food_posts (
  user_id, food_name, portions, photo_url, 
  allergens, pickup_start, pickup_end, 
  status, created_at, expires_at
) VALUES (
  $1, $2, $3, $4, $5, $6, $7, 
  'available', NOW(), NOW() + INTERVAL '4 hours'
);
```

#### `/browse` - View Available Food
**Description:** Shows available food filtered by user preferences  
**Handler:** `handleBrowse(ctx)`

**Request Processing:**
```python
async def handle_browse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await user_service.get_user_by_id(user_id)
    
    # Get available food posts
    foods = await food_service.get_available_food(
        exclude_user_id=user_id,
        dietary_restrictions=user.dietary_restrictions,
        radius_km=1.0,
        limit=10
    )
    
    return await format_food_list(update, context, foods)
```

**SQL Query:**
```sql
SELECT 
  fp.id, fp.food_name, fp.portions, fp.photo_url,
  fp.allergens, fp.pickup_start, fp.pickup_end,
  u.preferred_name, u.apartment_number,
  ST_Distance(u1.location_coords, u2.location_coords) as distance
FROM food_posts fp
JOIN users u ON fp.user_id = u.id
JOIN users u1 ON u1.telegram_id = $1  -- Current user
JOIN users u2 ON fp.user_id = u2.id   -- Food poster
WHERE fp.status = 'available'
  AND fp.expires_at > NOW()
  AND fp.user_id != u1.id
  AND NOT (fp.allergens && $2)  -- Exclude allergens
  AND ST_DWithin(u1.location_coords, u2.location_coords, 1000)
ORDER BY fp.pickup_start ASC
LIMIT 10;
```

**Response Format:**
```
Available Food Near You 🍽️

🍛 Chicken Curry (3 portions)
   👤 From: Sarah M. (Apt 4B)
   ⏰ Pickup: 6-7pm today
   📍 Distance: 2 floors up
   ⚠️ Contains: Dairy
   [🙋 Request] [ℹ️ Details]

🥗 Garden Salad (2 portions)
   👤 From: Mike L. (Apt 2A) 
   ⏰ Pickup: 5:30-6:30pm today
   📍 Distance: Same floor
   ✅ No allergens
   [🙋 Request] [ℹ️ Details]

---
🔄 Updated just now • [Refresh] [Filter]
```

#### `/request` - Request Food Item
**Description:** Request specific food posting  
**Handler:** `handleRequest(ctx, foodPostId)`

**Callback Query Processing:**
```python
async def handle_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Parse callback data
    action, food_post_id = query.data.split('_')
    food_post_id = int(food_post_id)
    user_id = update.effective_user.id
    
    # Validate request
    validation = await exchange_service.validate_request(user_id, food_post_id)
    if not validation.is_valid:
        await query.edit_message_text(validation.error_message)
        return
    
    # Create exchange request
    request = await exchange_service.create_exchange_request(user_id, food_post_id)
    
    # Notify both parties
    await notification_service.notify_sharer(request)
    await notification_service.notify_requester(request)
```

**Database Operations:**
```sql
-- Create exchange request
INSERT INTO exchange_requests (food_post_id, requester_id, status)
VALUES ($1, $2, 'pending')
RETURNING id;

-- Update food post status if needed
UPDATE food_posts 
SET status = 'pending_pickup' 
WHERE id = $1 AND status = 'available';
```

**Notification Messages:**
```python
# Notification message templates
async def create_sharer_notification(requester: User, food_post: FoodPost) -> str:
    return f"""🙋‍♂️ {requester.preferred_name} (Apt {requester.apartment_number}) wants your {food_post.food_name}!

[✅ Confirm Pickup] [💬 Message {requester.preferred_name}] [❌ Decline]"""

async def create_requester_notification(sharer: User) -> str:
    return f"""📤 Request sent to {sharer.preferred_name}!

You'll get pickup details once they confirm.
[💬 Message {sharer.preferred_name}] [❌ Cancel Request]"""
```

#### `/credits` - View Credit Balance
**Description:** Shows user's credit balance and transaction history  
**Handler:** `handleCredits(ctx)`

**Response Processing:**
```python
async def handle_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Calculate current balance
    balance = await credit_service.get_credit_balance(user_id)
    
    # Get recent transactions
    transactions = await credit_service.get_recent_transactions(user_id, limit=10)
    
    return await format_credits_display(update, context, balance, transactions)
```

**Credit Balance Query:**
```sql
SELECT COALESCE(SUM(amount), 0) as balance
FROM credits 
WHERE user_id = (
  SELECT id FROM users WHERE telegram_id = $1
);
```

**Recent Transactions Query:**
```sql
SELECT c.amount, c.transaction_type, c.description, c.created_at,
       fp.food_name, u.preferred_name as other_party
FROM credits c
LEFT JOIN exchange_requests er ON c.exchange_request_id = er.id
LEFT JOIN food_posts fp ON er.food_post_id = fp.id
LEFT JOIN users u ON (
  CASE 
    WHEN c.transaction_type = 'earned' THEN er.requester_id
    WHEN c.transaction_type = 'spent' THEN fp.user_id
  END
) = u.id
WHERE c.user_id = (SELECT id FROM users WHERE telegram_id = $1)
ORDER BY c.created_at DESC
LIMIT $2;
```

**Display Format:**
```
💰 Your Credit Balance

Current Balance: 5 credits

Recent Activity:
✅ +1 credit - Shared Chicken Curry with Mike L.
❌ -1 credit - Received Garden Salad from Sarah M.
🎁 +2 credits - Welcome bonus
✅ +1 credit - Shared Pasta Bake with Jane K.

[📊 Full History] [❓ How Credits Work]
```

#### `/rate` - Rate Exchange
**Description:** Rate completed food exchange  
**Handler:** `handleRate(ctx, exchangeId)`

**Rating Flow:**
```python
class RatingFlowState(Enum):
    ASK_FOOD_RATING = 1
    ASK_INTERACTION_RATING = 2
    ASK_OPTIONAL_COMMENT = 3
    CONFIRM_RATING = 4

rating_flow_handlers = {
    RatingFlowState.ASK_FOOD_RATING: ask_food_rating,
    RatingFlowState.ASK_INTERACTION_RATING: ask_interaction_rating,
    RatingFlowState.ASK_OPTIONAL_COMMENT: ask_optional_comment,
    RatingFlowState.CONFIRM_RATING: confirm_rating
}
```

**Step 1: Food Rating**
```
Bot: "How was the food? ⭐

Rate the quality, freshness, and taste:
[⭐] [⭐⭐] [⭐⭐⭐] [⭐⭐⭐⭐] [⭐⭐⭐⭐⭐]"
```

**Step 2: Interaction Rating**
```
Bot: "How was the interaction? 🤝

Rate communication and reliability:
[⭐] [⭐⭐] [⭐⭐⭐] [⭐⭐⭐⭐] [⭐⭐⭐⭐⭐]"
```

**Database Schema:**
```sql
INSERT INTO ratings (
  exchange_request_id, rater_id, rated_id,
  food_rating, interaction_rating, comment
) VALUES ($1, $2, $3, $4, $5, $6);
```

#### `/report` - Report Issue
**Description:** Report safety or quality issues  
**Handler:** `handleReport(ctx)`

**Report Categories:**
```python
class ReportCategory(Enum):
    FOOD_SAFETY = "food_safety"      # Illness, spoiled food, hygiene
    NO_SHOW = "no_show"              # Failed pickup, poor communication
    HARASSMENT = "harassment"        # Inappropriate behavior
    FALSE_INFO = "false_info"        # Wrong ingredients, fake photos
    OTHER = "other"                  # General concerns

REPORT_CATEGORY_DESCRIPTIONS = {
    ReportCategory.FOOD_SAFETY: "Illness, spoiled food, hygiene issues",
    ReportCategory.NO_SHOW: "Failed pickup, poor communication",
    ReportCategory.HARASSMENT: "Inappropriate behavior",
    ReportCategory.FALSE_INFO: "Wrong ingredients, fake photos",
    ReportCategory.OTHER: "General concerns"
}
```

**Report Flow:**
```
Bot: "What type of issue are you reporting? 🚨

[🦠 Food Safety] [👻 No-Show] [😠 Harassment] 
[❌ False Info] [📝 Other Issue]"

User selects category...

Bot: "Please describe what happened (minimum 20 characters):"
User: "The food had an unusual smell and made me feel sick"

Bot: "Would you like to upload photo evidence? (Optional)"
[📸 Upload Photo] [➡️ Continue Without Photo]

Bot: "Report submitted! 
Report ID: #RS2024-001
You'll hear back within 24 hours.

[📞 Emergency Contact] [ℹ️ Next Steps]"
```

---

## Internal API Endpoints

### User Management

#### `POST /api/users/verify-phone`
**Description:** Verify user phone number via SMS

**Request:**
```json
{
  "telegram_id": 123456789,
  "phone_number": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "verification_code_sent": true,
  "expires_in": 600
}
```

#### `POST /api/users/confirm-verification`
**Request:**
```json
{
  "telegram_id": 123456789,
  "verification_code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "user_verified": true,
  "next_step": "location_verification"
}
```

### Food Posts Management

#### `GET /api/food-posts/available`
**Description:** Get available food posts for user

**Query Parameters:**
```
user_id: number (required)
radius: string (default: '1km')
dietary_restrictions: string[] (optional)
limit: number (default: 10)
```

**Response:**
```json
{
  "success": true,
  "posts": [
    {
      "id": 123,
      "food_name": "Chicken Curry",
      "portions": 3,
      "photo_url": "https://s3.../photo.jpg",
      "allergens": ["dairy"],
      "pickup_start": "2024-01-15T18:00:00Z",
      "pickup_end": "2024-01-15T19:00:00Z",
      "sharer": {
        "preferred_name": "Sarah M.",
        "apartment_number": "4B"
      },
      "distance_meters": 50
    }
  ],
  "total": 5
}
```

#### `POST /api/food-posts`
**Description:** Create new food post

**Request:**
```json
{
  "user_id": 456,
  "food_name": "Chicken Curry",
  "portions": 3,
  "photo_url": "https://s3.../photo.jpg",
  "allergens": ["dairy"],
  "pickup_start": "2024-01-15T18:00:00Z",
  "pickup_end": "2024-01-15T19:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "post_id": 124,
  "expires_at": "2024-01-15T22:00:00Z"
}
```

### Exchange Management

#### `POST /api/exchanges/request`
**Description:** Create exchange request

**Request:**
```json
{
  "food_post_id": 123,
  "requester_id": 789
}
```

**Response:**
```json
{
  "success": true,
  "request_id": 456,
  "status": "pending",
  "notifications_sent": true
}
```

#### `PUT /api/exchanges/{id}/confirm`
**Description:** Confirm exchange pickup

**Request:**
```json
{
  "confirming_user_id": 456,
  "pickup_time": "2024-01-15T18:30:00Z"
}
```

---

## File Upload API

### Photo Upload Flow

#### `POST /api/upload/photo`
**Description:** Upload food photo to S3

**Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer {jwt_token}
```

**Request:**
```python
# FastAPI endpoint for photo upload
@app.post("/api/upload/photo")
async def upload_photo(
    photo: UploadFile = File(...),
    user_id: int = Form(...),
    purpose: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file type and size
    if photo.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Invalid file type")
    
    # Upload to S3
    s3_url = await s3_service.upload_file(photo, user_id, purpose)
    return {"photo_url": s3_url, "thumbnail_url": f"{s3_url}_thumb"}
```

**Response:**
```json
{
  "success": true,
  "photo_url": "https://s3.amazonaws.com/bucket/photos/uuid.jpg",
  "thumbnail_url": "https://s3.amazonaws.com/bucket/thumbs/uuid.jpg",
  "file_size": 1024000,
  "dimensions": {
    "width": 1080,
    "height": 720
  }
}
```

**Validation Rules:**
- Maximum file size: 5MB
- Allowed formats: JPEG, PNG, WebP
- Automatic compression for mobile
- Thumbnail generation (300x200)
- EXIF data removal for privacy

---

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "User-friendly error message",
    "details": "Technical details for debugging",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes
```python
class ErrorCode(Enum):
    # Authentication
    INVALID_TOKEN = "INVALID_TOKEN"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    LOCATION_NOT_VERIFIED = "LOCATION_NOT_VERIFIED"
    
    # Food Posts
    POST_NOT_FOUND = "POST_NOT_FOUND"
    POST_ALREADY_CLAIMED = "POST_ALREADY_CLAIMED"
    CANNOT_REQUEST_OWN_POST = "CANNOT_REQUEST_OWN_POST"
    
    # Credits
    INSUFFICIENT_CREDITS = "INSUFFICIENT_CREDITS"
    INVALID_CREDIT_AMOUNT = "INVALID_CREDIT_AMOUNT"
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    DAILY_LIMIT_REACHED = "DAILY_LIMIT_REACHED"
    
    # Validation
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"

ERROR_MESSAGES = {
    ErrorCode.INVALID_TOKEN: "Invalid or expired authentication token",
    ErrorCode.USER_NOT_VERIFIED: "User phone number not verified",
    ErrorCode.LOCATION_NOT_VERIFIED: "User location not verified",
    ErrorCode.POST_NOT_FOUND: "Food post not found or expired",
    ErrorCode.POST_ALREADY_CLAIMED: "Food post already claimed by someone else",
    ErrorCode.CANNOT_REQUEST_OWN_POST: "Cannot request your own food post",
    ErrorCode.INSUFFICIENT_CREDITS: "Not enough credits for this action",
    ErrorCode.INVALID_CREDIT_AMOUNT: "Credit amount must be positive",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Too many requests, please try again later",
    ErrorCode.DAILY_LIMIT_REACHED: "Daily action limit reached",
    ErrorCode.INVALID_INPUT: "Input validation failed",
    ErrorCode.MISSING_REQUIRED_FIELD: "Required field missing",
    ErrorCode.FILE_TOO_LARGE: "Uploaded file exceeds size limit"
}
```

---

## Rate Limiting

### Bot Commands
```python
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class RateLimit:
    requests: int
    window: timedelta

RATE_LIMITS = {
    "global": RateLimit(10, timedelta(minutes=1)),
    "share": RateLimit(5, timedelta(hours=1)),
    "request": RateLimit(20, timedelta(hours=1)),
    "report": RateLimit(3, timedelta(days=1)),
    "upload": RateLimit(10, timedelta(hours=1))
}
```

### Implementation
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/bot/webhook")
@limiter.limit("10/minute")
async def bot_webhook(request: Request, update: dict):
    # Process telegram update
    pass
```

---

## Webhook Configuration

### Telegram Webhook Setup
```python
import asyncio
from telegram import Bot
from telegram.constants import UpdateType

async def setup_webhook():
    bot = Bot(token=BOT_TOKEN)
    
    webhook_config = {
        "url": "https://api.neighborshare.app/bot/webhook",
        "allowed_updates": [
            UpdateType.MESSAGE,
            UpdateType.CALLBACK_QUERY,
            UpdateType.INLINE_QUERY
        ],
        "drop_pending_updates": True
    }
    
    await bot.set_webhook(**webhook_config)
    print("Webhook configured successfully")

# Run setup
asyncio.run(setup_webhook())
```

### Webhook Security
```python
import hmac
import hashlib
from fastapi import HTTPException, Request

async def verify_telegram_webhook(request: Request):
    """Verify webhook requests from Telegram"""
    token = BOT_TOKEN.encode('utf-8')
    body = await request.body()
    
    # Calculate expected signature
    expected_hash = hmac.new(
        token, 
        body, 
        hashlib.sha256
    ).hexdigest()
    
    # Get signature from headers
    signature = request.headers.get('x-telegram-bot-api-secret-token')
    
    if not signature or not hmac.compare_digest(signature, expected_hash):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return True
```

## Python Logging Integration for Elasticsearch

### Structured Logging Setup
```python
import logging
import json
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from typing import Dict, Any

class ElasticsearchHandler(logging.Handler):
    """Custom logging handler that sends logs to Elasticsearch"""
    
    def __init__(self, elasticsearch_client: AsyncElasticsearch, index_prefix: str = "app-logs"):
        super().__init__()
        self.es_client = elasticsearch_client
        self.index_prefix = index_prefix
    
    def emit(self, record: logging.LogRecord):
        """Send log record to Elasticsearch"""
        try:
            # Create structured log entry
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "service": "neighborhood-sharing-api"
            }
            
            # Add extra fields if present
            if hasattr(record, 'user_id'):
                log_entry["user_id"] = record.user_id
            if hasattr(record, 'food_post_id'):
                log_entry["food_post_id"] = record.food_post_id
            if hasattr(record, 'exchange_id'):
                log_entry["exchange_id"] = record.exchange_id
            
            # Create index name with date
            index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m.%d')}"
            
            # Send to Elasticsearch (async)
            asyncio.create_task(self._send_to_elasticsearch(index_name, log_entry))
            
        except Exception as e:
            # Fallback to standard logging
            print(f"Failed to send log to Elasticsearch: {e}")
    
    async def _send_to_elasticsearch(self, index_name: str, log_entry: Dict[str, Any]):
        """Async method to send log to Elasticsearch"""
        try:
            await self.es_client.index(
                index=index_name,
                body=log_entry
            )
        except Exception as e:
            print(f"Elasticsearch indexing failed: {e}")

# Logger configuration
def setup_logging(elasticsearch_client: AsyncElasticsearch):
    """Configure logging with Elasticsearch integration"""
    
    # Create formatter for structured logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup Elasticsearch handler
    es_handler = ElasticsearchHandler(elasticsearch_client)
    es_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(es_handler)
    
    return root_logger

# Business metrics logging
class BusinessMetricsLogger:
    """Logger for business metrics and events"""
    
    def __init__(self, elasticsearch_client: AsyncElasticsearch):
        self.es_client = elasticsearch_client
        self.logger = logging.getLogger("business_metrics")
    
    async def log_food_exchange(self, exchange_data: Dict[str, Any]):
        """Log food exchange completion"""
        metric_entry = {
            "timestamp": datetime.now().isoformat(),
            "metric_type": "food_exchange",
            "exchange_id": exchange_data["exchange_id"],
            "food_post_id": exchange_data["food_post_id"],
            "sharer_id": exchange_data["sharer_id"],
            "requester_id": exchange_data["requester_id"],
            "completion_time_minutes": exchange_data.get("completion_time"),
            "rating": exchange_data.get("rating"),
            "food_type": exchange_data.get("food_type"),
            "success": True
        }
        
        # Send to business metrics index
        index_name = f"business-metrics-{datetime.now().strftime('%Y.%m.%d')}"
        await self.es_client.index(
            index=index_name,
            body=metric_entry
        )
        
        # Also log to standard logger
        self.logger.info(
            "Food exchange completed",
            extra={
                "exchange_id": exchange_data["exchange_id"],
                "food_post_id": exchange_data["food_post_id"]
            }
        )
    
    async def log_user_registration(self, user_id: int, telegram_id: int):
        """Log new user registration"""
        metric_entry = {
            "timestamp": datetime.now().isoformat(),
            "metric_type": "user_registration",
            "user_id": user_id,
            "telegram_id": telegram_id,
            "registration_source": "telegram_bot"
        }
        
        index_name = f"business-metrics-{datetime.now().strftime('%Y.%m.%d')}"
        await self.es_client.index(
            index=index_name,
            body=metric_entry
        )

# Usage in FastAPI application
from fastapi import FastAPI, Request
from elasticsearch import AsyncElasticsearch
import time

app = FastAPI()
es_client = AsyncElasticsearch(hosts=["elasticsearch:9200"])
business_metrics = BusinessMetricsLogger(es_client)

# Setup logging
logger = setup_logging(es_client)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration * 1000,
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host
        }
    )
    
    return response

# Example usage in endpoint
@app.post("/api/food-posts")
async def create_food_post(food_data: FoodPostCreate, current_user: User = Depends(get_current_user)):
    try:
        # Create food post
        food_post = await food_service.create_food_post(food_data, current_user.id)
        
        # Log successful creation
        logger.info(
            "Food post created successfully",
            extra={
                "user_id": current_user.id,
                "food_post_id": food_post.id,
                "food_name": food_post.food_name,
                "portions": food_post.portions
            }
        )
        
        return food_post
        
    except Exception as e:
        # Log error
        logger.error(
            f"Failed to create food post: {str(e)}",
            extra={
                "user_id": current_user.id,
                "error_type": type(e).__name__,
                "food_name": food_data.food_name
            }
        )
        raise
```

This comprehensive API specification covers all the core functionality needed for the MVP Telegram bot, including Python-based implementation with Elasticsearch integration for monitoring and business intelligence. Each endpoint includes request/response examples, database operations, error handling patterns, and structured logging.