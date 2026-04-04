# Kalmori — TuneCore Clone / Digital Music Distribution Platform

## Problem Statement
Build a TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Core requirements include Authentication, Subscriptions, Object Storage for high-res files, AI Features, Artist/User management, Release/Track uploads, Distribution store management, Beat Marketplace, and strict Kalmori white-labeling.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Framer Motion + @dnd-kit
- **Backend**: FastAPI (Python) + MongoDB
- **Payments**: Stripe + PayPal
- **Storage**: Emergent Object Storage
- **AI**: Emergent LLM Key (OpenAI) for strategies, TTS for voice tags
- **Email**: Resend API (support@kalmori.org)
- **Auth**: JWT + Google OAuth (Emergent)
- **PDF**: reportlab
- **Audio**: pydub + ffmpeg
- **QR**: qrcode (Python)
- **DSP**: Spotify Web API (spotipy)

## Key Credentials
- Admin: admin@kalmori.com / Admin123!
- Secondary Admin: submitkalmori@gmail.com / Admin123!
- Spotify Client ID: f3d8dbd3c4f441efa5ca51edd0d455b1

## Implemented Features (All Tested & Verified)
1. Auth (JWT + Google OAuth + reCAPTCHA + Password Reset)
2. Subscription Plans (Free/Pro/Label) with Stripe Checkout
3. Release/Track Wizard (4-tab flow with audio upload)
4. Distribution Management (store selection, status tracking)
5. Fan Analytics Dashboard (streams, demographics, geo)
6. AI Release Strategy (Emergent LLM)
7. Save & Compare Strategies
8. Strategy Export to PDF (reportlab)
9. AI Smart Notifications
10. Weekly Digest Emails (Resend)
11. Revenue Analytics & Royalty Calculator
12. Release Performance Leaderboard
13. Goal Tracking & Milestones
14. Artist Public Profile (shareable link-in-bio)
15. Pre-Save Campaigns
16. Beat Marketplace (4-tier licensing)
17. Beat Purchase Contracts with E-Signatures + PDF Generation
18. AI Audio Watermarking (OpenAI TTS voice tags + pydub)
19. Collaboration Hub (posts, invites, messaging)
20. In-App Messaging (real-time chat, file/audio sharing, read receipts, typing indicators)
21. Producer Royalty Split System
22. Admin Payout Dashboard (batch processing, CSV export)
23. Automated Payout Scheduling ($100 threshold)
24. Artist Profile Enhancements (Audio Preview Player, Custom Theme Colors, QR Code Generator)
25. Landing Page Overhaul (12 feature cards + 3 detailed highlights)
26. Backend Refactoring (server.py split into route modules)
27. **Admin Page Builder V1** — Drag-and-drop visual editor with 12 block types
28. **Admin Page Builder V2 Enhancements** — Custom CSS injection, Image uploads, Block duplication, Multi-page selector (Landing/About/Pricing) — *Apr 2026*
29. **Spotify DSP OAuth Integration** — Real Spotify Web API connection with artist data, top tracks, albums, discography, and related artists — *Apr 2026*

## Admin Page Builder Details
- **Route**: `/admin/page-builder/:slug` (admin only)
- **Block Types**: Hero Banner, Text Block, Image, Feature Grid, CTA, Testimonials, Stats Row, Spacer, Two Columns, Pricing, Logo Bar, Video Embed
- **V2 Features**: Custom CSS injection per block, Image upload via Object Storage, Block duplication, Page Selector (Landing/About/Pricing)
- **Rendering**: DynamicPageRenderer overrides default About/Pricing/Landing pages when published

## Spotify Integration Details
- **OAuth Flow**: User clicks Connect → redirected to Spotify → callback stores tokens in DB
- **Data Available**: Artist profile, followers, popularity, top tracks, albums/singles, related artists
- **Pages**: /spotify (analytics dashboard), /settings > Integrations tab (connect/disconnect)
- **Redirect URI**: {FRONTEND_URL}/api/spotify/callback (must be registered in Spotify Developer Dashboard)
- **Library**: spotipy (Python)

## Backend Route Files
- `server.py` — Auth, Releases, Tracks, Distribution, Analytics, Goals, Wallet, Subscriptions, Purchases
- `routes/page_builder_routes.py` — Page Builder CRUD + publish + file upload + public file serving
- `routes/spotify_routes.py` — Spotify OAuth, artist data, connection management
- `routes/messages_routes.py` — In-App Messaging / Chat
- `routes/royalty_routes.py` — Producer Royalty Splits
- `routes/payouts_routes.py` — Admin Payout Dashboard
- `routes/ai_routes.py` — AI Strategy, Smart Insights, PDF Export
- `routes/email_routes.py` — Email notifications, digests
- `routes/beats_routes.py` — Beat Marketplace, watermarking
- `routes/collab_routes.py` — Collaboration Hub
- `routes/admin_routes.py` — Admin user management
- `routes/content_routes.py` — Content CRUD
- `routes/label_routes.py` — Label management
- `routes/paypal_routes.py` — PayPal integration

## DB Collections
users, releases, tracks, stream_events, artist_profiles, beats, contracts, conversations, messages, typing_status, royalty_splits, split_earnings, wallets, withdrawals, payout_settings, goals, notifications, notification_preferences, presave_campaigns, collaboration_posts, collab_invites, saved_strategies, digest_log, page_layouts, spotify_connections

## Remaining / Future Tasks
- P0: User must add redirect URI to Spotify Developer Dashboard for OAuth to work on production
- P0: Remind user to deploy (Save to Github) so login fix + page builder + Spotify work on kalmori.org
- P2: Further server.py refactoring (analytics, purchases sections into /routes/)
- P3: Apple Music for Artists integration (when API credentials available)
- P3: YouTube Music Analytics integration
