# Forge — Hackathon Platform

> A platform for hosting AI hackathons, starting with the **Studentrepreneur AI Hackathon** (live in 2 days).

---

## Product Brief

**Core value proposition:** Forge gives hackathon organizers a branded portal to gate access, distribute per-team Langflow credentials, and send participants directly into a self-hosted AI building environment.

**Riskiest assumptions:**
- Event-day credential flow (event code → team Langflow creds) must be zero-friction
- Langflow API exposes enough data (flows/projects per team) for judges to evaluate without a separate submission form
- Self-hosted Langflow is stable and accessible from the portal redirect

**Out of scope (for now):**
- Team self-formation / matchmaking
- Real-time leaderboards
- Payment / ticketing
- Multi-tenant organizer self-service

---

## Confirmed Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend | Astro (SSR, Netlify adapter) | User choice; deploys to Netlify |
| Backend | FastAPI + Railway | User choice; fast to prototype |
| Python package manager | uv | User choice; fast, modern |
| Database | SQLite → PostgreSQL | Zero-ops MVP, swap post-event |
| Auth | JWT (12h expiry) | Stateless, no OAuth complexity |
| Langflow creds | Per-team, unique | Each team has their own Langflow login |
| Langflow cred storage | Fernet-encrypted | Encrypt at rest even for MVP |
| Submissions | Pulled from Langflow API | No participant submission form needed |
| Langflow integration | Deferred to Phase 2 | API shape confirmed later |
| Admin portal | Full UI (create teams + hackathons) | Admin creates teams one by one |
| Deployment | Netlify (Astro) + Railway (FastAPI) | User choice |
| Leaderboard visibility | Judge + Admin only during event | Public after organizer announces |
| Judge scoring model | Multi-judge, scores averaged | Leaderboard shows team average across all judges |

---

## Design System

**Font:** JetBrains Mono — all weights, all styles
```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap" rel="stylesheet">
```

**Style:** Brutalism + Minimalism
- Hard borders (2–4px solid black or orange), no border-radius anywhere
- Heavy typographic hierarchy — oversized mono headlines
- Hard offset box shadows only: `4px 4px 0px #000000`
- No gradients, no soft shadows, no rounded corners
- Stark white/black backgrounds; orange is the single accent color
- Generous negative space balances the brutalism

**Color Palette**
```css
--color-bg:       #FFFFFF;   /* primary background */
--color-surface:  #000000;   /* nav, inverted cards, footer */
--color-accent:   #FF6B00;   /* CTAs, highlights, active states, badges */
--color-text:     #000000;
--color-text-inv: #FFFFFF;
--color-border:   #000000;
--color-error:    #FF0000;
```

**Component Rules**
- Buttons: solid fill, 2px border, no radius, `4px 4px 0 #000` shadow, lift on hover
- Cards: bordered box, no radius, optional offset shadow
- Inputs: 2px solid border, no radius, orange outline on focus
- Nav: black bg, white links, orange on active/hover
- Badges (status): uppercase, bordered, no radius, small font

---

## Architecture Overview

```
Browser
  └── Astro SSR (Netlify)
        ├── Public         → /, /login, /judge/login, /admin/login
        ├── Participant    → /hackathons, /hackathons/[id]
        ├── Judge          → /judge, /judge/[team_id]
        └── Admin          → /admin, /admin/hackathons/*, /admin/teams/*, /admin/judges/*

FastAPI (Railway)
  ├── /api/auth            → login for all roles (role field in body)
  ├── /api/hackathons      → CRUD (admin), list + detail (participant)
  ├── /api/teams           → CRUD (admin), unlock creds (participant)
  ├── /api/langflow        → Proxy Langflow API → fetch team projects for judging
  ├── /api/scores          → Judge scoring CRUD
  └── /api/admin           → Stats, judge management

Self-hosted Langflow
  └── FastAPI fetches project data using stored admin Langflow creds
  └── Participants redirect to Langflow URL directly after cred reveal

SQLite (dev + event day) → PostgreSQL (post-event)
```

---

## Routes & Pages

### Public (no auth)

| Route | Page |
|-------|------|
| `/` | Landing page |
| `/login` | Participant login |
| `/judge/login` | Judge login |
| `/admin/login` | Admin login |

### Participant Portal (participant JWT)

| Route | Page |
|-------|------|
| `/hackathons` | Hackathon list — filter: Current / Upcoming / Ended |
| `/hackathons/[id]` | Hackathon detail — event code → reveal team Langflow creds + redirect |

### Judge Portal (judge JWT)

| Route | Page |
|-------|------|
| `/judge` | Hackathon list — same filter pattern as participant (Current/Upcoming/Ended) |
| `/judge/[hackathon_id]` | Team list for that hackathon — scoring status per team |
| `/judge/[hackathon_id]/[team_id]` | Score team — project detail from Langflow + scoring form |

### Admin Portal (admin JWT)

| Route | Page |
|-------|------|
| `/admin` | Dashboard — stats (teams, hackathons, scored/unscored) |
| `/admin/hackathons` | List hackathons |
| `/admin/hackathons/new` | Create hackathon |
| `/admin/hackathons/[id]` | Edit hackathon |
| `/admin/hackathons/[id]/teams` | List teams for a hackathon |
| `/admin/hackathons/[id]/teams/new` | Create team (portal + Langflow creds) |
| `/admin/hackathons/[id]/teams/[tid]` | Edit / view team |
| `/admin/judges` | List judges |
| `/admin/judges/new` | Create judge account |

---

## Page Specs

### `/` Landing Page

**Header — sticky, black bg**
- Left: `FORGE` (bold mono wordmark)
- Right: `HACKATHONS` nav link + `START HACKING →` orange button

**Hero — white bg, full viewport height**
```
// AI HACKATHON PLATFORM          ← small caps eyebrow, orange

BUILD.
DEPLOY.
COMPETE.                          ← massive stacked type, each word own line

Ship AI agents in hours.
Compete with the best.            ← subheadline, lighter weight

[ START HACKING → ]               ← large orange bordered button
```

**Three Sections — alternating black / white panels, full width**

| # | Title | Body |
|---|-------|------|
| 1 | BUILD | Spin up AI agents and bots using Langflow. No setup. No boilerplate. Just ideas. |
| 2 | DEPLOY | Your agent runs live in our environment. Ship in minutes, iterate in seconds. |
| 3 | COMPETE | Judges review your live project. The best agent wins. |

Each section: large number (01/02/03) + section title + body + decorative border rule.

**CTA Banner — orange bg**
```
READY TO HACK?
[ START HACKING → ]    ← black bg, white text button (inverted)
```

**Footer — black bg, white text**
```
FORGE © 2025
```

---

### `/login` — Participant Login

- Centered black card on white bg
- Fields: `USERNAME` / `PASSWORD` (mono labels, full-width inputs, 2px border)
- `LOGIN →` button (orange, full-width)
- Error state: red-bordered inline message — `"Invalid credentials. Check your event sheet."`
- Link at bottom: `JUDGE? →` links to `/judge/login`

---

### `/hackathons` — Hackathon List

- Filter tab bar: `[CURRENT]  [UPCOMING]  [ENDED]` — active tab gets orange bg
- Grid of cards (bordered, offset shadow):
  - Hackathon name (bold), date range, status badge
  - Short description
  - `ENTER →` button

---

### `/hackathons/[id]` — Hackathon Detail + Cred Reveal

**Step 1 — Info panel**
- Name, theme, rules (markdown rendered in mono), timeline

**Step 2 — Event Code Unlock**
```
ENTER YOUR EVENT CODE
[ __________________ ]  [ UNLOCK → ]
```
- On valid code: slide in credentials reveal panel
```
YOUR LANGFLOW CREDENTIALS
USERNAME  team_xyz          [COPY]
PASSWORD  ••••••••          [COPY]

[ OPEN LANGFLOW → ]
```
- Langflow URL opens in new tab
- On invalid code: red border + error message

---

### `/judge` — Hackathon List (Judge)

Mirrors the participant hackathon list — same filter pattern, same card layout.
- Filter: `[CURRENT]  [UPCOMING]  [ENDED]`
- Cards: hackathon name, dates, status badge
- Button: `ENTER →` → `/judge/[hackathon_id]`

---

### `/judge/[hackathon_id]` — Team List + Scoring Status

- Header: hackathon name + `JUDGE PORTAL` badge (orange)
- Brutalist bordered table:

| TEAM | STATUS | MY SCORE | ACTION |
|------|--------|----------|--------|
| Team A | SCORED | 36/40 | VIEW → |
| Team B | PENDING | — | SCORE → |

- `LEADERBOARD →` button (shows averaged scores across all judges)

---

### `/judge/[hackathon_id]/[team_id]` — Score Team

- Team name + project info from Langflow (description, flow link)
- `OPEN IN LANGFLOW →` button
- Scoring form:
  - Innovation (1–10)
  - Technical Execution (1–10)
  - Impact / Use Case (1–10)
  - Presentation (1–10)
- Comments textarea
- `SUBMIT SCORE →` button (orange)
- If already scored: shows existing values, `UPDATE SCORE →` button

---

### `/admin` — Dashboard

Stats row: `TOTAL TEAMS` | `ACTIVE HACKATHONS` | `SCORED` | `UNSCORED`

Quick-link cards to all admin sections.

---

### `/admin/hackathons/new` (and edit)

Fields:
- Name, Description, Rules (markdown textarea), Theme
- Start date/time, End date/time
- Event Code (organizer-defined, given to participants at event)
- Langflow Base URL (for this hackathon's instance)
- Langflow Admin Username + Password (used by FastAPI to pull project data)

---

### `/admin/hackathons/[id]/teams/new` (and edit)

Fields:
- Team Name
- Portal Username + Password (Forge login credentials)
- Langflow Username + Password (this team's Langflow credentials)

---

### `/admin/judges/new` (and edit)

Fields:
- Judge Name
- Username + Password (Forge judge login)

---

## Backend — API Spec (FastAPI)

### Auth
```
POST /api/auth/login
  body: { username, password, role: "participant" | "judge" | "admin" }
  returns: { access_token, token_type, role }
```

### Hackathons
```
GET  /api/hackathons?status=current|upcoming|ended     (participant)
GET  /api/hackathons/{id}                              (participant)
POST /api/hackathons                                   (admin)
PUT  /api/hackathons/{id}                              (admin)
DEL  /api/hackathons/{id}                              (admin)
```

### Teams + Credential Unlock
```
POST /api/hackathons/{id}/unlock
  auth: participant JWT
  body: { event_code }
  returns: { langflow_username, langflow_password, langflow_url }

GET  /api/hackathons/{id}/teams          (admin)
POST /api/hackathons/{id}/teams          (admin)
PUT  /api/hackathons/{id}/teams/{tid}    (admin)
DEL  /api/hackathons/{id}/teams/{tid}    (admin)
```

### Langflow Integration (Submissions for Judging) — Phase 2
```
GET /api/hackathons/{id}/submissions
  auth: judge JWT
  → FastAPI authenticates to Langflow API using hackathon admin creds
  → Fetches flows/projects associated with each team
  returns: [{ team_id, team_name, project_name, description, flow_url }]

GET /api/hackathons/{id}/submissions/{team_id}
  auth: judge JWT
  returns: { full project detail from Langflow }

NOTE: Until Langflow integration is built, judge portal shows team names only.
      Project detail fields will be stubs ("Pending Langflow sync").
```

### Scoring
```
GET  /api/scores/{team_id}              (judge)
POST /api/scores/{team_id}              (judge)
  body: { innovation, execution, impact, presentation, comments }
PUT  /api/scores/{team_id}              (judge — update)

GET  /api/hackathons/{id}/leaderboard   (admin + judge)
  returns: teams ranked by total average score
```

### Admin — Judges + Stats
```
GET  /api/admin/judges
POST /api/admin/judges
PUT  /api/admin/judges/{id}
DEL  /api/admin/judges/{id}

GET  /api/admin/stats
  returns: { total_teams, active_hackathons, scored, unscored }
```

---

## Database Models (SQLAlchemy)

```python
User
  id, username, hashed_password
  role: "participant" | "judge" | "admin"
  created_at

Hackathon
  id, name, description, rules (text), theme
  start_at, end_at
  event_code                            # given to participants at the event
  langflow_url                          # base URL of Langflow instance
  langflow_admin_username               # used by FastAPI to fetch project data
  langflow_admin_password               # store encrypted
  created_at

Team
  id, hackathon_id, name
  user_id → FK User (role=participant)  # the portal login for this team
  langflow_username                     # team's Langflow login
  langflow_password                     # store encrypted
  created_at

HackathonAccess
  id, user_id, hackathon_id, unlocked_at   # audit log of event code unlocks

Score
  id, hackathon_id, team_id, judge_id
  innovation    (1–10)
  execution     (1–10)
  impact        (1–10)
  presentation  (1–10)
  total         (computed: sum or average)
  comments
  scored_at
```

---

## MVP Scope (2-Day Sprint)

### Must Ship (event day)
- [ ] Landing page — full design, hero, 3 sections, CTA
- [ ] Participant login → hackathon list (with filter) → hackathon detail
- [ ] Event code unlock → team Langflow cred reveal + redirect
- [ ] Judge login → submission list (from Langflow API)
- [ ] Judge scoring form + score submission
- [ ] Admin login + create hackathon + create teams + create judges

### Ship If Time Allows
- [ ] Admin edit / delete hackathon and teams
- [ ] Leaderboard view (admin + judge)
- [ ] Score editing for judges

### Post-Event
- [ ] Swap SQLite → PostgreSQL on Railway
- [ ] Public results / leaderboard page
- [ ] Export scores to CSV
- [ ] Multi-hackathon admin UX improvements

---

## Phased Roadmap

### Phase 0 — Scaffold (Day 1, AM)
- [ ] `forge-web/` — Astro SSR, Netlify adapter, global CSS (tokens + brutalist base)
- [ ] `forge-api/` — FastAPI via `uv init`, dependencies: fastapi, uvicorn, sqlalchemy, alembic, python-jose[cryptography], passlib[bcrypt], cryptography (Fernet)
- [ ] Alembic migrations for all models
- [ ] Fernet key in env var `FERNET_KEY` — used to encrypt/decrypt stored Langflow passwords
- [ ] Seed script: 1 hackathon, 2 teams, 1 judge, 1 admin
- [ ] `/api/auth/login` working, JWT verified in Astro middleware
- [ ] CORS: allow Astro dev server origin

**uv workflow:**
```bash
uv init forge-api
cd forge-api
uv add fastapi uvicorn sqlalchemy alembic "python-jose[cryptography]" "passlib[bcrypt]" cryptography
uv run uvicorn main:app --reload
```

**Gate:** Participant logs in → sees `/hackathons`.

### Phase 1 — Core Participant Flow (Day 1, PM)
- [ ] Landing page — hero, 3 sections, CTA, header, footer (full design)
- [ ] `/login` page
- [ ] `/hackathons` list + filter tabs
- [ ] `/hackathons/[id]` detail + event code unlock + cred reveal + Langflow redirect

**Gate:** Full participant flow end-to-end, locally.

### Phase 2 — Judge + Admin (Day 2, AM)
- [ ] Langflow API client in FastAPI (GET flows per team)
- [ ] `/judge` submission list — real data from Langflow
- [ ] `/judge/[team_id]` scoring form + submit
- [ ] `/admin` dashboard + stats
- [ ] `/admin/hackathons` create + view
- [ ] `/admin/hackathons/[id]/teams` create + view
- [ ] `/admin/judges` create + view

**Gate:** Judge can score a team. Admin can create a hackathon and team.

### Phase 3 — Polish + Deploy (Day 2, PM)
- [ ] Error states: bad login, bad event code, Langflow API failure
- [ ] Mobile responsive pass
- [ ] Load real event data via admin portal
- [ ] FastAPI → Railway (set JWT_SECRET, DB path, Langflow URL in env vars)
- [ ] Astro → Netlify (set API base URL env var)
- [ ] CORS locked to production Netlify domain
- [ ] Full smoke test: participant, judge, admin flows on prod

**Gate:** Everything works on live production URLs.

---

## Risk Register

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Langflow API doesn't expose per-team project data cleanly | M | H | Explore Langflow API before Phase 2; have manual flow-link entry as fallback |
| Not enough time — admin portal is last | M | M | Seed script fallback: pre-load data via Alembic seed, skip admin UI if needed |
| Langflow down during event | M | H | Pre-test before event; have printed backup creds sheet |
| SQLite concurrent writes at event peak | L | M | Mostly reads; acceptable for <200 users |
| JWT secret lost on Railway redeploy | M | H | Pin to Railway env var; document immediately |
| Team Langflow creds exposed client-side | L | H | Reveal once per session, HTTPS only, no localStorage persistence |

---

## Open Questions (resolve before Phase 2)

1. **Langflow API shape** — When ready to integrate, share the Langflow base URL and whether it uses API key or session token auth. FastAPI will use hackathon-level admin creds to query per-team flows.
