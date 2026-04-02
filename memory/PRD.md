# Kalmori - TuneCore Clone PRD

## Original Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Core requirements include Authentication, Subscriptions (Stripe/PayPal), Object Storage for high-res files, AI Features, Artist/User management, Release/Track uploads (with a Wizard), Distribution store management, and a Beat/Instrumental catalog for leasing and purchasing.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + Phosphor Icons
- **Backend**: FastAPI (modularized: server.py + core.py + /routes/)
- **Database**: MongoDB
- **Storage**: Emergent Object Storage
- **Payments**: Stripe + PayPal
- **Auth**: JWT + Google Social Login + reCAPTCHA v2
- **AI**: OpenAI via Emergent LLM Key
- **Email**: Resend (real API key)

## All Completed Features

### Core Platform
- JWT + Google Auth + reCAPTCHA v2, Admin Dashboard, Responsive dark UI

### Content & Distribution
- Professional 4-tab Release Wizard (General Info, Tracks, Territory/37 platforms, Summary with validation)
- UPC auto-generation, Copyright/Production lines, Volume management
- Cover Art + Booklet uploads, Spotify Canvas & Content ID

### Commerce & Payments
- Stripe subscriptions + upgrade/downgrade, Beat catalog + Object Storage
- Beat Purchase (4 license tiers), Download delivery, My Purchases page, Wallet

### Analytics & Insights
- Realistic DSP simulation (8 platforms, 14 countries, peak hours, growth curves, weekend boosts)
- Live Streaming Feed, Platform Breakdown, AI insights, CSV import
- Share Your Stats social cards with milestones

### Notifications & Communication
- Push Notifications (bell + dropdown + 30s polling)
- 8 notification preferences (email + push toggles)
- Resend email receipts (beat + subscription templates)

### Collaborations
- Invite system, Accept/Decline, Royalty splits, Email + in-app notifications

### Beat Catalog Search/Filter
- Search by name/genre/mood/tags, Genre/Mood/Key/BPM range/Price range filters
- Sort: newest, price low/high, BPM low/high
- Share buttons on beat cards

### Social Sharing
- Public share endpoints for beats, releases, artists with OG meta data
- Shareable deep links with rich previews

### Pre-Save Campaigns
- Campaign manager (create/delete), Public landing pages
- Countdown timer, Spotify/Apple Music/YouTube links
- Email subscription with confirmation, Subscriber count tracking

### Backend Architecture
- Modularized: server.py + core.py + /routes/ (ai, email, paypal, content, beats, collab)

## Key Pages & Routes
- `/` Landing, `/login`, `/register`, `/instrumentals` (beat catalog + search/filter)
- `/dashboard`, `/releases`, `/releases/new` (4-tab wizard), `/analytics`
- `/wallet`, `/purchases`, `/collaborations`, `/presave-manager`, `/settings`
- `/presave/:id` (public landing), `/spotify-canvas`, `/content-id`
- `/admin/*` (admin panel)

## Remaining Backlog
- Real DSP API OAuth integration (Spotify for Artists, Apple Music Analytics)
- Social sharing deep link OG tags in index.html
