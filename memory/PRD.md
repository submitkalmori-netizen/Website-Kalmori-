# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians with Authentication, Subscriptions, Object Storage, AI Features, Release/Track uploads with a professional Wizard, Distribution to 150+ platforms, Beat/Instrumental catalog, and dark premium UI.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons + Framer Motion
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB (20+ collections)
- **Storage**: Emergent Object Storage | **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2 + Email Verification
- **AI**: OpenAI GPT-4o via Emergent LLM Key | **Email**: Resend | **PDF**: reportlab

## UI Color Theme
- **Landing page & site-wide buttons**: Purple/Pink/Magenta animated gradient (#7C4DFF -> #E040FB -> #FF4081)
- **Button pairs**: First = filled animated, Second = outline with animated border
- **Login & Register pages only**: Blue-to-Purple animated gradient (#0095FF -> #7468F8)

## Subscription Tiers
| Plan | Price | Revenue Share |
|------|-------|---------------|
| Free | $0 | 20% taken |
| Rise | $9.99/mo | 10% taken |
| Pro | $19.99/mo | 0% (keep 100%) |

## All Completed Features

### Core Auth & Emails
- JWT + Google OAuth + reCAPTCHA + Email Verification
- Welcome emails, Admin sign-up notifications

### Email Domain Management
- Admin page for custom Resend domain configuration
- Add/verify/activate domains with DNS record display

### Subscription & Plan Gating
- 3-tier system with Stripe checkout, sidebar feature gating

### Promo Code / Discount System (Apr 2026)
- Admin CRUD: create codes with % or $ discount, plan targeting, expiry, max uses, duration
- Public validation endpoint with discount calculation
- Pricing page promo code input with real-time validation
- Redemption tracking with usage counts

### Track Editing (Apr 2026)
- Full edit form on Release Detail page with 12 fields
- Title, Title Version, Explicit, ISRC (with generator), Dolby Atmos ISRC, ISWC
- Language, Production, Publisher, Preview Start/End, Artists
- Inline edit/save/cancel on each track
- PUT /api/tracks/{id} backend endpoint

### Admin Dashboard
- Users, Submissions, Beat Manager, Royalty Import
- Schedules, Reconciliation, Campaigns, Leads
- Email Settings, Promo Codes

### Client Features
- Revenue Analytics + Export, Leaderboard, AI Strategy + PDF Export
- Fan Analytics, Goals, Beat catalog, Wallet
- 4-tab Release Wizard, 150+ platforms

### UI/UX Dark Theme
- Animated purple/pink gradients on landing page and all buttons
- Footer KALMORI logo animated, Emergent badge hidden
- Kalmori Artist Agreement page

## All Pages & Routes
`/` `/login` `/register` `/select-role` `/verify-email` `/pricing` `/label` `/instrumentals` `/dashboard` `/releases` `/releases/new` `/analytics` `/wallet` `/purchases` `/collaborations` `/presave-manager` `/fan-analytics` `/revenue` `/leaderboard` `/goals` `/settings` `/presave/:id` `/artist/:slug` `/spotify-canvas` `/content-id` `/admin` `/admin/submissions` `/admin/users` `/admin/users/:userId` `/admin/beats` `/admin/royalty-import` `/admin/campaigns` `/admin/leads` `/admin/email-settings` `/admin/promo-codes` `/agreement`

## Remaining Backlog
- P1: Real Spotify OAuth with API credentials
- P2: Replace simulated DSP data with real API feeds
