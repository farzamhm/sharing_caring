# Epic 4: Exchange Coordination & Credit System - Core MVP Epic

## Epic Goal  
Facilitate actual food exchanges between users with credit-based incentive system, pickup coordination, and completion tracking.

## Epic Description

**System Context:**
- Exchange management and credit tracking functionality
- Technology stack: FastAPI, PostgreSQL, Redis, Telegram notifications
- Integration points: Credit calculations, exchange state management, notifications

**Enhancement Details:**
- **What's being added:** Complete exchange lifecycle from request to completion with credits
- **How it integrates:** State machine for exchanges, credit transaction system, notification workflow
- **Success criteria:** Users can coordinate pickups, complete exchanges, earn/spend credits

## Stories

1. **Story 4.1:** Exchange Request & Confirmation (match users, confirm details)
2. **Story 4.2:** Pickup Coordination (time/location coordination via bot)
3. **Story 4.3:** Exchange Completion & Rating (completion verification, rating system)
4. **Story 4.4:** Credit System Implementation (earn/spend credits, balance tracking)

## Technical Requirements

- **Database:** Exchange requests table with state tracking, credits transaction log
- **State Management:** Exchange state machine (requested → confirmed → in_progress → completed)
- **Credit System:** Transaction-safe credit operations with audit trail
- **Notifications:** Multi-party notification system for exchange updates
- **Rating System:** 5-star rating with optional comments and reputation tracking

## Credit System Rules

- **Earning Credits:** +1 credit for each completed food share
- **Spending Credits:** -1 credit charged when food request is confirmed (not on request)
- **Welcome Credits:** New users receive 3 credits to bootstrap participation
- **Credit Balance:** Minimum 1 credit required to make food requests
- **Transaction Safety:** All credit operations are atomic and logged
- **Refund Policy:** Credits refunded if exchange is cancelled before pickup

## Exchange State Machine

```
requested → confirmed → in_progress → completed
     ↓         ↓            ↓
  cancelled  cancelled   cancelled
```

## Success Metrics

- **Exchange Completion Rate:** >85% of confirmed exchanges successfully complete
- **Average Exchange Time:** <2 hours from confirmation to completion
- **Credit System Adoption:** >90% of active users have positive credit balance
- **Rating Participation:** >70% of completed exchanges receive ratings
- **User Satisfaction:** Average rating >4.0 stars across all exchanges

## Business Rules

- **Exchange Timeouts:** Unconfirmed requests expire after 30 minutes
- **Pickup Windows:** Default 1-hour pickup windows, customizable by food poster
- **Rating Requirements:** Both parties must rate exchange for credits to be awarded
- **Credit Limits:** Maximum 50 credits per user to encourage circulation
- **Dispute Resolution:** Admin override capabilities for credit adjustments

## Dependencies

- **Prerequisite:** Food posting and discovery system (Epic 3)
- **Infrastructure:** Redis for state management and real-time notifications
- **Database:** ACID-compliant credit transactions
- **Bot Framework:** Advanced notification and confirmation workflows

## Definition of Done

- ✅ Complete exchange request and confirmation workflow
- ✅ Pickup coordination with time/location sharing
- ✅ Exchange completion verification and rating system
- ✅ Credit system with secure transaction processing
- ✅ State machine properly handles all exchange states and transitions
- ✅ Notification system keeps all parties informed throughout process
- ✅ Rating system builds user reputation and trust
- ✅ Credit transaction audit trail for transparency and debugging
- ✅ Admin tools for handling disputes and credit adjustments