# Forge API

FastAPI backend for the Forge hackathon platform. Deploys to Railway.

## Stack

- **Framework:** FastAPI
- **Package manager:** uv
- **Database:** SQLite (dev/event) → PostgreSQL (post-event)
- **ORM:** SQLAlchemy 2.0
- **Auth:** JWT via `python-jose` + `bcrypt` password hashing
- **Encryption:** Fernet (from `cryptography`) for Langflow credentials at rest

## Project Structure

```
forge-api/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration, DB init on startup
│   ├── core/
│   │   ├── config.py        # Settings loaded from .env via pydantic-settings
│   │   ├── security.py      # hash_password, verify_password, JWT encode/decode, Fernet encrypt/decrypt
│   │   └── deps.py          # FastAPI dependencies: get_current_participant/judge/admin
│   ├── db/
│   │   ├── session.py       # SQLAlchemy engine, SessionLocal, Base, get_db dependency
│   │   └── init_db.py       # create_all — called on startup, run directly to reset schema
│   ├── models/
│   │   ├── user.py          # User (participant | judge | admin)
│   │   ├── hackathon.py     # Hackathon + computed status property
│   │   ├── team.py          # Team (linked to User + Hackathon, holds Langflow creds)
│   │   ├── hackathon_access.py  # Audit log of event code unlocks
│   │   └── score.py         # Score (4 criteria × 1-10, total computed as property)
│   ├── schemas/
│   │   ├── auth.py          # LoginRequest, TokenResponse
│   │   ├── hackathon.py     # HackathonCreate/Update/Out/AdminOut
│   │   ├── team.py          # TeamCreate/Update/Out, UnlockRequest/Response
│   │   ├── score.py         # ScoreCreate/Update/Out, LeaderboardEntry
│   │   └── user.py          # UserCreate, UserOut
│   └── routers/
│       ├── auth.py          # POST /api/auth/login
│       ├── hackathons.py    # Participant list/detail + Admin CRUD
│       ├── teams.py         # Participant unlock + Admin team CRUD
│       ├── scores.py        # Judge GET/POST/PUT score + leaderboard
│       └── admin.py         # Admin stats + judge CRUD
├── seed.py                  # Populate DB with test data for local dev
├── pyproject.toml
├── .env                     # Local env vars (gitignored)
└── .env.example
```

## Environment Variables

Copy `.env.example` to `.env` before running.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./forge.db` |
| `JWT_SECRET` | Secret key for signing JWTs — **change before deploy** | `change-me` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_HOURS` | Token lifetime in hours | `12` |
| `FERNET_KEY` | Key for encrypting Langflow passwords at rest | _(empty = plaintext)_ |
| `FRONTEND_URL` | Allowed CORS origin | `http://localhost:4321` |

**Generate a Fernet key:**
```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Commands

Run from `forge-api/`:

| Command | Action |
|---------|--------|
| `uv run uvicorn app.main:app --reload` | Start dev server at `localhost:8000` |
| `uv run python seed.py` | Seed DB with test accounts and hackathon |
| `uv run python -m app.db.init_db` | Re-create all tables (destructive) |

## Running Locally

```bash
cd backend/forge-api

# Install dependencies
uv sync

# Create .env
cp .env.example .env
# Edit .env — set JWT_SECRET at minimum

# Seed the database
uv run python seed.py

# Start the server
uv run uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

## API Reference

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | — | Login for any role. Returns JWT. |

**Request body:**
```json
{ "username": "team_alpha", "password": "alpha123", "role": "participant" }
```
`role` must be one of `participant`, `judge`, `admin`. Returns 403 if the account exists but has a different role.

---

### Hackathons

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/hackathons?status=current` | participant | List hackathons filtered by status (`current` / `upcoming` / `ended`) |
| GET | `/api/hackathons/{id}` | participant | Get hackathon detail |
| GET | `/api/hackathons/admin/all` | admin | List all hackathons (includes event code) |
| POST | `/api/hackathons` | admin | Create hackathon |
| PUT | `/api/hackathons/{id}` | admin | Update hackathon |
| DELETE | `/api/hackathons/{id}` | admin | Delete hackathon (cascades teams + scores) |

**Hackathon status** is computed from `start_at` / `end_at` relative to current UTC time — not stored in the DB.

---

### Teams

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/hackathons/{id}/unlock` | participant | Validate event code → return Langflow credentials |
| GET | `/api/hackathons/{id}/teams` | admin | List teams for a hackathon |
| POST | `/api/hackathons/{id}/teams` | admin | Create team (also creates portal User account) |
| GET | `/api/hackathons/{id}/teams/{tid}` | admin | Get team detail |
| PUT | `/api/hackathons/{id}/teams/{tid}` | admin | Update team / rotate passwords |
| DELETE | `/api/hackathons/{id}/teams/{tid}` | admin | Delete team |

**Unlock flow:**
1. Participant POSTs their event code
2. Backend validates it against `hackathon.event_code` (case-insensitive)
3. Looks up the `Team` linked to the requesting user
4. Decrypts and returns `langflow_username`, `langflow_password`, `langflow_url`
5. Logs the unlock in `HackathonAccess`

---

### Scores

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/scores/{team_id}?hackathon_id=1` | judge / admin | Get this judge's score for a team (null if not yet scored) |
| POST | `/api/scores/{team_id}` | judge | Submit score |
| PUT | `/api/scores/{team_id}` | judge | Update existing score |
| GET | `/api/hackathons/{id}/leaderboard` | judge / admin | Teams ranked by average total score across all judges |

**Scoring criteria** — each 1–10:
- `innovation` — novelty and creativity
- `execution` — technical quality and functionality
- `impact` — usefulness and real-world applicability
- `presentation` — clarity of communication

`total` is the sum of the four criteria (max 40). Leaderboard averages totals across all judges.

---

### Admin

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/admin/stats` | admin | Dashboard stats (teams, hackathons, scored/unscored) |
| GET | `/api/admin/judges` | admin | List all judge accounts |
| POST | `/api/admin/judges` | admin | Create judge account |
| PUT | `/api/admin/judges/{id}` | admin | Update judge credentials |
| DELETE | `/api/admin/judges/{id}` | admin | Delete judge account |

---

## Data Models

```
User ──────────────────────────────────────────────────────────
  id, username (unique), hashed_password, role, created_at
  role: "participant" | "judge" | "admin"

Hackathon ─────────────────────────────────────────────────────
  id, name, description, rules, theme
  start_at, end_at
  event_code                    ← participants enter this at the event
  langflow_url
  langflow_admin_username
  langflow_admin_password       ← Fernet encrypted

Team ──────────────────────────────────────────────────────────
  id, name
  hackathon_id → Hackathon
  user_id → User                ← the team's portal login account
  langflow_username
  langflow_password             ← Fernet encrypted

HackathonAccess ───────────────────────────────────────────────
  id, user_id, hackathon_id, unlocked_at
  (audit log of successful event code unlocks)

Score ─────────────────────────────────────────────────────────
  id, hackathon_id, team_id, judge_id
  innovation, execution, impact, presentation  (1-10 each)
  comments, scored_at
  total → computed property (sum of 4 criteria)
  unique constraint: one score per (team, judge)
```

## Test Accounts (after seeding)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Judge | `judge01` | `judge1pass` |
| Judge | `judge02` | `judge2pass` |
| Participant | `team_alpha` | `alpha123` |
| Participant | `team_beta` | `beta123` |
| Participant | `team_gamma` | `gamma123` |

Event code for the test hackathon: **`FORGE2025`**

## Known Issues / Deferred

- **Alembic migrations** — not configured yet. Schema is managed via `Base.metadata.create_all()` on startup. Swap to Alembic before migrating to PostgreSQL.
- **Langflow integration** — `/api/hackathons/{id}/submissions` (fetch team projects from Langflow API) is planned but not yet implemented. Judge portal shows team stubs until this is wired up.
- **passlib removed** — `passlib[bcrypt]` is listed in `pyproject.toml` (installed transitively) but is not used. Password hashing uses `bcrypt` directly due to a compatibility issue with `bcrypt >= 5.x`.

## Deployment (Railway)

1. Push `backend/forge-api/` to a Railway service
2. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set environment variables in Railway dashboard:
   - `DATABASE_URL` — Railway PostgreSQL connection string
   - `JWT_SECRET` — long random string
   - `FERNET_KEY` — generate with the command above
   - `FRONTEND_URL` — your Netlify domain (e.g. `https://forge.netlify.app`)
4. Run seed script once after first deploy (or use the admin portal to create data)
