# Story 001.02: Flexible Verification Levels

**Epic:** EPIC-001 - Dual-Mode Platform Foundation
**Priority:** Critical
**Story Points:** 8
**Sprint:** TBD

## User Story
**As a** user selecting my community type  
**I want** appropriate verification based on my chosen mode  
**So that** I have the right balance of security and convenience  

## Acceptance Criteria
- [ ] Neighborhood Mode requires SMS verification + building address + apartment number
- [ ] Community Mode requires Telegram group membership + optional location sharing
- [ ] Verification level stored in user profile (`verification_level` field)
- [ ] Different verification flows based on mode selection
- [ ] Users can upgrade verification level if switching modes
- [ ] Verification status clearly displayed in user profile
- [ ] Failed verification attempts are logged and handled gracefully

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] UX/UI reviewed and approved
- [ ] Accessibility requirements met
- [ ] Security review completed (if applicable)

## Technical Notes
- Verification Matrix implementation:
  - **Neighborhood Mode**: SMS + location + apartment verification
  - **Community Mode**: Telegram group membership + optional location
- Events published to `verification.events` Valkey stream
- Database `verification_level` field tracks completion status
- Secure storage of verification data with appropriate retention policies

## Dependencies
- SMS verification service integration
- Location verification system
- Telegram group membership validation
- Database schema updates

## Risks & Mitigation
- **Risk**: SMS verification costs and reliability
- **Mitigation**: Implement fallback verification methods and cost monitoring
- **Risk**: Location verification accuracy
- **Mitigation**: Multiple verification approaches and manual review process