# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads, Distribution to 150+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons
- **Backend**: FastAPI (server.py + core.py + /routes/)
- **Database**: MongoDB (25+ collections)
- **Storage**: Emergent Object Storage | **Payments**: Stripe + PayPal
- **Auth**: JWT + Google OAuth + reCAPTCHA v2 + Email Verification
- **AI**: OpenAI via Emergent LLM Key | **Email**: Resend (support@kalmori.org)

## All Completed Features
- Auth (JWT + Google OAuth + reCAPTCHA + Email Verification)
- Subscription tiers (Free/Rise/Pro) with Stripe, plan gating
- Promo Codes (admin CRUD, public validation, pricing page)
- Referral Program (unique codes, auto-upgrade, admin overview)
- Analytics Email Reports (weekly/monthly, preview, send to all, preferences)
- Email Domain Management (custom Resend domain: kalmori.org)
- Track Editing (full 12-field form, inline edit/save)
- Release Calendar (monthly grid, industry dates, custom events, countdowns)
- Collaboration Hub (post opportunities, browse/filter, invites, security-hardened)
- In-App Messaging (auto-conversation on invite accept, file/audio sharing, read receipts, typing indicators)
- Admin Dashboard (users, submissions, beats, royalty import, schedules, reconciliation, campaigns, leads, email settings, promo codes, referrals, analytics reports)
- Client Features (revenue analytics, leaderboard, AI strategy, fan analytics, goals, beat catalog, wallet, 4-tab release wizard, 150+ platforms)
- UI Dark Theme (animated purple/pink gradients)

## All Routes
`/` `/login` `/register` `/select-role` `/verify-email` `/pricing` `/label` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/collab-hub` `/messages` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/goals` `/referrals` `/calendar` `/settings` `/presave/:id` `/artist/:slug` `/spotify-canvas` `/content-id` `/admin` `/admin/submissions` `/admin/users` `/admin/users/:userId` `/admin/beats` `/admin/royalty-import` `/admin/campaigns` `/admin/leads` `/admin/email-settings` `/admin/promo-codes` `/admin/referrals` `/admin/analytics-reports` `/agreement`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials
- P2: Replace simulated DSP data with real API feeds
