# 🤖 AI DEVELOPER: START HERE - CRITICAL BRIEFING

**Scrum Master:** Bob  
**For:** Dumb AI Development Agents  
**Status:** Ready for Implementation  
**Last Updated:** 2025-01-01  

---

## 🚨 CRITICAL: READ THIS BEFORE ANY CODING

You are about to implement a **dual-mode food sharing platform** transformation. This changes everything about how the platform works. **DO NOT START CODING** until you understand these critical points.

### **WHAT YOU'RE BUILDING:**
- Transform single-mode neighborhood platform → dual-mode platform
- Add **Neighborhood Mode** (high verification) + **Community Mode** (light verification)  
- Implement global reputation system that follows users across groups
- Build event-driven architecture using Valkey streams
- Create admin tools, partnerships, and credit integration

### **CURRENT PLATFORM:**
- Existing Telegram bot for neighborhood food sharing
- PostgreSQL database with users, buildings, food_posts, exchanges
- Basic credit system and SMS verification
- Single verification level and building-based sharing only

---

## 🎯 YOUR EXACT MISSION

### **PHASE 1: FOUNDATION (MUST COMPLETE FIRST)**
You must complete these **3 stories in exact order**:

1. **STORY-009-02-database-performance-optimization-ENHANCED.md**  
   **What:** Add dual-mode database schema + performance indexes  
   **Why Critical:** ALL other features depend on this database structure  
   **Files:** Create migration scripts, add new tables, create indexes  

2. **STORY-009-03-caching-strategy-implementation-ENHANCED.md**  
   **What:** Set up Valkey streams event-driven architecture  
   **Why Critical:** Reputation, analytics, admin features need event streams  
   **Files:** Create stream managers, event publishers, consumers  

3. **STORY-001-01-mode-selection-during-registration-ENHANCED.md**  
   **What:** Add mode selection to Telegram bot registration  
   **Why Critical:** First user-facing feature that enables dual-mode  
   **Files:** Update bot handlers, registration flow, user interface  

### **AFTER PHASE 1:** 
Follow the priority order in `/docs/product/DEVELOPMENT_QUEUE_FOR_AI.md`

---

## 🛠️ ENHANCED STORIES (DUMB AI READY)

### **Enhanced Stories with Exact Specifications:**
- ✅ `STORY-009-02-database-performance-optimization.md` (ENHANCED)
- ✅ `STORY-009-03-caching-strategy-implementation.md` (ENHANCED)  
- ✅ `STORY-001-01-mode-selection-during-registration.md` (ENHANCED)

### **Original Stories (Need Enhancement):**
- ⚠️ All other 55+ stories in `/docs/product/stories/` directory
- ⚠️ These have acceptance criteria but lack exact implementation specs
- ⚠️ Use enhanced stories as template for implementation detail level

---

## 🏗️ ARCHITECTURE REFERENCES (MUST READ)

### **CRITICAL DOCUMENTS TO READ BEFORE CODING:**
1. `/docs/product/epics/EPIC-001-Dual-Mode-Platform-Foundation.md`
   - Database schema specifications  
   - Mode comparison framework
   - Event-driven architecture requirements

2. `/docs/product/epics/EPIC-004-Global-Reputation-System.md`  
   - Reputation database tables
   - Trust level calculations
   - Stream processing for reputation events

3. `/docs/product/epics/EPIC-009-Platform-Scalability-Performance.md`
   - Valkey streams architecture
   - Performance requirements  
   - Auto-scaling specifications

4. `/valkey.conf`
   - Exact Valkey configuration for streams
   - Performance optimizations
   - Stream-specific settings

---

## 🔥 CRITICAL SUCCESS FACTORS

### **NEVER SKIP THESE:**
- [ ] Read ALL acceptance criteria in each story  
- [ ] Follow EXACT naming conventions from epic specs
- [ ] Implement ALL error handling as specified
- [ ] Run ALL tests before marking story complete
- [ ] Verify dependencies completed before starting story

### **EXACT TECHNICAL REQUIREMENTS:**
- **Database Response Time:** <200ms average for all queries
- **Stream Processing:** <100ms per event average  
- **User Interface:** <2 second response time for all interactions
- **Test Coverage:** 80%+ for all new code
- **Error Handling:** Graceful failures with user-friendly messages

### **NAMING CONVENTIONS (DO NOT DEVIATE):**
- **Database Fields:** `sharing_mode`, `verification_level`, `trust_level`
- **Stream Names:** `reputation.events`, `user.mode.transitions`, `analytics.user.behavior`
- **Mode Values:** `"neighborhood"` and `"community"` (exact strings)
- **Trust Levels:** `"developing"`, `"established"`, `"trusted"`, `"exemplary"`

---

## 🚨 FAILURE PREVENTION CHECKLIST

### **BEFORE STARTING ANY STORY:**
- [ ] All dependency stories are 100% complete (not just "mostly done")
- [ ] Database schema from previous stories is deployed and working
- [ ] You understand the exact technical specifications
- [ ] Test environment has all required dependencies

### **DURING IMPLEMENTATION:**
- [ ] Following exact code specifications from enhanced stories
- [ ] Using consistent naming across all files
- [ ] Implementing comprehensive error handling  
- [ ] Adding detailed logging for debugging

### **BEFORE MARKING COMPLETE:**
- [ ] ALL acceptance criteria demonstrably working
- [ ] Unit tests passing with required coverage
- [ ] Integration tests passing
- [ ] Performance requirements met
- [ ] No breaking changes to existing features

---

## 🎯 STORY COMPLETION TRACKING

### **PHASE 1 CRITICAL PATH:**
```
□ STORY-009-02: Database Schema + Performance (8pts) 
□ STORY-009-03: Valkey Streams Architecture (7pts)
□ STORY-001-01: Mode Selection Interface (5pts)
```
**Phase 1 Total:** 20 story points  
**Phase 1 Status:** 🔴 NOT STARTED

### **CRITICAL BLOCKER WARNING:**
🚨 **NO OTHER STORIES can be started until Phase 1 is 100% complete** 🚨

All reputation, analytics, admin, partnership, and credit features depend on the foundation created in Phase 1.

---

## 📞 HELP & ESCALATION

### **WHEN YOU'RE STUCK:**
1. **Technical Questions:** Re-read the epic documents and enhanced story specs
2. **Requirements Clarification:** Check acceptance criteria in original stories  
3. **Architecture Decisions:** Follow Winston's specifications exactly (no deviations)
4. **Process Questions:** Escalate to Bob (Scrum Master)

### **ESCALATION TRIGGERS:**
- Cannot complete story due to unclear requirements
- Performance benchmarks cannot be met with current approach
- Breaking changes required to existing platform
- Dependencies are unclear or conflicting

### **EMERGENCY CONTACTS:**
- **Bob (Scrum Master):** Story clarification and process issues
- **Sarah (Product Owner):** Requirements validation and acceptance
- **Winston (Architect):** Technical architecture questions

---

## 🏃‍♂️ READY TO START?

### **PRE-FLIGHT CHECKLIST:**
- [ ] I have read this entire document
- [ ] I understand the dual-mode platform concept  
- [ ] I have read the 3 critical epic documents
- [ ] I am ready to implement Phase 1 stories in exact order
- [ ] I will not start any story until its dependencies are complete
- [ ] I will follow the exact specifications without shortcuts

### **FIRST ACTION:**
Start with `STORY-009-02-database-performance-optimization-ENHANCED.md`

**DO NOT START ANY OTHER STORY FIRST.** The database foundation must be completed before anything else.

---

**REMEMBER: You are not just adding features - you are transforming the entire platform architecture. Precision and attention to detail are critical for success.**

🤖 **Good luck, AI developer. Follow the specs exactly and you'll build something amazing!**