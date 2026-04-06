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
1-38. Previous features (Auth, Subscriptions, Releases, Distribution, Analytics, AI, Beats, Contracts, Messaging, Royalty Splits, Payouts, Artist Profiles, Page Builder, Spotify, Cookie Consent, Feature Announcements, Analytics Cleanup, CSV Admin-Only Import, etc.)

### Latest Session (Apr 6, 2026)
39. **Role Selection (Artist/Producer/Label)** — Registration flow now includes 3 distinct account types with separate colors/icons. Backend accepts artist, producer, label roles.
40. **Admin Signup Notifications (ALL Admins)** — Fixed: send_admin_signup_notification now notifies ALL admin accounts (not just the first one). Both email + in-app notification sent.
41. **Notification Read State Fix** — Click handler now awaits markRead API call before navigating. Prevents race condition where notification reappears as unread.
42. **Admin Notification Bank** — Full-page admin notification history at /admin/notifications. Features: search, type filter (new_signup, feature_announcement, etc.), read/unread filter, pagination, mark-as-read, delete.
43. **Admin Feature Announcements UI** — CRUD page at /admin/feature-announcements for managing feature announcements with plan gating.
44. **Global Axios Token Refresh** — Auto-refreshes access token on 401 responses.
45. **Spotify Error Handling** — Shows error state instead of redirecting to login.

## Account Types
| Role | Description |
|------|-------------|
| Artist | Distribute music, track analytics, grow fanbase |
| Producer | Sell beats, manage instrumentals, earn from licensing |
| Label | Manage artists, distribute catalogs, track royalties |

## DB Collections
users, releases, tracks, stream_events, artist_profiles, beats, contracts, conversations, messages, typing_status, royalty_splits, split_earnings, wallets, withdrawals, payout_settings, goals, notifications, notification_preferences, presave_campaigns, collaboration_posts, collab_invites, saved_strategies, digest_log, page_layouts, spotify_connections, feature_announcements, cookie_consents, imported_royalties, email_verifications

## Remaining Tasks
- P0: Deploy to kalmori.org (Save to Github)
- P1: Apple Music Analytics API integration (pending user credentials)
- P2: Server.py refactoring into /routes/ modules
- P3: YouTube Music / other DSP integrations
