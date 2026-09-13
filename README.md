# LaptopSathi AI

An AI-powered laptop recommendation and decision-support platform built on a
**Knowledge Base architecture** (no live scraping) with semantic search,
a hybrid recommendation engine, and explainable AI — designed as a
production-style, resume/portfolio-grade system rather than a toy demo.

```
Knowledge Base (CSV/JSON)
   -> Data Ingestion        (schema validation, dedup)
   -> Data Engineering      (cleaning, normalization, derived features)
   -> Knowledge Database    (SQLite/PostgreSQL via SQLAlchemy)
   -> Feature Store         (Programming/AI-ML/Gaming/... scores)
   -> Semantic Search       (Sentence Transformers + FAISS)
   -> Hybrid Recommendation Engine
   -> Explainable AI
   -> FastAPI Backend
   -> Frontend (static HTML/JS console)
```

## Project layout

```
app/
  config.py                 Central settings (env-driven)
  database.py                SQLAlchemy engine/session
  models/db_models.py         ORM schema: brands, laptops, cpu/gpu benchmarks,
                               price_history, compatibility_scores,
                               embeddings_metadata, user_preferences,
                               user_history, kb_versions
  schemas/schemas.py           Pydantic API contracts
  ingestion/pipeline.py        CSV/JSON ingestion, schema validation, dedup
  engineering/pipeline.py      Cleaning, normalization, derived features
  feature_store/scores.py      The 9 engineered scores
  search/semantic_search.py    Sentence-Transformers + FAISS
  recommendation/engine.py     Hybrid weighted recommendation engine
  explainability/explainer.py  Reasons / pros / cons / confidence
  budget_optimizer/            Upgrade/downgrade suggestions
  comparison/                  Multi-laptop comparison
  price_intelligence/          Price history & trend
  personalization/             User preferences & history
  similar_finder/               Embedding-based similar-laptop search
  analytics/                    Dataset statistics
  versioning/                   KB version snapshots & rollback
  routers/                      FastAPI route handlers (thin adapters only)
  main.py                       FastAPI app

scripts/
  generate_synthetic_dataset.py  Seeds data/raw/laptops_raw.csv (250 laptops)
  init_db.py                     Creates DB tables
  run_ingestion.py                Full pipeline: ingest -> engineer -> score -> DB -> version
  build_embeddings.py             Builds/rebuilds the FAISS index

web/                              React + TypeScript SPA (see web/README.md)
tests/test_basic.py               Pure-logic tests (no DB/ML deps required)
```

## Frontend

The frontend is `web/` — a React + TypeScript SPA covering AI Search, AI
Recommendations, Comparison, Budget Optimizer, Saved Laptops, Analytics, and
an Admin panel, all behind JWT auth. See `web/README.md` for setup.

(An earlier framework-free `frontend/index.html` prototype existed pre-auth;
it's been removed since it predates JWT and would 401 against every
protected endpoint — `web/` is the only supported frontend now.)

## Backend robustness

- All service-layer errors are typed (`app/utils/exceptions.py`:
  `NotFoundError`, `InvalidRequestError`, `DependencyNotReadyError`) and
  mapped centrally in `app/main.py` to a single JSON error shape:
  `{"error": {"code": ..., "message": ..., "details": ...}}` — the frontend
  relies on this shape to show meaningful messages instead of generic
  failures.
- A logging middleware records method/path/status/latency for every request.
- `/health` reports live DB connectivity and whether the semantic-search
  index has been built yet, so the frontend can tell "server is down" apart
  from "server is up but you haven't run `build_embeddings.py`".


## Authentication & authorization (production-grade)

Full JWT-based auth system, not a prototype:

- **Tables**: `users`, `roles`, `permissions` (+ `role_permissions` join),
  `refresh_tokens`, `password_resets`, `user_sessions`. `user_preferences`
  and `user_history` now carry a real integer FK to `users.id` instead of a
  client-supplied string.
- **Passwords**: bcrypt only, never plaintext, enforced by a Pydantic
  validator (upper/lower/digit, 8+ chars) on register and reset.
- **Tokens**: short-lived signed JWT access tokens (15 min) + opaque,
  rotating refresh tokens stored server-side only as a SHA-256 hash.
  Refreshing revokes the old token and issues a new pair (rotation).
- **Account lockout**: 5 failed attempts locks the account for 15 minutes
  (both configurable via `.env`).
- **Rate limiting**: `/api/auth/register`, `/register/verify-otp`,
  `/register/resend-otp`, `/login`, `/admin-login`, `/refresh`,
  `/forgot-password`, and `/reset-password` are all IP-rate-limited
  (`app.utils.rate_limit`) — account lockout alone only protects one known
  account, not registration spam, reset-email spam, or credential stuffing
  spread across many addresses. In-memory, so it's per-process; swap for a
  Redis-backed limiter if you scale to multiple backend replicas.
- **RBAC**: `user` and `admin` roles, each with a real permission set in the
  `permissions` table. `app.auth.dependencies.require_role()` /
  `require_permission()` enforce this server-side on every protected route —
  search, recommend, compare, budget-optimizer, similar, price-intelligence,
  and the wishlist/profile endpoints require login; analytics and everything
  under `/api/admin/*` (KB upload, KB versioning, user management, settings,
  logs) require the `admin` role.
- **Registration / email verification**: two-step — `POST /api/auth/register`
  creates an *unverified* account and emails a 6-digit OTP; the account
  cannot log in (`authenticate()` checks `is_verified`) until that code is
  confirmed at `POST /api/auth/register/verify-otp`, which then logs the
  user in. This is what proves the signup email is real and reachable, not
  just well-formed. Codes expire in 10 minutes and lock out after 5 wrong
  attempts (`REGISTRATION_OTP_EXPIRE_MINUTES` / `MAX_REGISTRATION_OTP_ATTEMPTS`
  in `.env`).
- **Password reset**: token-based (`POST /api/auth/forgot-password` /
  `reset-password`); the reset link is emailed the same way as the OTP above.
- **Outgoing email**: real SMTP via `app.utils.email` (any provider — Gmail,
  SendGrid, Mailgun, SES, Postmark, or your own server all speak SMTP, see
  `.env.example` for provider-specific settings). If `SMTP_HOST` is left
  unset, email is logged instead of sent (`EMAIL PLACEHOLDER -> ...` in the
  server log) — fine for local development, but means no real user ever
  receives their OTP or reset link, so set it before deploying.
- **Seeding**: `python scripts/seed_auth.py --admin-email ... --admin-password ...`
  creates the two roles, all permissions, and (optionally) your first admin
  — seeded admins are created already-verified, bypassing the OTP flow,
  since it's a trusted CLI bootstrap step rather than public registration.

See `web/README.md` for the React + TypeScript frontend that implements the
full login/register/forgot-password/reset-password/admin-login UI against
this API.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

# 1. Seed a synthetic knowledge base (stand-in for Kaggle/manufacturer sources;
#    swap this for your own CSV/JSON at any time — same pipeline handles both).
python scripts/generate_synthetic_dataset.py

# 2. Create DB tables
python scripts/init_db.py

# 3. Run the full ingestion pipeline (creates KB version v1)
python scripts/run_ingestion.py --file data/raw/laptops_raw.csv --notes "Initial synthetic seed"

# 4. Build the semantic search index
python scripts/build_embeddings.py

# 5. Start the API
uvicorn app.main:app --reload
```

The app auto-bootstraps on startup: if the `laptops` table is empty it will
automatically run steps 3-4 against the newest file in `data/raw/`, so steps
3-4 above are optional conveniences, not strictly required (set
`AUTO_BOOTSTRAP_KB=false` in `.env` to disable this and manage the KB purely
through the admin API).

Then, in a second terminal, start the frontend:
```bash
cd web
npm install
cp .env.example .env
npm run dev              # http://localhost:5173
```
See `web/README.md` for full frontend setup, and the **Docker deployment**
section below for a one-command production-style deployment. Interactive API
docs are at `http://localhost:8000/docs`.

## Updating the knowledge base

Drop a new CSV/JSON file into `data/raw/` (matching the required columns —
see `app/ingestion/pipeline.py::REQUIRED_COLUMNS`) and re-run:

```bash
python scripts/run_ingestion.py --file data/raw/your_new_export.csv --notes "Monthly refresh"
python scripts/build_embeddings.py
```

Each run creates a new `KBVersion` row and a full CSV snapshot under
`data/kb_versions/`, so you can roll back or diff versions
(`app/versioning/kb_version.py`).

## Switching to PostgreSQL for production

Change `DATABASE_URL` in `.env`, e.g.:
```
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/laptopsathi
```
No application code changes are required — SQLAlchemy handles the rest.
(Install `psycopg2-binary` if using Postgres.)

## Docker deployment

The whole stack (backend + FAISS index + frontend behind nginx) is
containerized:

```bash
cp .env.example .env
# Edit .env: set a real JWT_SECRET_KEY at minimum.
# Optionally set ADMIN_EMAIL / ADMIN_PASSWORD to auto-create the first admin.

docker compose up --build
```

- Frontend: `http://localhost` (nginx, reverse-proxies `/api/*` to the
  backend container — the browser only ever talks to one origin, so no CORS
  configuration is needed for this setup).
- Backend directly (e.g. for `/docs`): `http://localhost:8000`.
- The sqlite DB, FAISS index, and KB version snapshots persist in the
  `laptopsathi_data` named volume across restarts/redeploys.
- On first boot, the container seeds RBAC roles/permissions, creates the
  admin user if `ADMIN_EMAIL`/`ADMIN_PASSWORD` are set, and (via the
  app's own startup hook) auto-ingests `data/raw/laptops_raw.csv` and
  builds the search index — no manual pipeline steps required.
- For a split deployment (frontend and backend on different hosts/domains),
  build the frontend image with
  `--build-arg VITE_API_BASE_URL=https://api.yourdomain.com` instead, and
  set `CORS_ORIGINS` on the backend to the frontend's real origin.

**Before exposing this publicly**, at minimum:
- Set a unique `JWT_SECRET_KEY` (never use the default).
- Set `CORS_ORIGINS` to your real origin(s) if not using the bundled nginx proxy.
- Consider switching `DATABASE_URL` to PostgreSQL (see above) once you need
  more than single-instance/single-writer sqlite.
- Put the backend behind HTTPS (a reverse proxy / load balancer terminating
  TLS in front of `docker-compose.yml`'s services — this repo does not
  terminate TLS itself).

## Tests

```bash
python -m pytest tests/test_basic.py -v
```
These tests cover the data-engineering and feature-store logic and need only
pandas/numpy — useful for CI even before ML dependencies are installed.

## Notes on the knowledge-base data source

Per the project's design decision, this system does **not** scrape Amazon/
Flipkart live. `scripts/generate_synthetic_dataset.py` generates a realistic
250-laptop dataset (brand/CPU/GPU catalog with plausible benchmark scores and
an INR pricing model) so the whole pipeline runs end-to-end out of the box.
To use real data, export a Kaggle laptop dataset or manufacturer spec sheet
to the same column schema and point `run_ingestion.py` at it instead.
