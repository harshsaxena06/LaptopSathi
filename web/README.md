# LaptopSathi AI — Web (React + TypeScript)

The production authentication frontend: two-column login/register/admin-login,
forgot/reset password, protected dashboard, profile, and an admin panel —
all wired to the FastAPI auth backend in `../app/auth`.

## Setup

```bash
cd web
npm install
cp .env.example .env     # set VITE_API_BASE_URL if the API isn't on localhost:8000
npm run dev               # http://localhost:5173
```

Make sure the backend is running and seeded first (from the repo root):
```bash
python scripts/init_db.py
python scripts/seed_auth.py --admin-email admin@laptopsathi.ai --admin-password "ChangeMe123!"
uvicorn app.main:app --reload
```

## What's implemented

- **Auth pages**: Login (animated User ⇄ Admin toggle), Register, Forgot
  Password, Reset Password, Profile, 404.
- **Full console, ported and JWT-protected**: AI Search, AI Recommendations
  (with explainability), Comparison, Budget Optimizer, Saved Laptops,
  Analytics (admin-only), Admin user management — every request goes
  through the same `api` client that handles the access token and silent
  refresh, so there is no separate unauthenticated console anymore.
- **Components**: AuthLayout, AuthCard, LoginForm, RegisterForm,
  AdminLoginForm, PasswordInput, PasswordStrengthMeter, SocialLoginButtons
  (Google/GitHub — disabled placeholders), RememberMeCheckbox, ProtectedRoute,
  RoleGuard, AppShell (sidebar + mobile drawer), LaptopCard, ScoreDials,
  ExplanationBlock, skeleton/empty/error state primitives.
- **Auth flow**: JWT access token kept in memory only; refresh token
  persisted to `localStorage` (Remember me) or `sessionStorage` (session
  only); silent refresh-on-boot; automatic refresh-and-retry on a single 401.
- **Dark/light mode**, toast notifications, password strength meter,
  show/hide password, framer-motion transitions throughout.

## Scope note

The legacy `../frontend/index.html` static console is now superseded by
this app — it was never updated to send a JWT, so it will 401 against the
now-protected API. Keep it only for reference, or delete it.

## Verification note

This sandbox has no network access, so `npm install` / `tsc` against real
`@types/react` etc. could not be run here. What *was* verified:
- Every `.ts`/`.tsx` file passes an `esbuild` syntax transform.
- The entire app bundles cleanly from `main.tsx`, with all local imports
  (path aliases, relative imports, CSS) resolving correctly — only the
  external npm packages (react, react-router-dom, framer-motion) are
  stubbed out for this check.
Run `npm install && npm run build` once you have network access to get a
full TypeScript type-check against the real library types.
