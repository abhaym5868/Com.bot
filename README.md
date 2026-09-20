# ⚡ Changelog & Product Updates Widget

> **A modern, full-stack product communication and changelog platform built with:**
> - **Python & FastAPI**
> - **MongoDB & Motor**
> - **React 18 & Vite 5**
> - **Coss UI Design System**
> - **Dual-Transport JWT Authentication**

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Solution](#3-solution)
4. [Features](#4-features)
5. [Technology Stack](#5-technology-stack)
6. [Architecture](#6-architecture)
7. [Folder Structure](#7-folder-structure)
8. [Database Design](#8-database-design)
9. [API Documentation](#9-api-documentation)
10. [Authentication Architecture](#10-authentication-architecture)
11. [Environment Variables](#11-environment-variables)
12. [Installation](#12-installation)
13. [Backend Setup](#13-backend-setup)
14. [Frontend Setup](#14-frontend-setup)
15. [MongoDB Setup](#15-mongodb-setup)
16. [Running Tests](#16-running-tests)
17. [Postman Collection](#17-postman-collection)
18. [Widget Embed / Widget Studio](#18-widget-embed--widget-studio)
19. [UI/UX Features](#19-uiux-features)
20. [Security](#20-security)
21. [Additional Features](#21-additional-features)
22. [Assumptions](#22-assumptions)
23. [Limitations](#23-limitations)
24. [Future Improvements](#24-future-improvements)
25. [License](#25-license)

---

## 1. Project Overview

**Changelog & Product Updates Widget** is a production-grade, self-hosted product communication platform designed for SaaS companies, open-source projects, and digital products. It empowers engineering and product teams to publish announcements, feature releases, performance boosts, and bug fixes directly to users via a public web timeline and an in-app embeddable widget.

The system features:
- A public **Changelog Timeline** with debounced real-time search, category taxonomy, and safe Markdown rendering.
- An in-app **"What's New" Notification Center** with real-time unread badge counts, slide-over drawer, and read-state synchronization.
- An interactive **Emoji Reaction Engine** (❤️, 🎉, 🚀) with duplicate prevention, real-time count aggregation, and user reaction state.
- An **Admin Studio** featuring a split-screen live Markdown editor, cover image upload pipeline, and draft/scheduled/publish workflows.
- A **Widget Studio** with a 6-tab customization panel, realistic customer SaaS dashboard live preview, device mode switcher, preset profiles, and multi-framework embed code generators.
- A zero-dependency, Shadow-DOM isolated **Embeddable JavaScript Widget** (`changelog-widget.js`).
- A **Public JSON Feed** and **RSS 2.0 XML Feed** with CDN-friendly HTTP caching headers.
- A hardened **Dual-Transport Authentication System** (httpOnly cookies and Bearer tokens) with rotating refresh tokens and Role-Based Access Control (RBAC).

---

## 2. Problem Statement

Modern software teams ship continuous improvements, but communicating these updates effectively remains a significant challenge:
1. **Low Feature Awareness**: Product improvements buried in marketing emails or blogs are missed by active users.
2. **Context Switching**: Sending users outside the app to read release notes causes friction and drops engagement.
3. **Expensive SaaS Lock-in**: Commercial changelog widgets (e.g., Beamer, LaunchDarkly, Headway) enforce steep recurring monthly subscription fees and vendor data capture.
4. **No Direct Feedback Loop**: Standard release notes are static broadcasts lacking immediate qualitative signals on what users appreciate.

---

## 3. Solution

A fully self-hosted, extensible, and beautifully crafted changelog platform that:
- Embeds directly into any web application or dashboard in under 2 minutes via a single `<script>` tag or React/Vue component.
- Isolates widget styling within the browser's Shadow DOM to eliminate CSS collisions.
- Provides immediate user feedback loops through lightweight emoji reactions.
- Automates publication scheduling and RSS/JSON syndication from a single intuitive administrative dashboard.
- Operates under your own infrastructure with zero third-party tracking or recurring subscription fees.

---

## 4. Features

### 📢 Public Experience
- **Reverse-Chronological Timeline**: Releases displayed with clean date formatting and pinned announcements sticky at the top.
- **Category Taxonomy**: Color-coded badges for `#New`, `#Improved`, and `#Fixed`.
- **Rich Markdown Rendering**: Headers, bullet lists, blockquotes, tables, and syntax-highlighted code blocks rendered safely without executing arbitrary HTML.
- **Images & Media**: Cover images and embedded screenshots served securely from the asset pipeline.
- **Debounced Search**: 300ms debounced search scanning both titles and markdown bodies using ReDoS-sanitized queries (`re.escape()`).
- **Dedicated Detail Pages**: Clean, SEO-friendly permalinks addressed by URL-safe slugs (e.g. `/changelog/quantum-speed-ai-assistant-v2-0`).
- **Emoji Reactions**: Immediate reader feedback via ❤️, 🎉, and 🚀 with duplicate prevention and user state tracking.

### 🔔 Notification Center
- **What's New Drawer**: Mobile-friendly slide-over panel displaying recent release cards.
- **Header Notification Bell**: Pill counter displaying the exact count of unread releases published since the user's `last_viewed_changelog_date`.
- **Read-State Synchronization**: Opening the drawer automatically syncs the read status to the server and resets the badge count.
- **Unauthenticated Visitor Support**: Displays recent product highlights seamlessly without requiring a login.

### ✍️ Admin Studio
- **Admin Dashboard**: Comprehensive management interface displaying draft, scheduled, and published release cards.
- **Changelog CRUD**: Create, edit, pin/unpin, schedule, publish, and delete release notes.
- **Split-Screen Markdown Studio**: Synchronized live editing with syntax formatting toolbar (Headings, Bold, Italic, Code, Link, List, Quote).
- **Cover Image Upload Pipeline**: Ingests JPEG, PNG, WebP, and GIF files up to 5MB, validates MIME types, and returns static asset URLs.
- **Automated Scheduling Worker**: Background scheduler auto-promotes `SCHEDULED` posts to `PUBLISHED` when their release time arrives.
- **Activity & Audit Trail**: Chronological log of administrative actions (`/admin/activity`) tracking creations, edits, pins, publishes, and deletions.

### 📊 Real Analytics & Engagement
- **Anonymous View Tracking**: Salted hash view tracker prevents double-counting without storing personally identifiable information.
- **Aggregate Metrics**: Real-time totals for views, reactions, scheduled releases, and drafts.
- **Top Performing Updates**: Identifies the most-viewed and most-reacted releases.

### 🧩 Widget Studio & Standalone Embed
- **6-Tab Customization Suite**: General, Appearance, Position, Content, Behavior, and Scoped Shadow DOM Custom CSS.
- **Presets Bar**: 1-click profiles (`Modern`, `Minimal`, `Professional`, `Compact`, `Announcement`) plus Reset to Defaults.
- **Customer SaaS Dashboard Live Preview**: Realistic mock SaaS dashboard with simulated header, sidebar, KPI cards, and data table.
- **Device Mode Switcher**: Preview across **Desktop (100%)**, **Tablet (640px)**, and **Mobile (360px)** viewports.
- **Interactive Preview Drawer**: Clicking the widget launcher opens the realistic changelog drawer with live seeded updates.
- **Multi-Framework Embed Code Generator**: Export snippets for **HTML / Script**, **React**, **Next.js**, and **Vue 3**.
- **Cloud Configuration Persistence**: Synchronizes settings directly to `GET` and `PUT /api/v1/widget/config`.

### 🌙 Theming & UI/UX
- **Multi-Option Theme Switcher**: Choose between **Light (☀️)**, **Dark (🌙)**, and **System (💻)** modes. Automatically tracks OS `prefers-color-scheme` in system mode.
- **Deep Dark Mode Tokens**: Curated obsidian surfaces (`#080B12`, `#101622`, `#182132`), structural borders (`#263044`), and electric indigo/violet accents (`#6366F1`, `#8B5CF6`).
- **Command Palette (⌘K / Ctrl+K)**: Instant keyboard-driven search modal with live query debouncing, category filter shortcuts, and direct page navigation.
- **Collapsible Admin Sidebar**: Smooth toggle between full 248px sidebar and 68px icon-only mode with persistent `localStorage` storage.
- **Sticky 64px Header**: Glassmorphic blur (`backdrop-filter: blur(16px)`), brand glow on hover, and active state indicators.

### 📡 Developer API & Syndication
- **RSS 2.0 XML Feed**: `GET /api/v1/changelog/rss` delivers an RFC 822 compliant XML feed for feed readers.
- **Public JSON Feed**: `GET /api/v1/changelog/feed` provides a lightweight JSON response with `Cache-Control: public, max-age=300`.

---

## 5. Technology Stack

| Domain | Technology | Description |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (0.115+) | Modern, high-performance Python ASGI web framework with OpenAPI schemas. |
| **Async Database Driver** | [Motor](https://motor.readthedocs.io/) (3.5+) | Official asynchronous MongoDB driver based on `asyncio` and `PyMongo`. |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | High-speed data parsing, serialization, and type enforcement. |
| **Authentication** | `python-jose`, `bcrypt` | Secure JWT HS256 token signing and timing-attack resistant password hashing. |
| **Frontend Framework** | [React 18](https://react.dev/) + [Vite 5](https://vitejs.dev/) | High-speed HMR build tool and component framework. |
| **UI Primitives** | [Coss UI](https://coss.com/ui) + [@base-ui/react](https://base-ui.com/) | Accessible, headless primitives (`Button`, `Input`, `Select`, `Badge`, `Card`, `Dialog`, `Sheet`, `Menu`, `Tabs`, `Textarea`, `Kbd`, `Separator`). |
| **Styling** | Vanilla CSS Token System | Harmonious CSS variables, glassmorphism, responsive breakpoints, and dark mode tokens without utility-class bloat. |
| **HTTP Client** | [Axios](https://axios-http.com/) | Interceptor-driven client with automatic silent JWT refresh and retry queues. |
| **Routing** | [React Router v6](https://reactrouter.com/) | Declarative client-side routing with role-guarded routes. |
| **Markdown Engine** | `react-markdown` + `remark-gfm` | GitHub Flavored Markdown renderer with safe sanitization. |

---

## 6. Architecture

```
┌────────────────────────────────────────────────────────┐
│             Web Client / Embed Widget                  │
│       (React 18 SPA  /  Shadow DOM Script)             │
└───────────────────────────┬────────────────────────────┘
                            │
              HTTP Requests │ Dual-Transport Credentials
           (REST JSON / RSS)│ (Bearer Token / httpOnly Cookie)
                            ▼
┌────────────────────────────────────────────────────────┐
│               FastAPI ASGI Application                 │
│              (Uvicorn High-Concurrency)                │
└──────┬────────────────────┬────────────────────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌───────────────┐
│ Auth & RBAC  │    │ API Routers  │     │ Static Assets │
│ Middleware   │    │ - /auth      │     │ - /uploads    │
│ - JWT HS256  │    │ - /changelog │     │ - /static/    │
│ - CSRF Cookie│    │ - /reactions │     │   widget/     │
│ - Role Guard │    │ - /notifs    │     └───────────────┘
└──────┬───────┘    │ - /analytics │
       │            │ - /widget    │
       │            │ - /audit     │
       │            └───────┬──────┘
       └────────────┬───────┘
                    ▼
┌────────────────────────────────────────────────────────┐
│               Service & Business Layer                 │
│   (Auth, Changelogs, Reactions, Notifications, Widget) │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                Async Motor Driver Pool                 │
└───────────────────────────┬────────────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│              MongoDB Document Database                 │
│          (Local Docker or MongoDB Atlas)               │
└────────────────────────────────────────────────────────┘
```

---

## 7. Folder Structure

```text
changelog-widget/
├── README.md                                  # Primary repository documentation
├── LICENSE                                    # MIT License
├── .gitignore                                 # Git ignore definitions
├── .env.example                               # Root environment configuration template
│
├── backend/
│   ├── app/
│   │   ├── config/                            # Database connection & Pydantic settings
│   │   │   ├── __init__.py
│   │   │   ├── database.py                    # Motor client, connection check & ping
│   │   │   └── settings.py                    # Environment variable parsing
│   │   ├── middleware/                        # Security & authentication dependencies
│   │   │   ├── __init__.py
│   │   │   └── auth.py                        # JWT decoding, cookie helpers & RBAC
│   │   ├── models/                            # Document definitions & schemas
│   │   │   ├── __init__.py
│   │   │   ├── base.py                        # PyObjectId serialization & timestamps
│   │   │   ├── changelog.py                   # ChangelogModel definition
│   │   │   ├── enums.py                       # Category, Status, and Role enums
│   │   │   ├── indexes.py                     # MongoDB index definitions
│   │   │   ├── reaction.py                    # ReactionModel definition
│   │   │   ├── refresh_token.py               # Token rotation records
│   │   │   ├── user.py                        # UserModel definition
│   │   │   └── widget_config.py               # Widget Studio configuration model
│   │   ├── routes/                            # FastAPI endpoint controllers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                        # Signup, login, refresh, logout, recovery
│   │   │   ├── changelog.py                   # CRUD, publish, pin, search, RSS, feed
│   │   │   ├── health.py                      # Health check & database diagnostics
│   │   │   ├── notification.py                # Notification counts & mark-read
│   │   │   ├── reaction.py                    # Reaction add/remove/summary
│   │   │   ├── upload.py                      # Image asset upload pipeline
│   │   │   └── widget_config.py               # Widget Studio configuration endpoints
│   │   ├── schemas/                           # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── changelog.py
│   │   │   ├── notification.py
│   │   │   ├── reaction.py
│   │   │   ├── user.py
│   │   │   └── widget_config.py
│   │   ├── services/                          # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── changelog_service.py
│   │   │   ├── notification_service.py
│   │   │   └── reaction_service.py
│   │   ├── utils/                             # Utility helpers
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py                         # JWT token creation & validation
│   │   │   ├── password.py                    # Bcrypt hashing & verification
│   │   │   ├── response.py                    # Standardized API response formatters
│   │   │   └── slug.py                        # URL-safe slug generator with suffixes
│   │   └── main.py                            # FastAPI app initialization, routes, CORS
│   ├── static/
│   │   └── widget/
│   │       └── changelog-widget.js            # Standalone Shadow DOM embed script
│   ├── tests/                                 # Automated integration & unit tests
│   │   ├── test_auth_api.py
│   │   ├── test_changelog_api.py
│   │   ├── test_complete_suite.py
│   │   ├── test_feed_api.py
│   │   ├── test_notification_api.py
│   │   ├── test_reaction_api.py
│   │   ├── test_search_api.py
│   │   ├── test_security.py
│   │   ├── test_upload_api.py
│   │   ├── test_v2_features.py
│   │   └── test_widget_api.py
│   ├── uploads/                               # Static image upload directory
│   ├── requirements.txt                       # Backend Python dependencies
│   ├── .env.example                           # Backend environment template
│   └── seed.py                                # Test data seeder
│
├── frontend/
│   ├── src/
│   │   ├── components/                        # Reusable React components
│   │   │   ├── ui/                            # Coss UI accessible primitives
│   │   │   │   ├── badge.jsx
│   │   │   │   ├── button.jsx
│   │   │   │   ├── card.jsx
│   │   │   │   ├── dialog.jsx
│   │   │   │   ├── input.jsx
│   │   │   │   ├── kbd.jsx
│   │   │   │   ├── menu.jsx
│   │   │   │   ├── select.jsx
│   │   │   │   ├── separator.jsx
│   │   │   │   ├── sheet.jsx
│   │   │   │   ├── tabs.jsx
│   │   │   │   ├── textarea.jsx
│   │   │   │   ├── coss-ui.css
│   │   │   │   └── index.js
│   │   │   ├── AdminSidebar.jsx               # Collapsible navigation sidebar
│   │   │   ├── CommandPalette.jsx & .css      # ⌘K global search & command modal
│   │   │   ├── DarkModeToggle.jsx             # Backwards-compatible wrapper
│   │   │   ├── MarkdownStudio.jsx & .css      # Split-screen editor & live preview
│   │   │   ├── Navbar.jsx & .css              # Sticky 64px header with brand glow
│   │   │   ├── NotificationCenter.jsx & .css  # Unread pill counter & drawer
│   │   │   ├── ProtectedRoute.jsx             # Role-based route guard
│   │   │   ├── ReactionButtons.jsx & .css     # Interactive emoji reaction pills
│   │   │   └── ThemeSwitcher.jsx              # Light / Dark / System mode menu
│   │   ├── context/
│   │   │   └── AuthContext.jsx                # Global authentication & token provider
│   │   ├── hooks/
│   │   │   ├── useApi.js                      # API state & error hook
│   │   │   └── useDebounce.js                 # Input debounce hook
│   │   ├── lib/
│   │   │   └── utils.js                       # Class concatenation helpers
│   │   ├── pages/                             # Route views
│   │   │   ├── ActivityLogPage.jsx            # Admin activity audit trail
│   │   │   ├── AdminDashboardPage.jsx & .css  # Changelog CRUD & elevated stat cards
│   │   │   ├── AnalyticsDashboardPage.jsx & .css # Views & reaction analytics
│   │   │   ├── AuthPages.css                  # Authentication forms stylesheet
│   │   │   ├── ChangelogDetailPage.jsx & .css # Single release permalink view
│   │   │   ├── FeedPage.jsx & .css            # Developer JSON & RSS feed viewer
│   │   │   ├── LoginPage.jsx                  # Sign in page
│   │   │   ├── SignupPage.jsx                 # Sign up page
│   │   │   ├── TimelinePage.jsx & .css        # Public release timeline & filters
│   │   │   ├── WidgetConfigPage.jsx           # 6-Tab Widget Studio & preview
│   │   │   └── WidgetStudio.css               # Widget Studio & mock app stylesheet
│   │   ├── services/                          # API client services
│   │   │   ├── api.js                         # Axios instance with refresh interceptor
│   │   │   ├── authService.js
│   │   │   ├── changelogService.js
│   │   │   ├── notificationService.js
│   │   │   ├── reactionService.js
│   │   │   └── widgetService.js               # Widget Studio configuration API client
│   │   ├── App.jsx                            # Application route tree
│   │   ├── index.css                          # Token system & theme styles
│   │   └── main.jsx                           # Application bootstrap
│   ├── public/                                # Public static assets
│   ├── package.json                           # Frontend dependencies & scripts
│   ├── vite.config.js                         # Vite dev server & proxy settings
│   └── .env.example                           # Frontend environment template
│
└── postman/
    ├── changelog-widget.json                  # Postman Collection v2.1.0
    └── changelog-widget.postman_collection.json
```

---

## 8. Database Design

The data store is MongoDB, with document schemas validated via Pydantic models.

### Collections

#### 1. `users` Collection
Stores user identity, role, credentials, and notification tracking timestamps.
```json
{
  "_id": ObjectId("675a1b2c3d4e5f6a7b8c9d0e"),
  "name": "Alex Mercer",
  "email": "alex@example.com",
  "password_hash": "$2b$12$e7k2m9s8...",
  "role": "admin",
  "email_verified": false,
  "refresh_token_hash": "$2b$12$...",
  "last_viewed_changelog_date": ISODate("2026-09-17T12:00:00Z"),
  "created_at": ISODate("2026-09-17T10:00:00Z"),
  "updated_at": ISODate("2026-09-17T12:00:00Z")
}
```

#### 2. `changelogs` Collection
Stores release updates with draft/scheduled/published states, categorization, and version tags.
```json
{
  "_id": ObjectId("675a2c3d4e5f6a7b8c9d0e1f"),
  "title": "Quantum Speed AI Assistant v2.0",
  "slug": "quantum-speed-ai-assistant-v2-0",
  "content_markdown": "## Instant Answers\n\nExperience 10x faster responses...",
  "category": "NEW",
  "version": "v2.0.0",
  "cover_image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f",
  "status": "PUBLISHED",
  "is_pinned": true,
  "published_at": ISODate("2026-09-17T14:30:00Z"),
  "scheduled_for": null,
  "created_by": ObjectId("675a1b2c3d4e5f6a7b8c9d0e"),
  "created_at": ISODate("2026-09-17T14:00:00Z"),
  "updated_at": ISODate("2026-09-17T14:30:00Z")
}
```

#### 3. `reactions` Collection
Captures individual emoji reactions linked to user and changelog.
```json
{
  "_id": ObjectId("675a3d4e5f6a7b8c9d0e1f2a"),
  "user_id": ObjectId("675a1b2c3d4e5f6a7b8c9d0e"),
  "changelog_id": ObjectId("675a2c3d4e5f6a7b8c9d0e1f"),
  "reaction": "🚀",
  "created_at": ISODate("2026-09-17T15:00:00Z")
}
```

#### 4. `widget_config` Collection
Stores customizable widget launcher, appearance, position, and behavior properties.
```json
{
  "_id": "default",
  "widget_name": "What's New",
  "launcher_text": "What's New",
  "launcher_style": "pill",
  "launcher_size": "md",
  "icon": "sparkle",
  "position": "bottom-right",
  "offset_x": 24,
  "offset_y": 24,
  "theme": "auto",
  "accent_color": "#6366F1",
  "border_radius": 12,
  "shadow": "medium",
  "animation": "subtle",
  "show_badge": true,
  "show_count": true,
  "max_notifications": 5,
  "title": "What's New",
  "subtitle": "Latest product announcements",
  "show_category": true,
  "show_date": true,
  "show_cover_image": true,
  "show_reactions": true,
  "show_read_more": true,
  "max_visible_updates": 5,
  "open_behavior": "drawer",
  "close_on_outside_click": true,
  "close_on_esc": true,
  "mark_read_on_open": true,
  "auto_open": false,
  "auto_open_delay": 5,
  "custom_css": "",
  "updated_at": ISODate("2026-09-21T03:30:00Z")
}
```

### Database Indexes

Created automatically on startup via [`backend/app/models/indexes.py`](backend/app/models/indexes.py):

| Collection | Index Fields | Type | Purpose |
|---|---|---|---|
| `users` | `{"email": 1}` | **Unique** | Enforces email uniqueness across all accounts. |
| `changelogs` | `{"slug": 1}` | **Unique** | Guarantees clean, unique SEO URL paths. |
| `changelogs` | `{"status": 1, "published_at": -1}` | **Compound** | Accelerates public timeline filtering ordered by date. |
| `changelogs` | `{"published_at": -1}` | Single | Speeds up reverse-chronological sorting and notification queries. |
| `changelogs` | `{"is_pinned": -1, "published_at": -1}` | **Compound** | Speeds up sticky pinned post queries. |
| `reactions` | `{"user_id": 1, "changelog_id": 1, "reaction": 1}` | **Compound Unique** | Prevents duplicate reactions of the same emoji by the same user. |
| `reactions` | `{"changelog_id": 1}` | Single | Optimizes aggregation queries for reaction counters. |
| `audit_logs` | `{"created_at": -1}` | Single | Speeds up chronological administrative audit retrieval. |
| `view_logs` | `{"changelog_id": 1, "viewer_hash": 1}` | **Compound** | Deduplicates anonymous reader view counts within a cooldown window. |

---

## 9. API Documentation

Interactive Swagger documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

| Method | Path | Access | Description |
|---|---|---|---|
| `GET` | `/` | Public | API root health confirmation. |
| `GET` | `/health` | Public | System and MongoDB connection diagnostics. |
| `POST` | `/api/v1/auth/signup` | Public | Register user. First registered user bootstraps as `admin`. Returns user profile; tokens transported via httpOnly cookies. |
| `POST` | `/api/v1/auth/login` | Public | Authenticates credentials; returns user profile and sets secure httpOnly cookies. |
| `POST` | `/api/v1/auth/refresh` | Public | Reads httpOnly refresh cookie, revokes old token, and issues fresh rotated token cookies. |
| `POST` | `/api/v1/auth/logout` | Authenticated | Revokes active refresh token in database and clears all cookies. |
| `GET` | `/api/v1/auth/csrf` | Public | Generates/retrieves CSRF double-submit token and sets `csrf_token` cookie. |
| `GET` | `/api/v1/auth/me` | Authenticated | Profile of currently authenticated user. |
| `POST` | `/api/v1/auth/forgot-password` | Public | Initiates password recovery (generic response prevents email enumeration). |
| `POST` | `/api/v1/auth/reset-password` | Public | Completes password reset using token and revokes active sessions. |
| `GET` | `/api/v1/changelog` | Public | Paginated list of published updates (admins see all). |
| `POST` | `/api/v1/changelog` | **Admin Only** | Creates a new changelog post (DRAFT, SCHEDULED, or PUBLISHED). |
| `GET` | `/api/v1/changelog/{slug}` | Public | Retrieves update by slug or ID. |
| `PUT` | `/api/v1/changelog/{id}` | **Admin Only** | Updates an existing changelog post. |
| `DELETE` | `/api/v1/changelog/{id}` | **Admin Only** | Deletes an entry and cascades deletion to reactions. |
| `POST` | `/api/v1/changelog/{id}/publish` | **Admin Only** | Publishes a draft or scheduled post. |
| `POST` | `/api/v1/changelog/{id}/pin` | **Admin Only** | Pins post to top of listings. |
| `POST` | `/api/v1/changelog/{id}/unpin` | **Admin Only** | Unpins sticky post. |
| `GET` | `/api/v1/changelog/feed` | Public | Public JSON feed with `Cache-Control: public, max-age=300`. |
| `GET` | `/api/v1/changelog/rss` | Public | RFC 822 compliant RSS 2.0 XML syndication feed. |
| `POST` | `/api/v1/reactions` | Authenticated | Adds ❤️, 🎉, or 🚀 reaction to a post. |
| `DELETE` | `/api/v1/reactions/{id}` | Authenticated | Removes previously placed reaction. |
| `GET` | `/api/v1/reactions/changelog/{id}` | Public | Aggregated reaction counts and current user's reaction state. |
| `GET` | `/api/v1/notifications` | Public/Auth | Unread release count and recent update summaries. |
| `POST` | `/api/v1/notifications/mark-read` | Authenticated | Updates `last_viewed_changelog_date` and resets badge. |
| `POST` | `/api/v1/upload/image` | **Admin Only** | Validates and saves JPEG/PNG/WebP/GIF (up to 5MB). |
| `POST` | `/api/v1/analytics/view/{id}` | Public | Records anonymous deduplicated view event. |
| `GET` | `/api/v1/analytics/dashboard` | **Admin Only** | Comprehensive aggregate metrics and top posts. |
| `GET` | `/api/v1/audit` | **Admin Only** | Chronological log of administrative actions. |
| `GET` | `/api/v1/widget/config` | Public | Returns active widget studio configuration. |
| `PUT` | `/api/v1/widget/config` | **Admin Only** | Updates persistent widget configuration. |

---

## 10. Authentication Architecture

The platform implements a hardened, zero-trust authentication architecture designed specifically to prevent Cross-Site Scripting (XSS) credential theft and Cross-Site Request Forgery (CSRF).

```
┌──────────────┐                                       ┌─────────────────────────┐
│ Client (SPA) │                                       │ FastAPI Auth Middleware │
└──────┬───────┘                                       └────────────┬────────────┘
       │                                                            │
       │ 1. POST /api/v1/auth/login { email, password }             │
       ├───────────────────────────────────────────────────────────>│
       │                                                            │ 2. Validate bcrypt hash
       │                                                            │ 3. Generate Access Token (15m, httpOnly cookie)
       │                                                            │ 4. Generate Refresh Token (7d, httpOnly cookie)
       │                                                            │ 5. Generate CSRF Token (readable cookie)
       │ 6. Response: { "user": { ... } } + Set-Cookies             │
       │<───────────────────────────────────────────────────────────┤
       │                                                            │
       │ 7. State-Changing Request (POST/PUT/DELETE)                │
       │    Headers: X-CSRF-Token: <token>                          │
       │    Cookies: access_token=<jwt>, csrf_token=<token>         │
       ├───────────────────────────────────────────────────────────>│
       │                                                            │ 8. Validate Double-Submit CSRF
       │                                                            │ 9. Verify JWT HS256 signature & RBAC
       │ 10. HTTP 200 Response                                      │
       │<───────────────────────────────────────────────────────────┤
```

### Key Security Safeguards
1. **Zero Frontend Token Storage**: Neither `access_token` nor `refresh_token` are stored in `localStorage` or `sessionStorage`. Tokens are NEVER exposed in login or signup JSON responses; responses strictly return `{ "user": { ... } }`.
2. **Strict httpOnly Cookie Transport**:
   - `access_token`: 15-minute expiry, `httpOnly`, `SameSite=Lax`, `Secure` in production.
   - `refresh_token`: 7-day expiry, `httpOnly`, `SameSite=Lax`, `Secure` in production.
3. **Double-Submit CSRF Protection**:
   - The server issues a cryptographically secure `csrf_token` in a readable cookie.
   - The frontend Axios interceptor reads this cookie and attaches the `X-CSRF-Token` header for state-changing HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`).
   - The backend validates matching tokens on all cookie-authenticated state changes. Safe methods (`GET`, `HEAD`, `OPTIONS`) and direct `Authorization: Bearer` API clients are exempt.
4. **Rotating Refresh Tokens**: Single-use refresh tokens stored hashed in MongoDB. Exchanging a refresh token generates a new pair and revokes the predecessor.
5. **Password Complexity & Session Invalidation**: Enforces minimum 8 characters with mixed-case, numbers, and special characters. Password resets revoke all active sessions immediately.
6. **Anti-Enumeration Protection**: The forgot-password endpoint returns a generic confirmation message regardless of whether an email exists.
7. **RBAC Dependency Injection**: Admin routes enforce `get_current_admin_user`, rejecting non-admin attempts with HTTP 403 Forbidden.

---

## 11. Environment Variables

### Root Configuration (`.env.example`)
Located at the root of the repository:
```env
# Backend Configuration: Copy changelog-widget/backend/.env.example to changelog-widget/backend/.env
# Frontend Configuration: Copy changelog-widget/frontend/.env.example to changelog-widget/frontend/.env
```

### Backend Configuration (`changelog-widget/backend/.env`)
| Variable | Type | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | string | `development` | Runtime mode: `development`, `staging`, or `production`. |
| `MONGO_URI` | string | *Required* | MongoDB connection string (Local or MongoDB Atlas). |
| `DATABASE_NAME` | string | `changelog_db` | Database name in MongoDB. |
| `JWT_SECRET_KEY` | string | `<GENERATE_A_RANDOM_SECRET>` | Signing key for HS256 JWTs (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`). |
| `JWT_ALGORITHM` | string | `HS256` | JWT signature algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `15` | Access token lifespan in minutes. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | int | `7` | Refresh token lifespan in days. |
| `COOKIE_SECURE` | bool | `false` | Set to `true` in production to enforce HTTPS cookies. |
| `COOKIE_SAMESITE` | string | `lax` | Cookie SameSite policy: `lax`, `strict`, or `none`. |
| `FRONTEND_URL` | string | `http://localhost:5173` | Allowed frontend origin for CORS. |
| `CORS_ORIGINS` | string | `""` | Comma-separated list of additional allowed CORS origins. |
| `UPLOAD_DIR` | string | `uploads` | Directory for uploaded media assets. |
| `MAX_UPLOAD_SIZE_MB` | int | `5` | Maximum upload file size limit in megabytes. |

### Frontend Configuration (`changelog-widget/frontend/.env`)
| Variable | Type | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | string | `http://127.0.0.1:8000` | Target URL of the backend FastAPI service. |

---

## 12. Installation & Quick Start

### Prerequisites
- **Python**: Version 3.10 or higher.
- **Node.js**: Version 18.x or higher with `npm`.
- **MongoDB**: Local MongoDB instance or free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) cluster URI.

### Clone the Repository
```bash
git clone https://github.com/abhaym5868/Com.bot.git
cd Com.bot
cd changelog-widget
```

---

## 13. Backend Setup

From the `changelog-widget` directory:

```bash
cd backend

# 1. Create Python virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate          # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment file
cp .env.example .env
# Edit .env and verify MONGO_URI is configured
# Generate a secret: python -c "import secrets; print(secrets.token_urlsafe(32))"

# 5. Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **API Root**: `http://127.0.0.1:8000/`
- **Health Diagnostic**: `http://127.0.0.1:8000/health`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

---

## 14. Frontend Setup

In a separate terminal, from the `changelog-widget` directory:

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev
```

The frontend application will start at `http://localhost:5173`.

---

## 15. MongoDB Setup

### Option A: MongoDB Atlas (Cloud - Recommended)
1. Sign in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free **M0 Sandbox** cluster.
3. In **Database Access**, create a database user with read/write privileges.
4. In **Network Access**, add `0.0.0.0/0` (or your static IP) to the IP allowlist.
5. In **Database → Connect**, copy your connection string:
   ```env
   MONGO_URI="mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/changelog_db?retryWrites=true&w=majority"
   ```
6. Paste into `backend/.env`.

### Option B: Local MongoDB (Docker)
```bash
docker run -d \
  --name changelog-mongo \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  mongo:7.0
```
Set in `backend/.env`:
```env
MONGO_URI="mongodb://localhost:27017"
DATABASE_NAME="changelog_db"
```

---

## 16. Running Tests

The backend includes automated integration test suites using `mongomock-motor` for isolated execution without mutating live data:

```bash
cd changelog-widget/backend
source venv/bin/activate

# 1. Run all pytest test suites
pytest tests/test_security.py tests/test_widget_api.py -v

# 2. Run v2 integration features test
python -m tests.test_v2_features
```

---

## 17. Postman Collection

A complete Postman collection is exported at [`postman/changelog-widget.json`](postman/changelog-widget.json).

### Importing into Postman
1. Open **Postman**.
2. Click **Import** in the upper left.
3. Select `postman/changelog-widget.json`.
4. The collection contains pre-configured requests across 5 folders:
   - **Auth**: Signup, Login, Refresh, Logout, Forgot Password, Reset Password.
   - **Changelog**: List, Create, Get by Slug, Update, Publish, Pin/Unpin, Delete.
   - **Reactions**: Add Reaction, Remove Reaction, Reaction Summary.
   - **Notifications**: Unread Count, Mark Read.
   - **Feed & RSS**: JSON Feed, RSS 2.0 Feed.
5. Automated test scripts extract `access_token`, `refresh_token`, and IDs for chained testing.

---

## 18. Widget Embed / Widget Studio

The application provides an interactive **Widget Studio** at `/admin/widget` for designing and deploying live changelog badges and slide-over drawers on any external website.

### Customization Options (6 Tabs)
1. **General**: Widget name, launcher button text, launcher style (`pill`, `circular`, `minimalist`, `badge-only`), launcher size (`sm`, `md`, `lg`), and launcher icon (`sparkle ⚡`, `bell 🔔`, `megaphone 📣`, `star ⭐`, `rocket 🚀`).
2. **Appearance**: Theme mode (`auto`, `light`, `dark`), brand accent color (picker + hex + swatches), border radius (0–24px), shadow depth (`none`, `soft`, `medium`, `elevated`), and hover animations (`none`, `subtle`, `pulse`, `bounce`).
3. **Position**: Screen anchor (`bottom-right`, `bottom-left`, `top-right`, `top-left`), horizontal offset (px), and vertical offset (px).
4. **Content**: Drawer title, subtitle, max visible updates, and display toggles for category tags, dates, reactions, and read more links.
5. **Behavior**: Display mode (`drawer`, `modal`, `popover`), outside click dismissal, ESC key dismissal, unread badge counter, and mark-read on open.
6. **Custom CSS**: Scoped Shadow DOM CSS editor for custom overrides.

### Presets & Live Customer Preview
- **Presets**: 1-click profiles (`Modern`, `Minimal`, `Professional`, `Compact`, `Announcement`) plus Reset to Defaults.
- **Realistic Customer SaaS Dashboard Live Preview**: Interactive viewport featuring mock SaaS navigation, revenue/user KPI cards, and data table.
- **Device Mode Switcher**: Inspect widget placement across **Desktop (100%)**, **Tablet (640px)**, and **Mobile (360px)** viewports.
- **Interactive Live Preview**: Click the preview launcher button to test drawer animations, unread counters, and release cards.

### Multi-Framework Code Snippets

#### HTML / Script Tag
```html
<!-- Antigravity Changelog Widget -->
<script
  src="http://127.0.0.1:8000/static/widget/changelog-widget.js"
  data-api="http://127.0.0.1:8000"
  data-position="bottom-right"
  data-theme="auto"
  data-accent="#6366F1"
  data-text="What's New"
  data-style="pill"
  data-radius="12"
  defer
></script>
```

#### React Component
```jsx
import { useEffect } from 'react';

export function ChangelogWidget() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'http://127.0.0.1:8000/static/widget/changelog-widget.js';
    script.setAttribute('data-api', 'http://127.0.0.1:8000');
    script.setAttribute('data-position', 'bottom-right');
    script.setAttribute('data-theme', 'auto');
    script.setAttribute('data-accent', '#6366F1');
    script.setAttribute('data-text', "What's New");
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.getElementById('cw-widget-host')?.remove();
    };
  }, []);

  return null;
}
```

---

## 19. UI/UX Features

- **Command Palette (⌘K / Ctrl+K)**: Instant search palette with debounced querying, category filters, and quick navigation across all admin and public views.
- **Multi-Option Theme Switcher**: Instant switching between Light, Dark, and System modes with persistent `localStorage` synchronization.
- **Collapsible Admin Sidebar**: Smooth toggle between 248px and 68px width with icon tooltips and state persistence.
- **Elevated Stat Cards**: Dashboard metrics cards with tinted icon containers, responsive grids, and subtle hover lifts.
- **Sticky 64px Header**: High-performance backdrop blur (`backdrop-filter: blur(16px)`), brand glow on hover, and active nav states.
- **Notification Bell Pill Counter**: Header bell displaying unread counter pill (`🔔 2`) with accent ring.

---

## 20. Security

1. **Password Security**: Passwords hashed with `bcrypt` using auto-generated salts.
2. **Dual-Transport Auth**: Employs `httpOnly`, `samesite="lax"` cookies to eliminate XSS token theft in web browsers, with optional Bearer tokens for mobile clients.
3. **ReDoS Mitigation**: Search inputs are sanitized via Python's `re.escape()` to protect regex engine execution.
4. **Markdown Sanitization**: `react-markdown` safe AST parser prevents arbitrary JavaScript injection (`javascript:` URIs or `<script>` tags).
5. **Role-Based Access Control**: Sensitive actions strictly require admin authorization.

---

## 21. Additional Features

- **Automatic Slug Conflict Resolution**: Titles sharing identical names automatically generate incremented suffixes (`update-v1`, `update-v1-1`).
- **Cascading Reaction Deletion**: Deleting a changelog post triggers cleanup of associated reactions to prevent orphaned records.
- **Silent Token Refresh**: Axios response interceptor catches HTTP 401s, requests a renewed token, and transparently retries failed requests.
- **Micro-Animations**: Staggered card fade-ins, pulse notifications, and smooth drawer transitions.

---

## 22. Assumptions

1. **Bootstrap Admin**: In development environments, the first registered user is automatically granted the `admin` role.
2. **Single-Tenant Core**: Releases are organized under a single product organization.
3. **UTC Timestamps**: All scheduling, dates, and audit events are generated and stored in UTC (`datetime.now(timezone.utc)`).

---

## 23. Limitations

1. **Local Media Storage**: Media uploads are saved to `backend/uploads/`. Distributed multi-server clusters should configure cloud object storage (e.g. S3, Cloudflare R2, GCS).
2. **Simulated Email Reset**: Password reset tokens are returned directly in development responses rather than sending physical emails.

---

## 24. Future Improvements

- [ ] **Multi-Tenant Organizations**: Support multiple discrete products with isolated teams and permissions.
- [ ] **Slack & Discord Webhooks**: Dispatch automated notifications to community channels on release publication.
- [ ] **Cloud Storage Adapter**: Native S3 / R2 / GCS storage drivers.
- [ ] **User Comments & Discussions**: Reader discussion threads with administrative moderation.

---

## 25. License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
