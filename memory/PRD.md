# Kalmori — TuneCore Clone / Digital Music Distribution Platform

## Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Core requirements include Authentication, Subscriptions, Object Storage, AI Features, Artist management, Release/Track uploads, Distribution, Beat Marketplace, Admin Page Builder, and Kalmori white-labeling.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Framer Motion + @dnd-kit
- **Backend**: FastAPI (Python) + MongoDB
- **Payments**: Stripe + PayPal | **Storage**: Emergent Object Storage
- **AI**: Emergent LLM Key (OpenAI) | **Email**: Resend API
- **Auth**: JWT + Google OAuth | **DSP**: Spotify Web API (spotipy)

## Implemented Features (All Tested)
1-18. Core features (Auth, Subscriptions, Releases, Distribution, Analytics, AI, Beats, Contracts, Messaging, Royalty Splits, Payouts, Artist Profiles, etc.)
19. Admin Page Builder V1 — Drag-and-drop, 12 block types
20. Page Builder V2 — Custom CSS, Image uploads, Block duplication, Multi-page
21. Page Builder Auto-Seeding — Landing (14), About (5), Pricing (4) blocks
22. Reset to Default button
23. Template Library — 10 pre-built feature templates
24. Spotify DSP OAuth Integration — Real artist data
25. Admin User Cleanup
26. Updated Subscription Gating (spotify_data, beat_marketplace, messaging, royalty_splits)
27. **Clickable Notifications** — All 23+ notification types navigate to relevant page
28. **Feature Announcements** — Admin creates announcements, all users notified with plan-gated access badges
29. **What's New page** — /features shows Available (green ACTIVE) vs Locked (gold Upgrade) based on user plan
30. **Reply-To Email** — All emails reply to submitkalmori@gmail.com
31. **Cookie Consent** — Banner + backend DB logging
32. **Landing Page Hero Text** — "The Ai Powered Music Distribution Service" with animations
33. **Analytics Cleanup** — Removed ALL simulated/fake data. Endpoints return real DB data only (zeros when empty)
34. **CSV Import Admin-Only** — Only admins can import streaming data via CSV. Button hidden for non-admin users
35. **Removed Fake Percentages** — Stats cards no longer show hardcoded change indicators

## Subscription Tiers
| Feature | Free | Rise | Pro |
|---------|------|------|-----|
| Spotify Data | Locked | Locked | Unlocked |
| Beat Marketplace | Locked | Unlocked | Unlocked |
| In-App Messaging | Locked | Unlocked | Unlocked |
| Royalty Splits | Locked | Locked | Unlocked |
| AI Strategy | Locked | Locked | Unlocked |
| Fan Analytics | Locked | Unlocked | Unlocked |

## DB Collections
users, releases, tracks, stream_events, artist_profiles, beats, contracts, conversations, messages, typing_status, royalty_splits, split_earnings, wallets, withdrawals, payout_settings, goals, notifications, notification_preferences, presave_campaigns, collaboration_posts, collab_invites, saved_strategies, digest_log, page_layouts, spotify_connections, feature_announcements, cookie_consents, imported_royalties

## Remaining Tasks
- P0: Deploy to kalmori.org (Save to Github)
- P0: Add custom domain in Resend for email delivery
- P1: Apple Music Analytics API integration (pending user credentials)
- P2: Admin UI form for creating feature announcements (currently API-only)
- P2: Further server.py refactoring into /routes/ modules
- P3: YouTube Music / other DSP integrations
