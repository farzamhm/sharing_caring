# Tracking Spreadsheet Setup Guide

## Overview

You'll need 4 main sheets in your Google Sheets or Excel workbook:
1. **Exchange Log** - Track every food share
2. **Participants** - Manage user information
3. **Daily Metrics** - Track engagement patterns
4. **Weekly Summary** - Compile results for reporting

---

## Sheet 1: Exchange Log

### Columns (A-N):

| Column | Header | Example | Purpose |
|--------|--------|---------|---------|
| A | Date | 2024-01-15 | When exchange happened |
| B | Time | 6:30 PM | When food was shared |
| C | Sharer Name | Sarah M | Who provided food |
| D | Sharer Apt | 4B | Their apartment |
| E | Food Item | Chicken Curry | What was shared |
| F | Portions | 3 | How many servings |
| G | Receiver Name | Mike L | Who received food |
| H | Receiver Apt | 2A | Their apartment |
| I | Exchange Type | Pickup | Pickup/Delivery |
| J | Completed | Yes | Was exchange successful |
| K | Receiver Rating | 5 | Rating 1-5 |
| L | Receiver Comments | "Delicious!" | Brief feedback |
| M | Issues/Notes | None | Any problems |
| N | Follow-up Needed | No | Action required |

### Sample Rows:
```
Date       Time    Sharer  Apt  Food Item      Portions  Receiver  Apt  Type    Complete  Rating  Comments           Issues
1/15/24    6:30PM  Sarah M  4B  Chicken Curry      3     Mike L    2A   Pickup    Yes       5     "Amazing spices!"  None
1/15/24    7:00PM  Mike L   2A  Leftover Pizza     2     Jane K    1C   Pickup    Yes       4     "Good for kids"    None
1/16/24    12:30PM Jane K   1C  Veggie Soup        4     Tom B     3A   Pickup    No        -     -                  "No show"
```

---

## Sheet 2: Participants

### Columns (A-M):

| Column | Header | Example | Purpose |
|--------|--------|---------|---------|
| A | Name | Sarah Martinez | Full name |
| B | First Name | Sarah | For sharing |
| C | Apartment | 4B | Location |
| D | Phone | 555-0123 | Contact |
| E | Join Date | 2024-01-10 | When started |
| F | Food Restrictions | Vegetarian | Dietary needs |
| G | Total Shared | 8 | Meals given |
| H | Total Received | 6 | Meals received |
| I | Avg Rating Given | 4.5 | Rating they give |
| J | Avg Rating Received | 4.8 | Rating they get |
| K | Last Active | 2024-01-20 | Recent activity |
| L | Status | Active | Active/Inactive |
| M | Notes | "Great baker" | Special notes |

### Formulas to Add:
- **Total Shared (G):** `=COUNTIF('Exchange Log'!C:C,B2)`
- **Total Received (H):** `=COUNTIF('Exchange Log'!G:G,B2)`
- **Avg Rating Received (J):** `=AVERAGEIF('Exchange Log'!G:G,B2,'Exchange Log'!K:K)`

---

## Sheet 3: Daily Metrics

### Columns (A-K):

| Column | Header | Formula/Purpose |
|--------|--------|-----------------|
| A | Date | Manual entry |
| B | Total Exchanges | `=COUNTIF('Exchange Log'!A:A,A2)` |
| C | Unique Sharers | Count distinct sharers that day |
| D | Unique Receivers | Count distinct receivers that day |
| E | Active Users | Total unique people that day |
| F | WhatsApp Messages | Manual count |
| G | New Participants | Manual entry |
| H | Issues Reported | Manual count |
| I | Avg Rating | `=AVERAGEIF('Exchange Log'!A:A,A2,'Exchange Log'!K:K)` |
| J | Food Types | Count different meals |
| K | Notes | Daily observations |

### Sample Week:
```
Date        Total Ex  Sharers  Receivers  Active  Messages  New   Issues  Avg Rating  Notes
1/15/24         3        2         3        4       12       2      0       4.5      "Good start"
1/16/24         2        2         2        3        8       0      1       4.0      "One no-show"
1/17/24         4        3         4        5       15       1      0       4.8      "Best day yet"
```

---

## Sheet 4: Weekly Summary

### Sections:

**A. Weekly Metrics (Rows 1-15)**
| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Target |
|--------|--------|--------|--------|--------|--------|
| Total Participants | 8 | 10 | 10 | 12 | 10+ |
| Active Users | 7 | 9 | 8 | 10 | 8+ |
| Total Exchanges | 12 | 18 | 22 | 25 | 20+ |
| Exchanges per User | 1.5 | 1.8 | 2.2 | 2.1 | 2+ |
| Avg Rating | 4.2 | 4.5 | 4.6 | 4.7 | 4+ |
| Safety Incidents | 0 | 0 | 0 | 0 | 0 |
| Completion Rate | 85% | 92% | 95% | 96% | 90% |

**B. Top Performers (Rows 17-25)**
| Name | Meals Shared | Meals Received | Avg Rating | Notes |
|------|--------------|----------------|------------|-------|
| Sarah M | 8 | 6 | 4.8 | "Consistent sharer" |
| Mike L | 4 | 7 | 4.5 | "Great feedback" |

**C. Issues Tracking (Rows 27-35)**
| Date | Issue | Resolution | Status |
|------|-------|------------|--------|
| 1/16 | No-show for pickup | Messaged participant | Resolved |
| 1/18 | Food quality concern | Direct discussion | Resolved |

---

## Setup Instructions

### 1. Create Google Sheets Workbook
1. Go to sheets.google.com
2. Create new blank spreadsheet
3. Rename to "Neighborhood Sharing Pilot Tracking"
4. Add 4 sheets with names above

### 2. Set Up Each Sheet
1. Add column headers as specified
2. Format date columns as dates
3. Add formulas where indicated
4. Create data validation for ratings (1-5)

### 3. Essential Formulas

**For Exchange Log:**
- Completion rate: `=COUNTIF(J:J,"Yes")/COUNTA(J:J)*100`
- Daily exchanges: `=COUNTIF(A:A,TODAY())`

**For Participants:**
- Active this week: `=COUNTIFS('Exchange Log'!A:A,">="&TODAY()-7,'Exchange Log'!C:C,B2)+COUNTIFS('Exchange Log'!A:A,">="&TODAY()-7,'Exchange Log'!G:G,B2)`

**For Daily Metrics:**
- Running total: `=SUM(B$2:B2)`
- Week over week growth: `=(B2-B9)/B9*100`

### 4. Conditional Formatting
- Green: Ratings 4-5
- Yellow: Ratings 3-3.9
- Red: Ratings 1-2.9
- Red: Any incomplete exchanges

---

## Data Collection Process

### Daily (5 minutes):
1. Open Exchange Log sheet
2. Add any exchanges from WhatsApp group
3. Update completion status
4. Add ratings/feedback received
5. Update Daily Metrics sheet

### Weekly (15 minutes):
1. Update Weekly Summary metrics
2. Calculate week-over-week changes
3. Identify top performers
4. Review any issues or patterns
5. Prepare weekly report

---

## Key Metrics to Watch

### Success Indicators:
- **Exchange completion rate >90%**
- **Average rating >4.0**
- **Weekly exchanges increasing**
- **New participants joining**
- **Issues decreasing over time**

### Warning Signs:
- **Completion rate <80%**
- **Ratings trending down**
- **Same people always sharing/receiving**
- **Multiple complaints about same person**
- **Participation dropping off**

---

## Mobile-Friendly Data Entry

### Option 1: Google Forms Integration
Create form with fields:
- Date/Time
- Sharer name
- Food item
- Receiver name
- Rating
- Comments

Form responses auto-populate Exchange Log

### Option 2: Smartphone App
- Google Sheets mobile app
- Quick entry templates
- Voice-to-text for comments

---

## Privacy & Security

### Data Protection:
- Share sheet with read-only access for participants
- Use first names only in shared view
- Keep full contact info on separate private sheet
- Regular backup to prevent data loss

### Weekly Reports to Participants:
- Overall metrics only
- No individual performance data
- Fun highlights and achievements
- Thank you messages

---

## Analytics & Insights

### Weekly Questions to Answer:
1. Which days/times see most activity?
2. What types of food are most popular?
3. Who are the "super sharers"?
4. What causes exchanges to fail?
5. How satisfied are participants?
6. Are people building relationships?

### Charts to Create:
- Daily exchange volume
- Participant activity levels
- Food category breakdown
- Rating trends over time
- Completion rate by week

---

## Sample Dashboard View

```
WEEK 3 SNAPSHOT
📊 Total Exchanges: 22 (+4 from last week)
👥 Active Users: 8/10 (80% participation)
⭐ Average Rating: 4.6/5
✅ Completion Rate: 95%
🚨 Issues: 0

TOP SHARERS THIS WEEK:
🥇 Sarah M. (5 meals shared)
🥈 Mike L. (3 meals shared)
🥉 Jane K. (3 meals shared)

MOST POPULAR FOODS:
1. Italian dishes (6 exchanges)
2. Soups (4 exchanges)
3. Baked goods (3 exchanges)
```

---

This tracking system will give you comprehensive data to evaluate your pilot's success and identify areas for improvement. The key is consistent daily entry and weekly analysis to spot trends early.

*Setup Time: 30-45 minutes*  
*Daily Maintenance: 5 minutes*  
*Weekly Analysis: 15 minutes*