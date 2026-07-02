# Peer Learn — Backend API Reference (for AI Frontend Generation)

> **Purpose of this document:** This is a complete specification of the FastAPI backend for the "Peer Learn" platform (a School21 peer-to-peer learning system). Use this document to build a frontend (React + TypeScript) that connects to this backend correctly. Every endpoint, request body, response shape, authentication rule, and business rule is described here. **Do not modify the backend — only build the frontend to match these contracts exactly.**

---

## 1. Overview

**Peer Learn** is a peer-to-peer learning platform for School21 students. Students:
- Log in with their **School21 credentials** (linked to a Telegram account via OTP).
- Create **slots** (time windows where they can teach a project they've finished).
- Search and **book** slots to learn projects they're currently working on.
- Run live sessions (start → finish), earn **XP**, **Peer Points**, and **Peer Coins**.
- Leave **reviews** (positive/negative) for each other.
- Compete on **leaderboards** (most XP, most taught, most learned).
- Receive **notifications** in real time via WebSocket.

The UI language is **Uzbek** (uz-UZ). All user-facing text should be in Uzbek.

---

## 2. Tech Stack (backend — for context only)

- **Framework:** FastAPI (Python), async
- **Auth:** JWT (access + refresh tokens), HS256
- **DB:** PostgreSQL (async), Redis (cache + OTP)
- **Real-time:** WebSocket
- **External:** School21 API (login/profile/projects), Telegram Bot (OTP delivery)

---

## 3. Base URLs & Connection

| Item | Value |
|------|-------|
| REST API base | `/api/v1` |
| WebSocket (notifications) | `/ws/slots?token=<access_token>` |
| WebSocket (live slot session) | `/ws/slot/{slot_id}?token=<access_token>` |
| Health check | `GET /health` → `{"status": "ok"}` |
| Dev backend origin | `http://localhost:8000` |
| Dev frontend origin | `http://localhost:5173` |

### Vite dev proxy (required for local dev)

The frontend must proxy `/api` and `/ws` to the backend. Use this in `vite.config.ts`:

```ts
server: {
  port: 5173,
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true },
    '/ws':  { target: 'ws://localhost:8000', ws: true },
  },
}
```

All API requests should use the relative base `/api/v1` (the proxy forwards them). All requests/responses are JSON unless noted.

---

## 4. Authentication

### 4.1 Token model

- On successful login the backend returns an **access_token** and a **refresh_token**.
- Send the access token on every protected request:
  `Authorization: Bearer <access_token>`
- Access token expires in **24 hours**, refresh token in **30 days**.
- Store tokens client-side (e.g. localStorage via a persisted store).

### 4.2 Login flow (two cases)

The login flow has **two possible outcomes** because every account must be linked to Telegram.

**Step 1 — `POST /api/v1/auth/login`**

Request:
```json
{ "login": "school21_login", "password": "user_password" }
```

Response (case A — Telegram already linked → fully logged in):
```json
{
  "status": "ok",
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "onboarding_done": false,
  "temp_token": null,
  "bot_url": null
}
```

Response (case B — Telegram NOT linked → must verify via bot):
```json
{
  "status": "need_telegram",
  "access_token": null,
  "refresh_token": null,
  "token_type": "bearer",
  "onboarding_done": false,
  "temp_token": "abc123...",
  "bot_url": "https://t.me/<bot>?start=abc123..."
}
```

Frontend behavior:
- If `status === "ok"` → save tokens, then navigate to `/onboarding` if `onboarding_done` is false, else `/dashboard`.
- If `status === "need_telegram"` → store `temp_token`, show a screen with a link to `bot_url` ("Open Telegram bot"), and an OTP code input. The user gets a code from the bot.

Errors:
- `401` — wrong login or password (`detail: "Login yoki parol noto'g'ri"`)
- `502` — School21 unreachable
- Rate limit: **5 requests / 15 minutes** per IP.

**Step 2 — `POST /api/v1/auth/verify-code`** (only in case B)

Request:
```json
{ "temp_token": "abc123...", "code": "123456" }
```

Response (success):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "onboarding_done": false
}
```

Errors:
- `400` — invalid/expired temp_token, code not found, or wrong code.
- `409` — this Telegram account is already linked to another user.
- Rate limit: **10 / minute**.

### 4.3 Refresh — `POST /api/v1/auth/refresh`

Request:
```json
{ "refresh_token": "..." }
```
Response: same shape as the `verify-code` success response (new access + refresh).
Use this automatically on a `401` response (axios interceptor): try refresh once, retry the original request; if refresh fails, log out.

### 4.4 Logout — `POST /api/v1/auth/logout`

Requires auth. Returns `204 No Content`. Frontend should clear tokens locally.

### 4.5 Current user — `GET /api/v1/auth/me`

Requires auth. Returns a **UserMe** object (see §6.1).

### 4.6 Unlink Telegram — `POST /api/v1/auth/unlink-telegram`

Requires auth. Body: `{ "password": "school21_password" }`. Confirms School21 password, then unlinks Telegram so the user can re-link with a different account. Rate limit: **3 / hour**.
Response: `{ "status": "ok", "message": "..." }`.

---

## 5. Data Types (shared)

All IDs are **UUID strings**. All datetimes are **ISO 8601 strings (UTC)**, e.g. `"2026-06-16T14:30:00Z"`.

### 5.1 Slot status enum
```
"open" | "booked" | "in_progress" | "completed" | "cancelled" | "absent"
```

### 5.2 Notification types (string `type` field)
```
"slot_booked" | "slot_started" | "slot_completed" | "slot_cancelled"
| "review_received" | "absent_given" | "absent_received" | "system"
```

---

## 6. Schemas (response/request models)

### 6.1 UserMe (full profile of the authenticated user)
```ts
interface UserMe {
  id: string                       // UUID
  telegram_username: string | null
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  campus: string | null
  core_program: string | null
  main_track: string | null
  coalition_name: string | null
  level: number
  xp: number
  // UserMe-only fields:
  school21_login: string
  email: string | null
  current_location: string | null
  peer_points: number
  peer_coins: number
  languages: string[]
  is_admin: boolean
  onboarding_done: boolean
}
```

### 6.2 UserPublic (other users)
Same as UserMe but **without** the UserMe-only fields (no school21_login, email, points, etc.). Fields: `id, telegram_username, first_name, last_name, avatar_url, campus, core_program, main_track, coalition_name, level, xp`.

### 6.3 Slot (SlotOut)
```ts
interface Slot {
  id: string
  reviewer_id: string              // owner / teacher
  reviewee_id: string | null       // student who booked
  reviewer_project: string         // project the teacher offers
  reviewee_project: string | null  // project the student is learning
  start_time: string               // ISO
  end_time: string                 // ISO
  actual_start: string | null
  actual_end: string | null
  duration_minutes: number | null
  status: SlotStatus
  is_online: boolean
  campus: string
}
```

### 6.4 SlotSearchResult (anonymous search result)
```ts
interface SlotSearchResult {
  id: string
  start_time: string
  end_time: string
  campus: string
  is_online: boolean
}
```

### 6.5 Review
```ts
interface Review {
  id: string
  slot_id: string
  author_id: string
  target_id: string
  is_positive: boolean
  comment: string | null
}
```

### 6.6 Notification
```ts
interface Notification {
  id: string
  type: string
  title: string | null
  body: string | null
  slot_id: string | null
  is_read: boolean
  created_at: string
}
```

### 6.7 LeaderboardEntry
```ts
interface LeaderboardEntry {
  rank: number
  user_id: string
  first_name: string | null
  last_name: string | null
  value: number   // XP total, or taught count, or learned count
}
```

---

## 7. Endpoints

> All endpoints below require `Authorization: Bearer <access_token>` **unless explicitly marked Public**. All paths are prefixed with `/api/v1`.

### 7.1 Auth — (see §4 for full flow)
| Method | Path | Auth | Body | Response |
|--------|------|------|------|----------|
| POST | `/auth/login` | Public | `{login, password}` | LoginResponse (§4.2) |
| POST | `/auth/verify-code` | Public | `{temp_token, code}` | TokenResponse |
| POST | `/auth/refresh` | Public | `{refresh_token}` | TokenResponse |
| POST | `/auth/logout` | Yes | — | 204 |
| POST | `/auth/unlink-telegram` | Yes | `{password}` | `{status, message}` |
| GET | `/auth/me` | Yes | — | UserMe |

### 7.2 Onboarding
After first login, if `onboarding_done` is false, route the user through onboarding (2 steps: confirm track, then select languages).

| Method | Path | Body | Response |
|--------|------|------|----------|
| GET | `/onboarding/track` | — | `{core_program, main_track}` |
| POST | `/onboarding/confirm` | `{main_track: string}` | `{core_program, main_track}` |
| POST | `/onboarding/languages` | `{languages: string[]}` (min 1) | `{onboarding_done, main_track, languages}` |
| GET | `/onboarding/status` | — | `{onboarding_done, main_track, languages}` |

`POST /onboarding/languages` sets `onboarding_done = true`. After it succeeds, navigate to `/dashboard`.

Track options (suggested UI list): `Web`, `Mobile`, `GameDev`, `DataScience`, `DevOps`, `Blockchain`.
Language options (suggested): `O'zbek`, `Русский`, `English`, `Français`, `Deutsch`, `Español`, `Türkçe`, `العربية`, `فارسی`, `中文`.

### 7.3 Dashboard
`GET /dashboard/` → returns:
```ts
{
  user: UserMe,
  xp_to_next_level: number,
  active_slots: Slot[],          // booked + in_progress slots involving this user
  unread_notifications: number
}
```
Use this as the home screen data source. Note: this endpoint also refreshes the user's live School21 location on each call.

### 7.4 Slots
| Method | Path | Query / Body | Response | Notes |
|--------|------|------|----------|-------|
| GET | `/slots/` | query: `status?`, `date?` (YYYY-MM-DD) | `Slot[]` | Slots where user is reviewer or reviewee |
| POST | `/slots/` | `{reviewer_project, start_time, end_time, is_online}` | `Slot` (201) | Create a teaching slot |
| GET | `/slots/{id}` | — | `Slot` | |
| DELETE | `/slots/{id}` | body: `{reason?}` | `Slot` | Cancel (reviewer only) |
| POST | `/slots/{id}/book` | `{reviewee_project?}` | `Slot` | Book an open slot |
| POST | `/slots/{id}/start` | — | `Slot` | Mark your side as started |
| POST | `/slots/{id}/finish` | — | `Slot` | Mark your side as finished |
| POST | `/slots/{id}/absent` | — | `Slot` | Mark the other party absent |
| GET | `/slots/search` | query: `project` (required) | `SlotSearchResult[]` | Find open slots matching a project |
| GET | `/slots/my/teachable-projects` | — | `{projects: {title, id}[]}` | Finished (ACCEPTED) projects — used when creating a slot |
| GET | `/slots/my/in-progress-projects` | — | `{projects: {title, id}[]}` | Current (IN_PROGRESS) projects — used when searching |

`start_time`/`end_time` must be ISO datetime strings. Convert from a `datetime-local` input via `new Date(value).toISOString()`.

### 7.5 Reviews
| Method | Path | Body | Response | Notes |
|--------|------|------|----------|-------|
| POST | `/reviews/` | `{slot_id, is_positive, comment?}` | `Review` (201) | Only allowed after slot is `completed`; one review per user per slot |
| GET | `/reviews/my` | — | `Review[]` | Reviews about me |
| GET | `/reviews/user/{user_id}` | — | `Review[]` | Reviews about a specific user |

Errors: `400` if slot not completed; `403` if not a participant; `409` if already reviewed.

### 7.6 Leaderboard
| Method | Path | Query | Response |
|--------|------|------|----------|
| GET | `/leaderboard/most-xp` | — | `LeaderboardEntry[]` |
| GET | `/leaderboard/most-taught` | — | `LeaderboardEntry[]` |
| GET | `/leaderboard/most-learned` | — | `LeaderboardEntry[]` |
| GET | `/leaderboard/history` | `month` (YYYY-MM-DD, required), `category` (`most_xp`\|`most_taught`\|`most_learned`) | `[{rank, user_id, value}]` |

All leaderboards are computed for the **current calendar month**.

### 7.7 Profile
| Method | Path | Body | Response | Notes |
|--------|------|------|----------|-------|
| GET | `/profile/` | — | `{user: UserMe, stats}` | My profile + stats |
| PATCH | `/profile/` | `{first_name?, last_name?, avatar_url?}` | `UserMe` | Update editable fields |
| GET | `/profile/skills` | — | School21 skills object | Read-only skills radar data |
| GET | `/profile/{username}` | — | `UserPublic` | Public profile by school21_login |

`stats` shape:
```ts
{
  positive_reviews: number,
  negative_reviews: number,
  all_reviews: number,
  taught_count: number,
  learned_count: number
}
```

### 7.8 Notifications
| Method | Path | Query | Response | Notes |
|--------|------|------|----------|-------|
| GET | `/notifications/` | `limit?` (≤100, default 20), `offset?` | `Notification[]` | Newest first |
| POST | `/notifications/{id}/read` | — | 204 | Mark one read |
| POST | `/notifications/read-all` | — | 204 | Mark all read |

### 7.9 Settings
| Method | Path | Body | Response |
|--------|------|------|----------|
| GET | `/settings/` | — | `{languages, campus}` |
| PATCH | `/settings/language` | `{language: string}` | `{languages}` |
| PATCH | `/settings/theme` | `{theme: "light" | "dark"}` | `{theme}` (echo; theme is client-side) |

Theme is a client-side preference — persist it locally (light/dark/system). The PATCH is optional confirmation only.

### 7.10 Admin (only if `user.is_admin === true`)
Show an admin section only when `is_admin` is true. Endpoints (all under `/admin`, require admin):
- `GET /admin/users?q&limit&offset` → `UserMe[]`
- `GET /admin/users/{id}` → `UserMe`
- `POST /admin/users/{id}/block` → toggles active, returns `UserMe`
- `DELETE /admin/users/{id}` → 204
- `GET /admin/slots?status&limit&offset` → `Slot[]`
- `POST /admin/slots/{id}/resolve` → `Slot` (refunds reviewee, cancels)
- `DELETE /admin/reviews/{id}` → 204
- `POST /admin/adjust-xp` body `{user_id, amount}` → `UserMe`
- `POST /admin/adjust-points` body `{user_id, points, coins}` → `UserMe`
- `POST /admin/notify` body `{user_id?, title, body}` (no user_id = broadcast) → 202
- `GET /admin/stats` → `{total_users, total_slots, completed_slots, avg_duration_minutes}`

---

## 8. WebSocket (real-time)

### 8.1 Global notifications socket
Connect after login:
```
ws(s)://<host>/ws/slots?token=<access_token>
```
Incoming messages are JSON. Handle these `type` values:
- `{ "type": "slot_update" }` → re-fetch slots + dashboard.
- `{ "type": "notification" }` → re-fetch notifications + dashboard.

Reconnect automatically after ~3s if the socket closes. Choose `wss` when the page is https, else `ws`.

### 8.2 Live slot session socket (optional, for an in-session screen)
```
ws(s)://<host>/ws/slot/{slot_id}?token=<access_token>
```
Client → server events (send as JSON):
- `{ "event": "client.start" }`
- `{ "event": "client.finish" }`
- `{ "event": "client.absent" }`

Server → client events:
- `{ "event": "slot.start", "who": "reviewer"|"reviewee" }`
- `{ "event": "slot.both_started", "reviewer_link": "<t.me/...>", "reviewee_link": "<t.me/...>" }`
- `{ "event": "slot.finish", "who": "..." }`
- `{ "event": "slot.both_finished", "duration_minutes": number }`
- `{ "event": "slot.absent", "by": "<user_id>" }`

A bad/expired token closes the socket with code `4401`.

---

## 9. Business Rules (must reflect in UI logic)

These rules are enforced by the backend. The UI should anticipate them to avoid confusing errors.

1. **Slot lifecycle:** `open → booked → in_progress → completed`. Side branches: `cancelled`, `absent`.
2. **Booking** requires the reviewee to have **≥1 peer point**; booking deducts 1 point. Cannot book your own slot. Slot must be `open`.
3. **Start:** both reviewer and reviewee must call start. The slot only moves to `in_progress` once **both** have started (`actual_start` is set then).
4. **Finish:** only available **15 minutes after** `actual_start`. Both sides must finish; on the second finish the slot becomes `completed`, `duration_minutes` is set, and the reviewer earns **+25 XP**.
5. **Cancel:** only the **reviewer** can cancel, and only before completion. If it was booked, the reviewee's point is refunded.
6. **Absent:** can be marked on `booked`/`in_progress` slots. The absent party loses **15 XP**. Point adjustments depend on who marked whom.
7. **Reviews:** only after `completed`; one review per user per slot; positive or negative + optional comment (max 500 chars suggested).
8. **Campus rule:** slots for the `tashkent` campus must be `is_online = true` (creating an offline Tashkent slot returns `400`).
9. **Roles in a slot:** `reviewer` = teacher (slot owner), `reviewee` = student (booker). Compare `slot.reviewer_id`/`slot.reviewee_id` against the current user's `id` to decide which actions to show.

---

## 10. Error Handling

- Errors return JSON: `{ "detail": "<message>" }` (the message is usually in Uzbek and safe to display).
- Common codes: `400` validation/business rule, `401` unauthenticated (trigger refresh), `403` forbidden, `404` not found, `409` conflict (e.g. slot not open, already reviewed), `422` request body validation, `429` rate limited, `502` School21 upstream error.
- On `401`: attempt one token refresh, then retry; if refresh fails, log out and redirect to `/login`.

---

## 11. Suggested Frontend Architecture (React + TS)

- **HTTP client:** `axios` instance with `baseURL: '/api/v1'`, request interceptor to attach the Bearer token, response interceptor for refresh-on-401 (single-flight; queue concurrent requests during refresh).
- **Server state:** TanStack Query (`@tanstack/react-query`) for all GET endpoints and mutations; invalidate `['slots']`, `['dashboard']`, `['notifications']` after relevant mutations and on WS events.
- **Auth state:** a small persisted store (e.g. Zustand) holding `accessToken`, `refreshToken`, `isAuthenticated`, `onboardingDone`.
- **Routing:** route guards — an Auth guard for protected routes, a Guest guard for `/login`. Redirect to `/onboarding` while `onboarding_done` is false.
- **Pages to build:** Login, Onboarding (track + languages), Dashboard, Slots list, Slot detail, Search peers, Leaderboard, Profile, Public user profile (`/profile/:username`), Review (`/review?slot=<id>`), Notifications, Settings.
- **Layout:** desktop = fixed left sidebar; mobile = bottom tab bar. Dark theme by default.
- **Locale:** all UI text in Uzbek; format dates with `toLocaleString('uz-UZ', ...)`.

---

## 12. Suggested TypeScript Type Definitions (drop-in)

```ts
export type SlotStatus = 'open' | 'booked' | 'in_progress' | 'completed' | 'cancelled' | 'absent'

export interface LoginRequest { login: string; password: string }
export interface LoginResponse {
  status: 'ok' | 'need_telegram'
  access_token?: string
  refresh_token?: string
  token_type: string
  onboarding_done: boolean
  temp_token?: string
  bot_url?: string
}
export interface VerifyCodeRequest { temp_token: string; code: string }
export interface TokenResponse {
  access_token: string; refresh_token: string; token_type: string; onboarding_done: boolean
}

export interface UserPublic {
  id: string; telegram_username?: string | null; first_name?: string | null
  last_name?: string | null; avatar_url?: string | null; campus?: string | null
  core_program?: string | null; main_track?: string | null
  coalition_name?: string | null; level: number; xp: number
}
export interface UserMe extends UserPublic {
  school21_login: string; email?: string | null; current_location?: string | null
  peer_points: number; peer_coins: number; languages: string[]
  is_admin: boolean; onboarding_done: boolean
}

export interface Slot {
  id: string; reviewer_id: string; reviewee_id?: string | null
  reviewer_project: string; reviewee_project?: string | null
  start_time: string; end_time: string
  actual_start?: string | null; actual_end?: string | null
  duration_minutes?: number | null; status: SlotStatus
  is_online: boolean; campus: string
}
export interface SlotCreate { reviewer_project: string; start_time: string; end_time: string; is_online: boolean }
export interface SlotSearchResult { id: string; start_time: string; end_time: string; campus: string; is_online: boolean }

export interface Review { id: string; slot_id: string; author_id: string; target_id: string; is_positive: boolean; comment?: string | null }
export interface ReviewCreate { slot_id: string; is_positive: boolean; comment?: string }

export interface Notification {
  id: string; type: string; title?: string | null; body?: string | null
  slot_id?: string | null; is_read: boolean; created_at: string
}

export interface DashboardResponse { user: UserMe; xp_to_next_level: number; active_slots: Slot[]; unread_notifications: number }

export interface LeaderboardEntry { rank: number; user_id: string; first_name?: string | null; last_name?: string | null; value: number }

export interface OnboardingStatus { onboarding_done: boolean; main_track?: string | null; languages: string[] }
export interface Project { title: string; id?: string }
export interface ProfileStats { positive_reviews: number; negative_reviews: number; all_reviews: number; taught_count: number; learned_count: number }
```

---

## 13. Quick Reference — Endpoint Map

```
PUBLIC
  POST   /api/v1/auth/login
  POST   /api/v1/auth/verify-code
  POST   /api/v1/auth/refresh

AUTH REQUIRED
  POST   /api/v1/auth/logout
  POST   /api/v1/auth/unlink-telegram
  GET    /api/v1/auth/me

  GET    /api/v1/onboarding/track
  POST   /api/v1/onboarding/confirm
  POST   /api/v1/onboarding/languages
  GET    /api/v1/onboarding/status

  GET    /api/v1/dashboard/

  GET    /api/v1/slots/
  POST   /api/v1/slots/
  GET    /api/v1/slots/{id}
  DELETE /api/v1/slots/{id}
  POST   /api/v1/slots/{id}/book
  POST   /api/v1/slots/{id}/start
  POST   /api/v1/slots/{id}/finish
  POST   /api/v1/slots/{id}/absent
  GET    /api/v1/slots/search?project=
  GET    /api/v1/slots/my/teachable-projects
  GET    /api/v1/slots/my/in-progress-projects

  POST   /api/v1/reviews/
  GET    /api/v1/reviews/my
  GET    /api/v1/reviews/user/{user_id}

  GET    /api/v1/leaderboard/most-xp
  GET    /api/v1/leaderboard/most-taught
  GET    /api/v1/leaderboard/most-learned
  GET    /api/v1/leaderboard/history?month=&category=

  GET    /api/v1/profile/
  PATCH  /api/v1/profile/
  GET    /api/v1/profile/skills
  GET    /api/v1/profile/{username}

  GET    /api/v1/notifications/
  POST   /api/v1/notifications/{id}/read
  POST   /api/v1/notifications/read-all

  GET    /api/v1/settings/
  PATCH  /api/v1/settings/language
  PATCH  /api/v1/settings/theme

ADMIN ONLY (is_admin)
  GET    /api/v1/admin/users
  GET    /api/v1/admin/users/{id}
  POST   /api/v1/admin/users/{id}/block
  DELETE /api/v1/admin/users/{id}
  GET    /api/v1/admin/slots
  POST   /api/v1/admin/slots/{id}/resolve
  DELETE /api/v1/admin/reviews/{id}
  POST   /api/v1/admin/adjust-xp
  POST   /api/v1/admin/adjust-points
  POST   /api/v1/admin/notify
  GET    /api/v1/admin/stats

WEBSOCKET
  /ws/slots?token=<access_token>          (global: slot_update, notification)
  /ws/slot/{slot_id}?token=<access_token> (live session events)
```
