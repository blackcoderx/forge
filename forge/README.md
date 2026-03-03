# Forge — Frontend

Astro SSR frontend for the Forge hackathon platform. Deploys to Netlify.

## Stack

- **Framework:** Astro 5 (SSR, `@astrojs/netlify` adapter)
- **Styling:** Plain CSS — brutalist + minimalist design system
- **Font:** JetBrains Mono (Google Fonts)
- **Auth:** JWT via `httpOnly` cookies, validated in Astro middleware
- **API:** Proxies to FastAPI backend via `API_URL` env var

## Project Structure

```
forge/
├── public/
│   └── favicon.svg
├── src/
│   ├── styles/
│   │   └── global.css              # design tokens, component primitives
│   ├── layouts/
│   │   └── Layout.astro            # base layout (header, footer, nav modes)
│   ├── middleware/
│   │   └── index.ts                # JWT route guards (participant / judge / admin)
│   └── pages/
│       ├── index.astro             # / landing page
│       ├── login.astro             # /login participant login
│       ├── hackathons/
│       │   ├── index.astro         # /hackathons list + filter
│       │   └── [id].astro          # /hackathons/[id] detail + event code unlock + cred reveal
│       ├── judge/
│       │   ├── login.astro         # /judge/login
│       │   ├── index.astro         # /judge hackathon list
│       │   └── [hackathon_id]/
│       │       ├── index.astro     # /judge/[id] team list + scoring status
│       │       └── [team_id].astro # /judge/[id]/[tid] scoring form
│       └── api/
│           ├── auth/
│           │   ├── login.ts        # POST /api/auth/login → sets JWT cookie
│           │   └── logout.ts       # GET  /api/auth/logout → clears cookies
│           ├── hackathons/[id]/
│           │   └── unlock.ts       # POST proxy → FastAPI unlock endpoint
│           └── scores/
│               └── [team_id].ts    # GET/POST/PUT proxy → FastAPI scores
├── .env                            # local env (copy from .env.example)
├── .env.example
├── astro.config.mjs
└── package.json
```

## Routes

### Public
| Route | Description |
|-------|-------------|
| `/` | Landing page — hero, Build/Deploy/Compete sections, CTA |
| `/login` | Participant login |
| `/judge/login` | Judge login |

### Participant (requires participant JWT)
| Route | Description |
|-------|-------------|
| `/hackathons` | Hackathon list with Current / Upcoming / Ended filter |
| `/hackathons/[id]` | Hackathon detail, event code entry, Langflow credential reveal |

### Judge (requires judge JWT)
| Route | Description |
|-------|-------------|
| `/judge` | Hackathon list |
| `/judge/[hackathon_id]` | Team list with scoring status per team |
| `/judge/[hackathon_id]/[team_id]` | Scoring form — 4 criteria (1–10), live total, comments |

### Admin (requires admin JWT) — pages pending
| Route | Description |
|-------|-------------|
| `/admin` | Dashboard — stats overview |
| `/admin/hackathons` | List / create / edit hackathons |
| `/admin/hackathons/[id]/teams` | List / create / edit teams |
| `/admin/judges` | List / create judges |

## Design System

Defined in `src/styles/global.css`.

**Colors**
```css
--color-bg:       #ffffff
--color-surface:  #000000
--color-accent:   #FF6B00
--color-text:     #000000
--color-text-inv: #ffffff
--color-border:   #000000
--color-error:    #ff0000
```

**Rules**
- No border-radius anywhere — squared corners throughout
- Hard offset box shadow: `4px 4px 0px #000000`
- All text in JetBrains Mono
- Orange is the only accent color

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_URL` | FastAPI backend base URL | `http://localhost:8000` |

Copy `.env.example` to `.env` before running locally.

## Commands

Run from this directory (`forge/`):

| Command | Action |
|---------|--------|
| `npm install` | Install dependencies |
| `npm run dev` | Start dev server at `localhost:4321` |
| `npm run build` | Build for production to `./dist/` |
| `npm run preview` | Preview production build locally |

## Auth Flow

1. User submits login form → `POST /api/auth/login` (Astro API route)
2. Astro route forwards credentials to FastAPI `/api/auth/login`
3. On success: JWT stored as `httpOnly` cookie (`forge_token`), role in `forge_role`
4. Astro middleware checks cookies on every protected route
5. Wrong role → redirected to their own portal home
6. No token → redirected to appropriate login page
7. Logout: `GET /api/auth/logout` clears both cookies

## What's Next

- [ ] Admin portal pages (`/admin/*`)
- [ ] FastAPI backend (`../forge-api/`)
- [ ] Langflow API integration (judge portal project data)
- [ ] Leaderboard page (`/judge/[hackathon_id]/leaderboard`)
- [ ] Deploy: push to Netlify, set `API_URL` to Railway backend URL
