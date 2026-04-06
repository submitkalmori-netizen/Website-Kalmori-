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
1-45. All previous features (Auth, Subscriptions, Releases, Distribution, Analytics, AI, Beats, Contracts, Messaging, Royalty Splits, Payouts, Artist Profiles, Page Builder, Spotify, Cookie Consent, Feature Announcements UI, Notification Bank, Analytics Cleanup, CSV Admin-Only Import, Role Selection, Global Token Refresh, etc.)

### Latest Session (Apr 6, 2026)
46. **Individual User Delete** — Admin can delete any non-admin user from /admin/users. Deletes ALL related data across 18+ collections (releases, tracks, beats, messages, analytics, wallets, etc). Admin accounts protected (returns 403). Confirmation modal with warning.
47. **ALL Admin Notifications Sync** — Fixed 3 notification sources (new_signup, new_submission, schedule_reminder) to use find() instead of find_one(). Both admin@kalmori.com AND submitkalmori@gmail.com now receive all notifications.

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
