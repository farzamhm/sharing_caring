# Wireframes - Neighborhood Sharing Platform

**Version:** 1.0  
**Date:** January 2024  
**Purpose:** User validation and interface design  

---

## Overview

This document provides comprehensive wireframes for the Neighborhood Sharing Platform's user interfaces. These wireframes are designed for user testing, prototype creation, and validation of the user experience across different platforms and scenarios.

---

## 1. Telegram Bot Interface Wireframes

### 1.1 Initial Bot Discovery & Start

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 NeighborBot                    │
│  @neighborshare_bot                 │
│  ○ last seen recently               │
│                                     │
│  Welcome to Neighborhood Sharing!   │
│  🏠✨                               │
│                                     │
│  I help neighbors share homemade    │
│  food and build community. Think    │
│  of me as your friendly building    │
│  coordinator who never sleeps!      │
│                                     │
│  Here's how it works:               │
│  • Share extra food with neighbors  │
│  • Discover amazing homemade meals  │
│  • Build trust through ratings      │
│  • Earn credits for sharing         │
│                                     │
│  Ready to join your neighborhood    │
│  community?                         │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🚀 Get      │ │ ❓ Learn    │   │
│  │ Started     │ │ More        │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────┐                   │
│  │ 📱 How It   │                   │
│  │ Works       │                   │
│  └─────────────┘                   │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 1.2 Registration Flow - Phone Verification

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Awesome! Let's get you set up,  │
│     Sarah!                          │
│                                     │
│  To keep our community safe and     │
│  local, I need to verify you're     │
│  really a neighbor. Can you share   │
│  your phone number for SMS          │
│  verification?                      │
│                                     │
│  Don't worry - your number stays    │
│  private and is only used for       │
│  verification and important safety  │
│  notifications.                     │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📱 Share Phone Number          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔒 Privacy Info                │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❌ Maybe Later                 │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 1.3 SMS Verification Code Entry

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Perfect! I just sent a          │
│     verification code to            │
│     +123***7890                     │
│                                     │
│  Please enter the 6-digit code      │
│  (it might take up to 2 minutes     │
│  to arrive):                        │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ [    6-digit code entry    ]    │ │
│  │                                 │ │
│  │ Example: 847392                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔄 Resend Code                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❓ Code Not Working?           │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 1.4 Location Verification

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Great! Your phone is verified ✅│
│                                     │
│  Now let's make sure you're really  │
│  in the neighborhood. Can you share │
│  your current location so I can     │
│  verify you're in or near our       │
│  building?                          │
│                                     │
│  This helps ensure only real        │
│  neighbors can access our food      │
│  sharing community.                 │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📍 Share Location              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🏠 Enter Address Manually      │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❓ Why Location?               │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 1.5 Profile Setup - Dietary Preferences

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Perfect! You're verified as     │
│     being at Oak Street Apartments! │
│     🏢✅                           │
│                                     │
│  Do you have any dietary            │
│  restrictions I should know about?  │
│  This helps me show you relevant    │
│  food options.                      │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🌱 Vegetarian│ │ 🥛 Dairy-  │   │
│  │             │ │ Free        │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🌾 Gluten-  │ │ 🥜 Nut      │   │
│  │ Free        │ │ Allergy     │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ ✅ No       │ │ ➕ Other    │   │
│  │ Restrictions│ │             │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 1.6 Main Menu - Registration Complete

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Welcome to the neighborhood,    │
│     Sarah M! 🎉                    │
│                                     │
│  You're all set up! Here's what     │
│  you can do:                        │
│                                     │
│  🍽️ /share - Share food with       │
│     neighbors                       │
│  🔍 /browse - See what's available  │
│  💰 /credits - Check your balance   │
│     (you start with 2 free credits!)│
│  ❓ /help - Get help anytime        │
│                                     │
│  Want a quick tour of how sharing   │
│  works?                             │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📚 Yes, show me!               │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🚀 I'll figure it out          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ Start browsing food         │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 2. Food Sharing Flow Wireframes

### 2.1 Share Command - Food Name Entry

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 /share                          │
│                                     │
│  🤖 Awesome! Let's share some food  │
│     with the neighbors! 🍽️          │
│                                     │
│  What delicious food are you        │
│  sharing today?                     │
│                                     │
│  Examples:                          │
│  • "Thai green curry"               │
│  • "Homemade banana bread"          │
│  • "Leftover lasagna"              │
│  • "Fresh garden salad"            │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Enter food name here...         │ │
│  └─────────────────────────────────┘ │
│                                     │
│  💡 Tip: Be specific so neighbors   │
│     know what to expect!            │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 2.2 Portions Entry

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 Thai green curry                │
│                                     │
│  🤖 Mmm, Thai green curry sounds    │
│     amazing! 🌶️🥥                  │
│                                     │
│  How many portions do you have      │
│  available? (1-10)                  │
│                                     │
│  Think about:                       │
│  • How many people could this feed? │
│  • Normal serving sizes             │
│  • Keep some for yourself!          │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │
│  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │   │
│  └───┘ └───┘ └───┘ └───┘ └───┘   │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌─────┐ │
│  │ 6 │ │ 7 │ │ 8 │ │ 9 │ │ 10+ │ │
│  └───┘ └───┘ └───┘ └───┘ └─────┘ │
│                                     │
│  Or type a number...                │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 2.3 Photo Upload Interface

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 4                               │
│                                     │
│  🤖 Perfect - 4 portions of Thai    │
│     green curry!                    │
│                                     │
│  A photo really helps neighbors     │
│  see how delicious it looks. Can    │
│  you snap a quick pic?              │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📸 Take Photo                  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🖼️ Choose from Gallery         │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏭️ Skip Photo                  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❓ Photo Tips                  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  💡 Photos get 3x more requests!    │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 2.4 Pickup Time Entry

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  📸 [Photo uploaded successfully] ✅ │
│                                     │
│  🤖 That looks absolutely           │
│     delicious! 🤤 Great photo!      │
│                                     │
│  When can neighbors pick this up?   │
│  For example:                       │
│  • "6-7pm tonight"                  │
│  • "Available now for next 2 hours"│
│  • "5:30-6:30pm today"             │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Enter pickup time...            │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Quick options:                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 📍 Now for  │ │ 🕕 5-6pm    │   │
│  │ 2 hours     │ │ today       │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🕕 6-7pm    │ │ 🕖 7-8pm    │   │
│  │ today       │ │ today       │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 2.5 Allergen Selection

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 6-7pm tonight                   │
│                                     │
│  🤖 Perfect timing! Does your Thai  │
│     green curry contain any of      │
│     these common allergens?         │
│                                     │
│  Select all that apply:             │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🥛 Dairy    │ │ 🥜 Nuts/    │   │
│  │             │ │ Peanuts     │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🌾 Gluten   │ │ 🥚 Eggs     │   │
│  │             │ │             │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ 🦐 Shellfish│ │ 🌶️ Very    │   │
│  │             │ │ Spicy       │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ✅ None of these               │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 2.6 Post Preview & Confirmation

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Got it! Here's your food post   │
│     preview:                        │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌶️ Thai Green Curry (4 portions)│ │
│  │ 📸 [Delicious photo attached]   │ │
│  │ ⏰ Pickup: 6-7pm tonight        │ │
│  │ 📍 From: Sarah M. (Apt 4B)      │ │
│  │ ⚠️ Contains: Dairy, Very Spicy  │ │
│  │ ✨ Posted: Just now             │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Look good?                         │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ✅ Post It!                    │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ✏️ Edit Something              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❌ Cancel                      │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 3. Food Browsing Flow Wireframes

### 3.1 Browse Command - Available Food List

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 /browse                         │
│                                     │
│  🤖 Here's what neighbors are       │
│     sharing right now! 🍽️          │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌶️ Thai Green Curry (4 portions)│ │
│  │ 👤 From: Sarah M. (Apt 4B)      │ │
│  │ ⏰ Pickup: 6-7pm tonight        │ │
│  │ 📸 [Photo]                     │ │
│  │ ⚠️ Contains: Dairy, Very Spicy  │ │
│  │ ⭐ Sarah has 4.9 stars (8 ex.)  │ │
│  │                                 │ │
│  │ [🙋 Request] [ℹ️ Details] [👤 Profile] │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🥗 Garden Salad (2 portions)    │ │
│  │ 👤 From: Emma J. (Apt 5C)       │ │
│  │ ⏰ Pickup: Available now-8pm    │ │
│  │ 📸 [Photo]                     │ │
│  │ ✅ Vegetarian, no allergens     │ │
│  │ ⭐ Emma has 4.7 stars (15 ex.)  │ │
│  │                                 │ │
│  │ [🙋 Request] [ℹ️ Details] [👤 Profile] │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [🔄 Refresh] [📊 Activity] [🍽️ Share]  │
└─────────────────────────────────────┘
```

### 3.2 Food Item Details View

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 🌶️ Thai Green Curry Details     │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📸 [Large food photo]           │ │
│  │                                 │ │
│  │ 🌶️ Thai Green Curry             │ │
│  │ 📊 4 portions available          │ │
│  │ ⏰ Pickup: 6-7pm tonight         │ │
│  │ 📍 From: Sarah M. (Apt 4B)       │ │
│  │ ⚠️ Contains: Dairy, Very Spicy   │ │
│  │                                 │ │
│  │ 💬 Sarah's note:                │ │
│  │ "Made with fresh coconut milk   │ │
│  │ and homegrown Thai basil! 🌿"   │ │
│  │                                 │ │
│  │ ⭐ Sarah's ratings:              │ │
│  │ 4.9 stars from 8 exchanges      │ │
│  │ "Amazing cook!" "Always fresh!" │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🙋 Request This (1 credit)      │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 Message Sarah First          │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [⬅️ Back] [👤 Sarah's Profile] [❌ Cancel] │
└─────────────────────────────────────┘
```

### 3.3 Request Confirmation

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Great choice! 🌶️ Sarah's Thai   │
│     Green Curry looks amazing!      │
│                                     │
│  Request Details:                   │
│  ┌─────────────────────────────────┐ │
│  │ • 4 portions Thai Green Curry   │ │
│  │ • From Sarah M. (Apt 4B)        │ │
│  │ • Pickup: 6-7pm tonight         │ │
│  │ • Contains: Dairy, Very Spicy   │ │
│  │ • Cost: 1 credit (you have 2)   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Confirm your request?              │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ✅ Yes, Request It!             │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 Message Sarah First          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 👤 Sarah's Reviews              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❌ Changed My Mind              │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 3.4 Request Sent Confirmation

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Request sent! 🎉                │
│                                     │
│  Sarah has been notified that you'd │
│  like her Thai Green Curry. You'll  │
│  hear back soon!                    │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Your Request:                   │ │
│  │ • Thai Green Curry (4 portions) │ │
│  │ • From Sarah M. (Apt 4B)        │ │
│  │ • Pickup: 6-7pm tonight         │ │
│  │ • Status: ⏳ Pending response   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Most people respond within 30      │
│  minutes. I'll notify you as soon   │
│  as Sarah replies!                  │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 Message Sarah               │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔍 Browse Other Food           │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📋 My Requests                 │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 4. Exchange Coordination Wireframes

### 4.1 Request Accepted Notification

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Fantastic news! 🎉             │
│                                     │
│  Sarah accepted your request!       │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Pickup Details:                 │ │
│  │ • What: Thai Green Curry (4)    │ │
│  │ • When: 6-7pm tonight           │ │
│  │ • Where: Sarah's apartment (4B) │ │
│  │ • Cost: 1 credit (deducted      │ │
│  │   when pickup confirmed)        │ │
│  └─────────────────────────────────┘ │
│                                     │
│  💬 Sarah says:                     │
│  "Hi Mike! The curry is ready and   │
│  staying warm. Just knock on 4B     │
│  anytime between 6-7pm. Looking     │
│  forward to meeting you!"           │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 Reply to Sarah              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📍 Get Directions              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏰ Set Reminder                │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 4.2 Direct Messaging Interface

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Send a message to Sarah:        │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ [Text input area]               │ │
│  │                                 │ │
│  │ Hi Sarah! Thanks so much - I'll │ │
│  │ be there around 6:30pm. Should  │ │
│  │ I bring a container or do you    │ │
│  │ have one?                       │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Quick replies:                     │
│  ┌─────────────────────────────────┐ │
│  │ 👍 "Thanks! See you at 6:30pm" │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📦 "Should I bring a container?"│ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏰ "Running 5 minutes late"     │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📋 Send Message                │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [⬅️ Back] [📋 Exchange Details] [❌ Cancel] │
└─────────────────────────────────────┘
```

### 4.3 Pickup Reminder

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 🔔 Pickup Reminder!             │
│                                     │
│  Time to get that delicious Thai    │
│  Green Curry from Sarah! 🌶️        │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📍 Sarah M. - Apartment 4B      │ │
│  │ ⏰ Available until 7pm           │ │
│  │ 🌶️ Thai Green Curry (4 portions)│ │
│  │                                 │ │
│  │ 💬 Sarah's message:             │ │
│  │ "No need to bring anything!     │ │
│  │ I have a nice container you     │ │
│  │ can keep. See you soon! 😊"     │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Have a great exchange! I'll check  │
│  in afterward to see how it went.   │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 👍 On my way!                  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏰ Running 5 min late           │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❌ Can't make it                │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 5. Rating & Feedback Wireframes

### 5.1 Post-Exchange Check-in

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Hope you enjoyed meeting Sarah  │
│     and getting that curry! 🌶️     │
│                                     │
│  Did the pickup go smoothly?        │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ✅ Yes, perfect!                │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 👍 Good overall                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 😐 It was okay                  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❌ Had some issues              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏰ It's happening now           │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📞 Sarah didn't show            │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 5.2 Rating Interface - Food Quality

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Wonderful! 🌟                  │
│                                     │
│  1 credit has been deducted from    │
│  your balance. New balance: 1 credit│
│                                     │
│  How would you rate your experience │
│  with Sarah?                        │
│                                     │
│  Food Quality:                      │
│  Rate the taste, freshness, and     │
│  description accuracy               │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │
│  │⭐ │ │⭐⭐│ │⭐⭐⭐│ │⭐⭐⭐⭐│ │⭐⭐⭐⭐⭐│ │
│  │   │ │   │ │   │ │   │ │   │   │
│  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5   │ │
│  └───┘ └───┘ └───┘ └───┘ └───┘   │
│                                     │
│  ┌─────────────┐                   │
│  │ Poor        │ Excellent         │
│  └─────────────┘                   │
│                                     │
│  💡 Tips:                           │
│  • 5⭐ = Restaurant quality         │
│  • 4⭐ = Delicious, would get again │
│  • 3⭐ = Good, met expectations     │
│  • 2⭐ = Okay but had issues        │
│  • 1⭐ = Poor quality/safety concern│
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 5.3 Rating Interface - Interaction

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Thanks! ⭐⭐⭐⭐⭐ for food      │
│     quality!                        │
│                                     │
│  Interaction & Communication:       │
│  Rate Sarah's communication,        │
│  reliability, and friendliness      │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │
│  │⭐ │ │⭐⭐│ │⭐⭐⭐│ │⭐⭐⭐⭐│ │⭐⭐⭐⭐⭐│ │
│  │   │ │   │ │   │ │   │ │   │   │
│  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5   │ │
│  └───┘ └───┘ └───┘ └───┘ └───┘   │
│                                     │
│  ┌─────────────┐                   │
│  │ Poor        │ Excellent         │
│  └─────────────┘                   │
│                                     │
│  💡 Consider:                       │
│  • Was pickup timing as planned?    │
│  • How was communication?           │
│  • Was Sarah friendly/welcoming?    │
│  • Would you exchange again?        │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 5.4 Comment Entry

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 Amazing! ⭐⭐⭐⭐⭐ across       │
│     the board!                      │
│                                     │
│  Any comment about your experience  │
│  with Sarah? (This helps other      │
│  neighbors)                         │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ [Comment text area]             │ │
│  │                                 │ │
│  │ The curry was incredible -      │ │
│  │ restaurant quality! Sarah was   │ │
│  │ so welcoming and the portions   │ │
│  │ were huge. Definitely           │ │
│  │ requesting from her again!      │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Quick options:                     │
│  ┌─────────────────────────────────┐ │
│  │ 👍 "Great food and friendly!"   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ "Delicious, would request    │ │
│  │    again!"                      │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏭️ Skip comment                │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [✅ Submit Rating] [⬅️ Back] [❌ Cancel] │
└─────────────────────────────────────┘
```

---

## 6. Credits & Profile Wireframes

### 6.1 Credits Dashboard

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 /credits                        │
│                                     │
│  🤖 💰 Your Credit Balance          │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Current Balance: 5 credits       │ │
│  │                                 │ │
│  │ 💡 1 credit = 1 meal            │ │
│  │ • Earn credits by sharing food  │ │
│  │ • Spend credits to receive food │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Recent Activity:                   │
│  ┌─────────────────────────────────┐ │
│  │ ✅ +1 credit - Shared Chicken   │ │
│  │    Curry with Mike L.           │ │
│  │ ❌ -1 credit - Received Garden  │ │
│  │    Salad from Sarah M.          │ │
│  │ 🎁 +2 credits - Welcome bonus   │ │
│  │ ✅ +1 credit - Shared Pasta     │ │
│  │    Bake with Jane K.            │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📊 Full History                │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ❓ How Credits Work             │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 6.2 User Profile View

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 👤 Your Profile                 │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Sarah M. (Apt 4B)               │ │
│  │ ⭐ 4.9 stars from 15 exchanges  │ │
│  │ 🏠 Oak Street Apartments        │ │
│  │ 📅 Member since Jan 2024        │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Your Stats:                        │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ 12 meals shared              │ │
│  │ 🙋 8 meals received             │ │
│  │ 💰 5 credit balance             │ │
│  │ 🌟 4.9 average rating           │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Dietary Preferences:               │
│  ┌─────────────────────────────────┐ │
│  │ 🌱 Vegetarian                   │ │
│  │ ❌ No other restrictions        │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ✏️ Edit Profile                │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📊 Detailed Stats              │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 7. Community Features Wireframes

### 7.1 Daily Digest

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 🌅 Good evening, Oak Street     │
│     Apartments!                     │
│                                     │
│  Here's your daily community        │
│  update for Tuesday, January 16th:  │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📊 Today's Sharing Activity:    │ │
│  │ • 8 successful food exchanges   │ │
│  │ • 5 different neighbors shared  │ │
│  │ • 12 neighbors received food    │ │
│  │ • 94% exchange completion rate  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🌟 Today's Highlights:          │ │
│  │ • Maria's lasagna got 5⭐ from  │ │
│  │   3 neighbors!                  │ │
│  │ • David helped Mrs. Chen with   │ │
│  │   fresh bread (so sweet! 🥖)    │ │
│  │ • New neighbor Tom joined and   │ │
│  │   shared pizza 🍕              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ Most Popular Today:          │ │
│  │ 1. Italian dishes (3 exchanges) │ │
│  │ 2. Homemade bread (2 exchanges) │ │
│  │ 3. Soups & stews (2 exchanges)  │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [🔍 Browse] [🍽️ Share] [📊 Stats] [🔕 Manage] │
└─────────────────────────────────────┘
```

### 7.2 Help & Support Menu

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 /help                           │
│                                     │
│  🤖 ❓ Help & Support               │
│                                     │
│  How can I help you today?          │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ How to share food            │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔍 How to find & request food   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💰 How credits work             │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⭐ Rating system explained      │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🛡️ Safety & community rules    │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🚨 Report a problem             │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 Contact support              │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 8. Error States & Edge Cases

### 8.1 No Food Available State

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 /browse                         │
│                                     │
│  🤖 🔍 Looking for available food... │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │     🍽️                         │ │
│  │                                 │ │
│  │ No food currently available     │ │
│  │                                 │ │
│  │ Be the first to share something │ │
│  │ delicious with your neighbors!  │ │
│  │                                 │ │
│  │ 💡 Food posts happen throughout │ │
│  │ the day - check back soon!      │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ Share Food Instead          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔔 Notify When Food Posted     │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔄 Refresh                     │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📊 See Community Activity      │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 8.2 Request Declined State

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  🤖 I heard back from David about   │
│     the sourdough bread.            │
│                                     │
│  Unfortunately, David declined      │
│  your request.                      │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 David's message:             │ │
│  │                                 │ │
│  │ "Hi Lisa! Sorry, I just         │ │
│  │ promised the bread to my        │ │
│  │ elderly neighbor Mrs. Chen      │ │
│  │ who's been feeling under the    │ │
│  │ weather. Hope you understand!   │ │
│  │ I'll have more bread this       │ │
│  │ weekend."                       │ │
│  └─────────────────────────────────┘ │
│                                     │
│  No worries - this happens          │
│  sometimes! Your credit hasn't      │
│  been charged.                      │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 👍 Totally understand          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔍 Browse other options        │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 💬 Reply to David              │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

### 8.3 Technical Error State

```
┌─────────────────────────────────────┐
│ Telegram - NeighborBot Chat         │
├─────────────────────────────────────┤
│                                     │
│  👤 /share                          │
│                                     │
│  🤖 ⚠️ Sorry! I'm experiencing some │
│     technical difficulties right    │
│     now. Let me try to help...      │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔧 What's happening:            │ │
│  │                                 │ │
│  │ I'm having trouble connecting   │ │
│  │ to my database right now.       │ │
│  │                                 │ │
│  │ This means I can't:             │ │
│  │ • Save new food posts           │ │
│  │ • Load your profile             │ │
│  │ • Process requests              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔄 Try again                   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔔 Notify me when fixed        │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⏰ Try later                   │ │
│  └─────────────────────────────────┘ │
│                                     │
│  Usually these issues resolve       │
│  within 30 minutes. Sorry for the   │
│  inconvenience! 😔                  │
│                                     │
├─────────────────────────────────────┤
│ Type a message...            [ ✈️ ] │
└─────────────────────────────────────┘
```

---

## 9. Progressive Web App Wireframes

### 9.1 PWA Home Screen

```
┌─────────────────────────────────────┐
│ NeighborShare PWA                   │
│ ☰ ≡                        🔔 👤   │ 
├─────────────────────────────────────┤
│                                     │
│  🏠 Oak Street Apartments           │
│  Welcome back, Sarah M!             │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ Quick Actions                   │ │
│  │                                 │ │
│  │ ┌─────────┐  ┌─────────┐       │ │
│  │ │  🍽️     │  │  🔍     │       │ │
│  │ │ Share   │  │ Browse  │       │ │
│  │ │ Food    │  │ Food    │       │ │
│  │ └─────────┘  └─────────┘       │ │
│  │                                 │ │
│  │ ┌─────────┐  ┌─────────┐       │ │
│  │ │  💰     │  │  📊     │       │ │
│  │ │Credits  │  │ Activity│       │ │
│  │ │ (5)     │  │         │       │ │
│  │ └─────────┘  └─────────┘       │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📅 Today's Activity             │ │
│  │                                 │ │
│  │ • 3 new food posts              │ │
│  │ • 1 pending request             │ │
│  │ • 8 total exchanges today       │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🍽️ Recently Available          │ │
│  │                                 │ │
│  │ [Food item previews...]         │ │
│  └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [🏠] [🔍] [🍽️] [💬] [👤]            │
└─────────────────────────────────────┘
```

### 9.2 PWA Food Browse Grid

```
┌─────────────────────────────────────┐
│ NeighborShare - Browse Food         │
│ ←                           🔔 🔍   │
├─────────────────────────────────────┤
│                                     │
│  Available Food (8 items)           │
│                                     │
│  [Filters: All ▼] [Sort: Time ▼]   │
│                                     │
│  ┌─────────┬─────────┬─────────┐    │
│  │ [📸]    │ [📸]    │ [📸]    │    │
│  │ Thai    │ Garden  │ Pizza   │    │
│  │ Curry   │ Salad   │ Slices  │    │
│  │ ⭐4.9   │ ⭐4.7   │ ⭐4.2   │    │
│  │ 4 port. │ 2 port. │ 3 port. │    │
│  │ Sarah M.│ Emma J. │ Tom B.  │    │
│  │ 6-7pm   │ Now-8pm │ Now-1hr │    │
│  └─────────┴─────────┴─────────┘    │
│                                     │
│  ┌─────────┬─────────┬─────────┐    │
│  │ [📸]    │ [📸]    │ [📸]    │    │
│  │ Bread   │ Pasta   │ Soup    │    │
│  │ Loaf    │ Bake    │ Bowls   │    │
│  │ ⭐4.8   │ ⭐4.6   │ ⭐5.0   │    │
│  │ 1 loaf  │ 6 port. │ 4 port. │    │
│  │ David R.│ Maria S.│ Priya P.│    │
│  │ 4-6pm   │ 7-8pm   │ 5-7pm   │    │
│  └─────────┴─────────┴─────────┘    │
│                                     │
│  ┌─────────┬─────────┐              │
│  │ [📸]    │ [📸]    │              │
│  │ Apple   │ Cookies │              │
│  │ Pie     │ Batch   │              │
│  │ ⭐4.6   │ ⭐4.9   │              │
│  │ 8 slice │ 2 dozen │              │
│  │ Jen L.  │ Carlos R│              │
│  │ Now-10pm│ 6-8pm   │              │
│  └─────────┴─────────┘              │
│                                     │
├─────────────────────────────────────┤
│ [🏠] [🔍] [🍽️] [💬] [👤]            │
└─────────────────────────────────────┘
```

---

## 10. Mobile Responsiveness Considerations

### Key Design Principles:

1. **Touch-Friendly Targets**
   - Minimum 44px button height
   - Adequate spacing between interactive elements
   - Clear visual feedback for taps

2. **Readable Text**
   - Minimum 16px font size for body text
   - High contrast ratios
   - Scalable typography

3. **Efficient Navigation**
   - Bottom navigation for primary actions
   - Swipe gestures for secondary actions
   - Back button consistency

4. **Fast Loading**
   - Progressive image loading
   - Skeleton screens during loading
   - Offline capability for critical functions

5. **Platform Conventions**
   - iOS: Tab bar, navigation controller patterns
   - Android: Material Design components
   - Web: Responsive grid layouts

---

## 11. Accessibility Features

### Visual Accessibility:
- High contrast mode support
- Large text size options
- Screen reader optimization
- Alt text for all images

### Motor Accessibility:
- Voice command integration
- Switch control support
- Adjustable touch targets
- Simplified navigation options

### Cognitive Accessibility:
- Clear, simple language
- Consistent navigation patterns
- Progress indicators
- Error prevention and recovery

---

These wireframes provide a comprehensive foundation for user testing, prototype development, and validation of the user experience across the Neighborhood Sharing Platform. They demonstrate the complete user journey from discovery through successful food sharing and community building.