# Story 002.04: Single Bot Instance Enforcement

**Epic:** EPIC-002 - Community Group Management System
**Priority:** High
**Story Points:** 3
**Sprint:** TBD

## User Story
**As a** Telegram group  
**I want** only one food-sharing bot instance per group  
**So that** there's consistent group management and no conflicts  

## Acceptance Criteria
- [ ] Check existing bot instances before creation
- [ ] Redirect subsequent /start commands to existing instance
- [ ] Show existing admin and creation date to subsequent users
- [ ] Prevent bot fragmentation and confusion
- [ ] Clear error messages for duplicate setup attempts
- [ ] Admin contact information provided to non-admin users
- [ ] Instance token uniquely identifies each group setup

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] UX/UI reviewed and approved
- [ ] Accessibility requirements met
- [ ] Security review completed (if applicable)

## Technical Notes
- Enforcement Logic:
  1. Check `group_bot_instances` table for existing instance
  2. If exists: show existing admin info, deny new instance
  3. If not exists: proceed with new instance creation
- `telegram_group_id` as primary key ensures uniqueness
- Instance token prevents unauthorized access
- Heartbeat mechanism for instance health monitoring

## Dependencies
- Database constraints for single instance enforcement
- Bot instance management system
- Admin contact information display
- Error handling for duplicate attempts

## Risks & Mitigation
- **Risk**: Race conditions in instance creation
- **Mitigation**: Database constraints and atomic operations
- **Risk**: Orphaned instances from inactive admins
- **Mitigation**: Heartbeat monitoring and admin transfer procedures