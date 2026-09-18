# ⚡ Changelog & Product Updates Widget

> **A modern, full-stack product communication and changelog platform built with FastAPI, MongoDB, React, and Vite.**

---

## 1. Project Overview

**Changelog & Product Updates Widget** is a production-grade, self-hosted SaaS application designed to help engineering and product teams communicate product releases, feature additions, performance improvements, and bug fixes directly to their users.

The system features:
- A public-facing interactive **Changelog Timeline** with debounced real-time search, category filtering, and responsive design.
- An in-app **"What's New" Notification Center** with real-time unread badge counts, popover/slide-over drawer, and read-state synchronization.
- An interactive **Emoji Reaction Engine** (❤️, 🎉, 🚀) with duplicate prevention, real-time count aggregation, and user reaction state.
- An **Admin Studio** with a split-screen live Markdown preview, cover image upload pipeline, and draft/publish workflow.
- A **Public JSON Feed** (`/api/v1/changelog/feed`) with CDN-friendly `Cache-Control` headers for RSS-style syndication, embeds, or mobile clients.
- A robust, hardened **Authentication & RBAC System** utilizing short-lived access tokens, long-lived rotating refresh tokens, and dual-transport authentication (httpOnly cookies and Bearer headers).

---

## 2. Problem Statement

Modern software teams ship features and bug fixes continuously, but communicating these changes effectively remains challenging:
1. **Low Feature Adoption**: Users frequently miss product improvements buried in email blasts or blog posts.
2. **Context Switching**: Directing users away from the application to external blogs causes friction and drops engagement.
3. **Complex Third-Party Services**: Commercial changelog widgets (e.g., Beamer, LaunchDarkly, Headway) introduce vendor lock-in, recurring SaaS subscription costs, and privacy concerns.
4. **Lack of Feedback Loops**: Most changelogs are one-way broadcasts without immediate feedback on whether users appreciate specific updates.

**Solution**: A fully-featured, performant, and self-hosted changelog engine providing an embeddable notification widget, public timeline, and feedback mechanisms directly under your control.

---

## 3. Features

### 📢 Public Changelog Timeline
- **Reverse-Chronological Stream**: Latest product releases displayed first with formatted publication dates.
- **Category Taxonomy**: Color-coded badges for `#New`, `#Improved`, and `#Fixed`.
- **Rich Markdown Rendering**: Headers, lists, quotes, tables, and syntax-highlighted code blocks rendered safely without arbitrary HTML execution.
- **Dedicated Detail Pages**: Clean, SEO-friendly permalinks by URL-safe slugs (e.g., `/changelog/superfast-ai-assistant`).

### 🔍 Real-Time Debounced Search & Filters
- **Instant Search**: Debounced search (300ms) querying both update titles and markdown body content.
- **Injection-Safe Queries**: MongoDB queries sanitized with `re.escape()` to prevent ReDoS and regex operator injection.
- **Category Filter Chips**: Single-click filtering between all updates or specific categories.

### 🔔 "What's New" Notification Center
- **Live Unread Counter**: Displays accurate badge count of updates published since the user's `last_viewed_changelog_date`.
- **Slide-Over Notification Drawer**: Mobile-friendly side panel displaying recent update cards and excerpts.
- **Zero-Friction Read Tracking**: Opening the drawer automatically syncs `last_viewed_changelog_date` with the server and resets the badge to zero.
- **Unauthenticated Visitor Support**: Displays recent product highlights without requiring an account.

### 💖 Interactive Reaction System
- **Three Core Emojis**: Quick feedback via ❤️ (Love), 🎉 (Celebration), and 🚀 (Rocket).
- **Duplicate Prevention**: Database-level unique constraint (`user_id` + `changelog_id` + `reaction`) ensures a user cannot double-react.
- **Optimistic State & Removal**: Users can click to react or click again to withdraw their reaction.
- **Aggregated Counts**: Provides total counts and dynamic flags (`user_reacted: true/false`) per reaction type.

### ✍️ Admin Markdown Studio & Lifecycle Management
- **Split-Screen Studio**: Live side-by-side editing with synchronized Markdown preview.
- **Formatting Toolbar**: One-click insertion for headings, bold, italic, code blocks, lists, links, and quotes.
- **Draft / Publish Workflows**: Posts remain in `DRAFT` status and strictly invisible to public visitors until published.
- **Automatic Slug Generation**: Clean URL slugs generated automatically from titles with conflict resolution (e.g., `feature-v1`, `feature-v1-1`).
- **Cover Image Upload Pipeline**: Ingests JPEG, PNG, WebP, and GIF assets up to 5MB, validates MIME types and file sizes, and serves them securely.

### 📡 Public JSON Feed
- **Syndication Ready**: `GET /api/v1/changelog/feed` delivers a clean, lightweight JSON response of published entries.
- **HTTP Caching**: Emits `Cache-Control: public, max-age=300` headers for edge CDN and browser caching.

---

## 4. Technology Stack

| Domain | Technology | Rationale |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (0.115+) | High-performance Python ASGI framework with automatic OpenAPI documentation and strict type enforcement. |
| **Async MongoDB Driver** | [Motor](https://motor.readthedocs.io/) (3.5+) | Official asynchronous Python driver for MongoDB based on `asyncio` and `PyMongo`. |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | High-speed data serialization and schema validation using Rust core (`pydantic-core`). |
| **Security & Auth** | `bcrypt`, `python-jose` | Timing-attack resistant password hashing with unique salts and HS256 JWT signature verification. |
| **Frontend Framework** | [React 18](https://react.dev/) + [Vite 5](https://vitejs.dev/) | Sub-second HMR development server with tree-shaken, highly optimized production bundles. |
| **HTTP Client** | [Axios](https://axios-http.com/) | Configured with automatic request interceptors and token refresh error retry queues. |
| **Routing** | [React Router v6](https://reactrouter.com/) | Client-side routing with route guards (`ProtectedRoute`) for admin areas. |
| **Markdown Rendering** | `react-markdown` + `remark-gfm` | Safe Markdown rendering adhering to GitHub Flavored Markdown standards. |
| **Design System** | Custom Vanilla CSS | Tailored CSS variables, glassmorphism (`backdrop-filter`), smooth micro-animations, and responsive layouts without bloated CSS libraries. |

---

## 5. System Architecture

```
                                  ┌────────────────────────┐
                                  │      Web Browser       │
                                  │   (React 18 SPA/Vite)  │
                                  └───────────┬────────────┘
                                              │
                    HTTP Requests             │ Credentials (Bearer Token /
                    & Static Assets           │ httpOnly Cookies)
                                              ▼
                                  ┌────────────────────────┐
                                  │   FastAPI ASGI Server  │
                                  │     (Uvicorn Engine)   │
                                  └───────────┬────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              │                               │                               │
              ▼                               ▼                               ▼
    ┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
    │  Auth Middleware │            │   Route Routers  │            │ Static Storage   │
    │  - JWT HS256     │            │  - /auth         │            │  /static/uploads │
    │  - Token Refresh │            │  - /changelog    │            │  (Local disk /   │
    │  - Role Guard    │            │  - /reactions    │            │   File system)   │
    └─────────┬────────┘            │  - /notifications│            └──────────────────┘
              │                     │  - /upload       │
              │                     └─────────┬────────┘
              └───────────────┬───────────────┘
                              ▼
                    ┌──────────────────┐
                    │  Service Layer   │
                    │  (Business Logic)│
                    └─────────┬────────┘
                              ▼
                    ┌──────────────────┐
                    │ Async Motor Pool │
                    └─────────┬────────┘
                              ▼
                    ┌──────────────────┐
                    │ MongoDB Database │
                    │ (Atlas or Local) │
                    └──────────────────┘
```

---

## 6. Folder Structure

```text
changelog-widget/
├── backend/
│   ├── app/
│   │   ├── config/              # Configuration & settings
│   │   │   ├── database.py      # Motor async database connection & health check
│   │   │   └── settings.py      # Pydantic BaseSettings loading from .env
│   │   ├── middleware/          # Security & Auth dependencies
│   │   │   └── auth.py          # JWT extraction, cookie helpers, RBAC dependencies
│   │   ├── models/              # MongoDB document definitions & indexes
│   │   │   ├── base.py          # PyObjectId validator & timestamp utilities
│   │   │   ├── changelog.py     # ChangelogModel definition
│   │   │   ├── enums.py         # Category, Status, and Role enumerations
│   │   │   ├── indexes.py       # MongoDB index setup routines
│   │   │   ├── reaction.py      # ReactionModel definition
│   │   │   └── user.py          # UserModel definition
│   │   ├── routes/              # Thin HTTP endpoint controllers
│   │   │   ├── auth.py          # Signup, Login, Refresh, Logout, Forgot/Reset
│   │   │   ├── changelog.py     # CRUD, Publish, Detail, Search, Public Feed
│   │   │   ├── health.py        # /health diagnostic endpoint
│   │   │   ├── notification.py  # Unread count & mark-read handlers
│   │   │   ├── reaction.py      # Add, remove, and list reactions
│   │   │   └── upload.py        # Image file upload & validation
│   │   ├── schemas/             # Pydantic request & response DTOs
│   │   │   ├── auth.py          # Login, signup, token response schemas
│   │   │   ├── changelog.py     # Create, update, filter, feed schemas
│   │   │   └── reaction.py      # Reaction creation & aggregation summary schemas
│   │   ├── services/            # Pure business logic & database interaction
│   │   │   ├── auth_service.py
│   │   │   ├── changelog_service.py
│   │   │   ├── notification_service.py
│   │   │   └── reaction_service.py
│   │   ├── utils/               # Helper utilities (JWT encode/decode)
│   │   │   └── jwt.py
│   │   └── main.py              # FastAPI application bootstrap & CORS setup
│   ├── tests/                   # Automated pytest/asyncio integration test suites
│   │   ├── test_auth_api.py
│   │   ├── test_changelog_api.py
│   │   ├── test_complete_suite.py   # Master 45+ test E2E verification suite
│   │   ├── test_feed_api.py
│   │   ├── test_notification_api.py
│   │   ├── test_reaction_api.py
│   │   ├── test_search_api.py
│   │   ├── test_security.py
│   │   └── test_upload_api.py
│   ├── uploads/                 # Static upload storage directory
│   ├── requirements.txt         # Backend Python dependencies
│   ├── .env.example             # Documented template for environment variables
│   └── .env                     # Local environment file (never committed)
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── MarkdownStudio.jsx & .css    # Split-screen editor & live preview
│   │   │   ├── Navbar.jsx & .css            # Glassmorphic header & navigation
│   │   │   ├── NotificationCenter.jsx & .css# Unread bell & slide-over drawer
│   │   │   ├── ProtectedRoute.jsx           # Role-based route guard
│   │   │   └── ReactionButtons.jsx & .css   # Interactive ❤️, 🎉, 🚀 reaction pills
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # Global session state & refresh provider
│   │   ├── pages/               # Route views
│   │   │   ├── AdminDashboardPage.jsx & .css# Changelog management & table view
│   │   │   ├── AuthPages.css    # Unified styles for auth forms
│   │   │   ├── ChangelogDetailPage.jsx & .css# Single release note view
│   │   │   ├── ForgotPasswordPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── ResetPasswordPage.jsx
│   │   │   ├── SignupPage.jsx
│   │   │   └── TimelinePage.jsx & .css      # Public changelog feed & search
│   │   ├── services/
│   │   │   ├── api.js           # Configured Axios instance with retry interceptors
│   │   │   ├── authService.js
│   │   │   ├── changelogService.js
│   │   │   ├── notificationService.js
│   │   │   └── reactionService.js
│   │   ├── App.jsx              # Routing definition
│   │   ├── index.css            # Design token system & global utilities
│   │   └── main.jsx             # React entry point
│   ├── package.json
│   └── vite.config.js
│
├── postman/
│   ├── changelog-widget.json                   # Exported Postman collection v2.1.0
│   └── changelog-widget.postman_collection.json
├── .gitignore
└── README.md
```

---

## 7. Database Design

The data store is MongoDB, leveraging document schemas defined and validated via Pydantic.

### Collections & Schemas

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
Stores product updates with draft/publish status and categorization.
```json
{
  "_id": ObjectId("675a2c3d4e5f6a7b8c9d0e1f"),
  "title": "Quantum Speed AI Assistant v2.0",
  "slug": "quantum-speed-ai-assistant-v2-0",
  "content_markdown": "## Instant Answers\n\nExperience 10x faster responses...",
  "category": "NEW",
  "cover_image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f",
  "status": "PUBLISHED",
  "published_at": ISODate("2026-09-17T14:30:00Z"),
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

### Database Indexes

Created automatically on application startup via [`app/models/indexes.py`](file:///Users/abhay/allprojects/demo/changelog-widget/backend/app/models/indexes.py):

| Collection | Index Fields | Type | Purpose |
|---|---|---|---|
| `users` | `{"email": 1}` | **Unique** | Enforces email uniqueness across all accounts. |
| `changelogs` | `{"slug": 1}` | **Unique** | Guarantees clean, unique SEO URL paths. |
| `changelogs` | `{"status": 1, "published_at": -1}` | **Compound** | Accelerates public queries filtering by published status ordered by date. |
| `changelogs` | `{"published_at": -1}` | Single | Speeds up reverse-chronological sorting and notification queries. |
| `reactions` | `{"user_id": 1, "changelog_id": 1, "reaction": 1}` | **Compound Unique** | Prevents duplicate reactions of the same emoji by the same user on a changelog. |
| `reactions` | `{"changelog_id": 1}` | Single | Optimizes aggregation queries for reaction counters. |

---

## 8. API Documentation

Interactive Swagger documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

### Endpoint Directory

| Method | Path | Access | Description |
|---|---|---|---|
| `GET` | `/` | Public | Sanity check / API status confirmation. |
| `GET` | `/health` | Public | Real-time health check reporting API and MongoDB connection status. |
| `POST` | `/api/v1/auth/signup` | Public | User registration. First account bootstrapped as `admin`. |
| `POST` | `/api/v1/auth/login` | Public | Authenticates user; returns JWTs and sets httpOnly cookies. |
| `GET` | `/api/v1/auth/me` | Authenticated | Fetches profile of the currently logged-in user. |
| `POST` | `/api/v1/auth/refresh` | Public | Rotates refresh token and issues a new access token. |
| `POST` | `/api/v1/auth/logout` | Authenticated | Revokes current session and clears cookies. |
| `POST` | `/api/v1/auth/forgot-password` | Public | Initiates password recovery. |
| `POST` | `/api/v1/auth/reset-password` | Public | Sets new password using reset verification token. |
| `GET` | `/api/v1/changelog` | Public | Paginated list of published updates (admins can view drafts). |
| `POST` | `/api/v1/changelog` | **Admin Only** | Creates a new changelog post (DRAFT or PUBLISHED). |
| `GET` | `/api/v1/changelog/{slug}` | Public | Retrieves update by slug or ObjectId (drafts return 404 to public). |
| `PUT` | `/api/v1/changelog/{id}` | **Admin Only** | Updates an existing changelog entry. |
| `DELETE` | `/api/v1/changelog/{id}` | **Admin Only** | Deletes an entry and cascades deletion to associated reactions. |
| `POST` | `/api/v1/changelog/{id}/publish`| **Admin Only** | Transitions draft to PUBLISHED and sets `published_at`. |
| `GET` | `/api/v1/changelog/feed` | Public | Unauthenticated JSON feed with `Cache-Control: public, max-age=300`. |
| `POST` | `/api/v1/reactions` | Authenticated | Adds a reaction (❤️, 🎉, 🚀) to a changelog. |
| `DELETE` | `/api/v1/reactions/{id}` | Authenticated | Removes a previously added reaction (owner or admin only). |
| `GET` | `/api/v1/reactions/changelog/{id}`| Public | Returns reaction counts and whether the current user reacted. |
| `GET` | `/api/v1/notifications` | Public/Auth | Returns unread count and recent updates. |
| `POST` | `/api/v1/notifications/mark-read` | Authenticated | Updates `last_viewed_changelog_date` and resets badge to 0. |
| `POST` | `/api/v1/upload/image` | **Admin Only** | Uploads image (JPEG, PNG, WebP, GIF up to 5MB) returning static URL. |

---

## 9. Authentication Architecture

The application implements a zero-trust, stateless authentication model:

```
┌──────────────┐                                       ┌─────────────────────────┐
│ Client (SPA) │                                       │ FastAPI Auth Middleware │
└──────┬───────┘                                       └────────────┬────────────┘
       │                                                            │
       │ 1. POST /auth/login { email, password }                    │
       ├───────────────────────────────────────────────────────────>│
       │                                                            │ 2. Validate bcrypt hash
       │                                                            │ 3. Generate Access Token (15m)
       │                                                            │ 4. Generate Refresh Token (7d)
       │                                                            │ 5. Save Refresh hash in DB
       │ 6. Return tokens + Set-Cookie (httpOnly, samesite="lax")   │
       │<───────────────────────────────────────────────────────────┤
       │                                                            │
       │ 7. Protected Request (Header: "Bearer <token>" OR Cookie)  │
       ├───────────────────────────────────────────────────────────>│
       │                                                            │ 8. Verify HS256 signature
       │                                                            │ 9. Verify exp & sub (User ID)
       │ 10. HTTP 200 Response                                      │
       │<───────────────────────────────────────────────────────────┤
```

### Key Security Safeguards
1. **Short-Lived Access Tokens**: Signed with HS256, carrying a 15-minute expiration window to limit damage if intercepted.
2. **Rotating Refresh Tokens**: Single-use refresh tokens stored hashed in MongoDB. When a refresh token is exchanged, a new pair is issued and the old token is invalidated.
3. **Dual Transport Authentication**: Supports both `Authorization: Bearer <token>` (for API clients, Swagger, and mobile) and `httpOnly`, `samesite="lax"` cookies (for secure web browsers).
4. **Role-Based Access Control (RBAC)**: Route handlers enforce `get_current_admin_user` using dependency injection, rejecting unauthorized operations with HTTP 403.
5. **Privilege Escalation Prevention**: In production mode, automatic admin role assignment is disabled; only the first bootstrap user or emails listed in `ADMIN_EMAILS` are granted administrative access.

---

## 10. Environment Variables

### Backend Configuration (`backend/.env`)

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | string | `development` | Runtime mode: `development`, `staging`, or `production`. |
| `MONGO_URI` | string | *Required* | MongoDB connection string (Local or MongoDB Atlas). |
| `DATABASE_NAME` | string | `changelog_db` | Name of the database within MongoDB. |
| `JWT_SECRET_KEY` | string | *Dev default* | Signing secret for HS256 JWTs (min 32 chars in production). |
| `JWT_ALGORITHM` | string | `HS256` | JWT signature algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `15` | Access token lifespan in minutes. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | int | `7` | Refresh token lifespan in days. |
| `FRONTEND_URL` | string | `http://localhost:5173` | Frontend URL allowed for CORS headers. |
| `CORS_ORIGINS` | string | `""` | Optional comma-separated list of additional CORS origins. |
| `ADMIN_EMAILS` | string | `""` | Comma-separated list of emails granted ADMIN role in production. |
| `UPLOAD_DIR` | string | `uploads` | Local directory for static uploaded images. |
| `MAX_UPLOAD_SIZE_MB` | int | `5` | Maximum image upload file size limit in megabytes. |

### Frontend Configuration (`frontend/.env`)

| Variable | Type | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | string | `http://localhost:8000` | Target URL of the backend FastAPI service. |

---

## 11. Step-by-Step Installation

### Prerequisites
- **Python**: Version 3.11 or higher.
- **Node.js**: Version 18.x or higher with `npm`.
- **MongoDB**: A running local MongoDB instance or a free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) cluster URI.

### 1. Clone Repository
```bash
git clone https://github.com/your-org/changelog-widget.git
cd changelog-widget
```

---

## 12. Running Backend

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
# Open .env and ensure MONGO_URI is set

# 5. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend server is now running:
- **API Root**: `http://localhost:8000/`
- **Health Diagnostic**: `http://localhost:8000/health`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`

---

## 13. Running Frontend

In a separate terminal window:

```bash
cd frontend

# 1. Install NPM packages
npm install

# 2. Start Vite development server
npm run dev
```

The React frontend will start instantly at `http://localhost:5173`.

---

## 14. MongoDB Setup

### Option A: MongoDB Atlas (Cloud Cluster - Recommended)
1. Sign in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free **M0 Sandbox** cluster.
3. Under **Security → Database Access**, create a user with read and write privileges.
4. Under **Security → Network Access**, add `0.0.0.0/0` (or your static IP address) to the IP access list.
5. In **Database → Connect**, copy your connection string:
   ```env
   MONGO_URI="mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/changelog_db?retryWrites=true&w=majority"
   ```
6. Paste the connection string into `backend/.env`.

### Option B: Local MongoDB (Docker)
Run MongoDB locally in one command:
```bash
docker run -d \
  --name changelog-mongo \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  mongo:7.0
```
Then set in `backend/.env`:
```env
MONGO_URI="mongodb://localhost:27017"
DATABASE_NAME="changelog_db"
```

Database indexes are automatically verified and created when the FastAPI server boots.

---

## 15. Running the Complete Test Suite

The project includes an end-to-end automated test suite utilizing `mongomock-motor` for isolated execution:

```bash
cd backend
source venv/bin/activate

# Execute all 9 test suites
PYTHONPATH=. python -c "
import sys, subprocess
test_files = [
    'tests/test_auth_api.py',
    'tests/test_changelog_api.py',
    'tests/test_feed_api.py',
    'tests/test_notification_api.py',
    'tests/test_reaction_api.py',
    'tests/test_search_api.py',
    'tests/test_security.py',
    'tests/test_upload_api.py',
    'tests/test_complete_suite.py',
]
for t in test_files:
    p = subprocess.run([sys.executable, t], capture_output=True, text=True)
    assert p.returncode == 0, f'Failed {t}: {p.stderr}'
    print(f'PASSED: {t}')
print('\nALL TEST SUITES PASSED FLAWLESSLY!')
"
```

---

## 16. Postman Collection

A Postman collection is exported at [`postman/changelog-widget.json`](file:///Users/abhay/allprojects/demo/changelog-widget/postman/changelog-widget.json).

### Importing into Postman
1. Open **Postman**.
2. Click **Import** in the upper left.
3. Select `postman/changelog-widget.json`.
4. The collection is organized into 5 logical folders:
   - **Auth**: Signup, Login, Refresh, Logout, Forgot Password, Reset Password.
   - **Changelog**: Create, List, Detail, Update, Publish, Delete.
   - **Reactions**: Add Reaction, Remove Reaction.
   - **Notifications**: Unread Count, Mark Read.
   - **Feed**: Public JSON Feed.
5. All requests are wired with test scripts that automatically capture `access_token`, `refresh_token`, `changelog_id`, `changelog_slug`, and `reaction_id` across subsequent requests.

---

## 17. UI & Experience Preview

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│  ⚡ Changelog           Timeline    JSON Feed   [ 🔔 3 ]     (A) Alex Admin [Sign out] │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Product Updates & Releases                                                     │
│   Stay up to date with the latest features, improvements, and bug fixes.        │
│                                                                                  │
│   [ 🔍 Search updates by keyword...            ]                                 │
│   [ ALL ]   [ # New ]   [ # Improved ]   [ # Fixed ]                             │
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐   │
│   │  [ #New ]  ·  September 17, 2026                                         │   │
│   │  Quantum Speed AI Assistant v2.0                                         │   │
│   │  ──────────────────────────────────────────────────────────────────────  │   │
│   │  We are thrilled to unveil our second-generation AI engine...            │   │
│   │                                                                          │   │
│   │  [ ❤️ 12 ]   [ 🎉 8 ]   [ 🚀 24 ]                  Read full update →    │   │
│   └──────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 18. Additional Features Implemented

- **Slug Collision Resolution**: Creating multiple posts with the same title automatically appends numerical suffixes (`update-v1`, `update-v1-1`, `update-v1-2`).
- **Cascading Reaction Cleanup**: Deleting a changelog automatically cleans up all associated reactions in MongoDB to prevent orphaned data.
- **Silent Token Renewal**: Axios response interceptors intercept HTTP 401s, silently refresh the JWT via `/auth/refresh`, and seamlessly retry queued requests without disrupting user interaction.
- **Micro-Animations & Polish**: Staggered notification drawer card entrances, pulsating preview dots, bell hover rings, and emoji reaction jumps.

---

## 19. Assumptions

1. **First-User Bootstrap**: In development environments, the first registered user is automatically designated as an Administrator to simplify testing.
2. **Single Organization**: The current release assumes single-tenant operation (all changelogs belong to a single organization).
3. **Timezones**: All timestamps are calculated, stored, and verified in UTC (`datetime.now(timezone.utc)`).

---

## 20. Limitations

1. **Local File Storage**: The default image storage pipeline saves files to the local disk (`uploads/`). Multi-instance cloud deployments behind load balancers should utilize an object store (e.g., AWS S3, Cloudflare R2, Google Cloud Storage).
2. **Email Delivery**: The password reset simulation outputs tokens directly in the API response in development mode rather than sending physical SMTP emails.

---

## 21. Future Improvements

- [ ] **Multi-Tenant Workspaces**: Support multiple distinct products/projects with custom domains per tenant.
- [ ] **Email & Slack Digest Webhooks**: Automatically broadcast newly published updates to customer Slack channels or email subscribers.
- [ ] **Cloud Object Storage Adapter**: Add native S3 / Cloudflare R2 / GCS drivers for distributed file uploads.
- [ ] **Embeddable Script Tag**: Provide a standalone `<script>` widget that can be dropped into any external website.
- [ ] **User Comments & Threads**: Enable two-way discussion on product updates with moderation controls.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
