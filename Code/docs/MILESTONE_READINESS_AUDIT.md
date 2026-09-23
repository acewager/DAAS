# Milestone Readiness Audit

**Audit date:** 2026-09-23
**Scope:** implementation in `Code/` compared with the MVP PRD.
**Verification state:** static review completed; runtime checks are pending because this workstation does not have Docker, Node/npm, or the backend Python dependencies installed.

## Current milestone decision

| Milestone | Decision | Evidence |
| --- | --- | --- |
| M1 — Project Foundation | Implemented; runtime verification pending | Django, React/Vite, Compose services for PostgreSQL/Redis/Celery/Traefik, DockerManager skeleton, environment template, health endpoint, and CI workflow are present. |
| M2 — Authentication | In progress; do not begin M3 | Registration, login/logout, session-based protection, role model/permissions, rate limits, event logging, and login/registration UI exist. Password reset and a user-profile management surface are absent. |
| M3–M10 | Not started | No end-to-end vertical slices exist for templates, provisioning, dashboard, browser desktop access, requests, analytics, administration, or production readiness. |

The roadmap requires the current vertical slice to be complete before its successor begins. Template Management (M3) is therefore blocked on closing M2 and performing its runtime/manual verification.

## M2 completion gate

Before updating the product status to **M2 complete**, implement and verify:

1. Email-based, single-use, time-limited password-reset request and confirmation endpoints, with reset events recorded.
2. An authenticated profile endpoint that permits the user to manage their own profile, plus the corresponding protected frontend page/route.
3. The PRD password policy: minimum length, mixed case, a number, and a special character. Apply the same policy in the frontend for immediate feedback and on the backend as the authority.
4. Tests for profile authorization/updates, reset-token expiry and single-use behavior, password policy rejection, and reset-related event logs.
5. A manual Compose smoke test: migrations, backend health, Redis/Celery connectivity, registration/login/logout, protected-route behavior, and secure-cookie behavior in the production configuration.

## Automation added by this audit

`.github/workflows/ci.yml` now prevents regressions by running Django migration checks, migrations, and pytest against PostgreSQL and Redis, plus a clean frontend dependency install and production build for pull requests and pushes to `main`.

## Local environment preparation

After Docker Engine and Docker Compose are installed on this machine, prepare and verify the stack with:

```bash
cd Code
./scripts/init_dev.sh
docker compose ps
docker compose exec backend python manage.py check --deploy
docker compose exec backend pytest -q
docker compose exec frontend npm run build
```

For local browser routing, add `127.0.0.1 app.localhost api.localhost` to `/etc/hosts`, as documented in the project README. Do not start M3 until the M2 gate is closed.
