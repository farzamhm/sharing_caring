# Story 002.02: Member Disclaimer System

**Epic:** EPIC-002 - Community Group Management System
**Priority:** Critical
**Story Points:** 6
**Sprint:** TBD

## User Story
**As a** new group member  
**I want to** receive and accept the food sharing disclaimer  
**So that** I can access bot features while understanding the risks  

## Acceptance Criteria
- [ ] Bot auto-detects new group members
- [ ] Clear disclaimer message presented immediately
- [ ] Users must type 'ACCEPT' or 'DECLINE' to proceed
- [ ] Accepted users gain full bot access
- [ ] Declined users are blocked from bot features
- [ ] Disclaimer version tracking for legal updates
- [ ] Admin notification of disclaimer status changes

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] UX/UI reviewed and approved
- [ ] Accessibility requirements met
- [ ] Security review completed (if applicable)

## Technical Notes
- Disclaimer flow implementation:
  ```
  User joins group → Bot detects → Shows disclaimer
                                       ↓
                            ACCEPT → User enabled
                            DECLINE → User blocked
  ```
- `group_member_status` table tracks disclaimer acceptance
- Disclaimer versioning for legal compliance
- Automatic member detection via Telegram events
- Bot access controlled by `bot_access_enabled` flag

## Dependencies
- Legal team review of disclaimer content
- Telegram webhook integration for member events
- Database schema for member status tracking
- Bot access control system

## Risks & Mitigation
- **Risk**: Legal liability from unclear disclaimer
- **Mitigation**: Legal team review and regular updates
- **Risk**: Users bypassing disclaimer
- **Mitigation**: Strict access control and audit logging