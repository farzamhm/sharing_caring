# Epic 3: Food Posting & Discovery - Core MVP Epic

## Epic Goal
Allow users to post food offerings with photos and details, and discover available food in their neighborhood through the Telegram bot interface.

## Epic Description

**System Context:**
- Core food sharing functionality for Telegram bot
- Technology stack: python-telegram-bot, FastAPI, PostgreSQL, S3 storage
- Integration points: Photo upload, food categorization, proximity matching

**Enhancement Details:**
- **What's being added:** Complete food sharing workflow from posting to discovery
- **How it integrates:** Multi-step bot conversations, photo handling, database storage
- **Success criteria:** Users can post food with photos, browse available food, request items

## Stories

1. **Story 3.1:** Food Posting Workflow (/share command with guided photo and details collection)
2. **Story 3.2:** Food Discovery & Browsing (/browse command with filtering)
3. **Story 3.3:** Food Request System (request handling and notifications)
4. **Story 3.4:** Food Post Management (edit, expire, cancel posts)

## Technical Requirements

- **Database:** Food posts table with full-text search capabilities
- **File Storage:** S3 integration for photo upload and compression
- **Search & Filtering:** Location-based proximity search with dietary filters
- **Bot Conversations:** Multi-step conversation handlers for food posting
- **Notifications:** Real-time notifications for food requests and status updates

## Success Metrics

- **Posting Completion Rate:** >90% of users who start /share complete the post
- **Photo Upload Success:** >95% of photos successfully uploaded and compressed
- **Discovery Engagement:** Users browse average 5+ food items per session
- **Request Response Time:** <15 minutes average from post to first request
- **Search Accuracy:** >90% of search results are relevant to user location/preferences

## Business Rules

- **Post Expiration:** Food posts automatically expire after 4 hours
- **Proximity Limit:** Users only see food within 500m radius (same building/immediate neighbors)
- **Photo Requirements:** All food posts must include a photo
- **Allergen Disclosure:** Users must specify common allergens (dairy, nuts, gluten, etc.)
- **Portion Limits:** Posts limited to 1-10 portions to prevent commercial use

## Dependencies

- **Prerequisite:** User registration and verification system (Epic 2)
- **External:** S3 bucket configuration and photo processing pipeline
- **Infrastructure:** Food service API endpoints and search indexing
- **Bot Framework:** Advanced conversation handlers and callback query processing

## Definition of Done

- ✅ Complete food posting workflow with photo upload
- ✅ Robust food discovery with location and dietary filtering
- ✅ Request system with real-time notifications
- ✅ Food post management (edit/cancel/expire) functionality
- ✅ Photo storage and compression working efficiently
- ✅ Search performance optimized for quick response times
- ✅ All business rules enforced at API and bot levels
- ✅ Error handling covers all edge cases (network failures, invalid uploads, etc.)