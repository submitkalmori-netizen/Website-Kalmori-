# TuneDrop / Kalmori - Product Requirements Document

## Overview
A TuneCore clone / high-volume digital content aggregator and B2B e-commerce platform for musicians. Built as a React Web Application matching the user's existing "Kalmori" React Native Expo app design.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python) + Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: Dual (JWT cookies + Bearer token with localStorage) + Google OAuth (Emergent)
- **Payments**: Stripe (via Emergent Integrations)
- **Storage**: Emergent Object Storage
- **Email**: Resend (optional, via env var)

## Architecture
```
/app/
├── backend/
│   ├── server.py          # Main backend (auth, releases, tracks, admin, wallet, AI, etc.)
│   ├── kalmori_routes.py  # GitHub-merged routes (CMS, Cart, Credits, Social, Testimonials, etc.)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js         # Routes, AuthContext (Bearer+cookie dual auth), CartProvider
│   │   ├── services/api.js # Centralized API service (mirrors mobile app pattern)
│   │   ├── context/CartContext.jsx # Cart state management
│   │   ├── components/    # PublicLayout, AdminLayout, DashboardLayout, GlobalFooter
│   │   └── pages/         # 15+ pages (Landing, Pricing, Services, Admin, Dashboard, etc.)
│   └── .env
└── memory/ (PRD.md, test_credentials.md)
```

## Completed Features

### Frontend (All pages pixel-perfect clone of Kalmori app)
- [x] Landing Page with slideshow hero, typewriter animation, platform logos
- [x] Pricing, Services, Stores, Contact, About, Promoting, Publishing pages
- [x] Leasing/Instrumentals page
- [x] Privacy Policy & Terms pages
- [x] PublicLayout with slide-out menu matching Kalmori exactly
- [x] Admin Dashboard UI with routing
- [x] User Dashboard with stats, charts, recent releases
- [x] Auth pages (Login/Register)
- [x] **API Service** (`services/api.js`) - Centralized endpoint definitions matching mobile app [Apr 2, 2026]
- [x] **AuthContext** - Bearer token + localStorage + 30min inactivity timeout [Apr 2, 2026]
- [x] **CartContext** - Cart state management with add/remove/update/checkout [Apr 2, 2026]

### Backend - Core (server.py)
- [x] Dual auth: JWT cookies + Bearer token (register/login return {access_token, user})
- [x] Extended UserCreate with user_role, country, state, town, post_code fields
- [x] Google OAuth via Emergent Integrations
- [x] Release CRUD, Track CRUD with audio upload
- [x] Distribution, Payments (Stripe), Wallet, Analytics, AI features
- [x] Notifications, Subscriptions, Admin dashboard
- [x] Ingestion/Review engine, Split payments, File serving

### Backend - Kalmori GitHub Merge (kalmori_routes.py) [Apr 2, 2026]
- [x] CMS system (slides, pricing, legal, full page editor, instrumentals)
- [x] Shopping Cart, Credits, Payment Methods, Extended Wallet/Withdrawals
- [x] Social features (follow/unfollow), Testimonials, Theme settings
- [x] Promotion Orders, Instrumental Requests
- [x] Analytics chart data, Public releases, Video serving, reCAPTCHA

## Upcoming Tasks (P1)
- [ ] AI Features integration (metadata generation, analytics summaries) using Emergent LLM Key
- [ ] Advanced Analytics Dashboard (Audience Map, TikTok UGC trends)
- [ ] Email notifications & password reset workflows
- [ ] PayPal payment integration

## Future Tasks (P2)
- [ ] Beat audio previews on the Leasing page
- [ ] Backend modularization (split server.py into distinct router files)
- [ ] YouTube Content ID / Spotify Canvas
- [ ] Video file uploads

## Testing
- iteration_7.json: 100% pass (27/27 backend + frontend) - Kalmori routes merge
- iteration_8.json: 100% pass (16/16 backend + frontend) - Auth & service layer
