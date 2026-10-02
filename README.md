# Desktop Cloud Platform

Self-hosted Desktop-as-a-Service (DaaS): provision isolated Linux desktop
environments in Docker containers, accessed through the browser via
noVNC. See the full specification in the project documentation
(`01A_Executive_Summary.md` through `22_Future_Roadmap.md`).

## Status

**Milestone M5 — Instance Dashboard complete** (`01D_Development_Roadmap.md`,
`17_Project_Task_Backlog.md`). Sprint 6 (Persistence) remains before M6.

Project foundation (VS-001 through VS-008), authentication (VS-009 through
VS-017 baseline + rate-limiting/role checks), template management
(VS-018 through VS-021), instance provisioning (VS-022 through VS-029,
VS-026 subdomains), the user dashboard (VS-030 through VS-034), and
container operations (VS-035 through VS-040) are implemented:

| Slice  | Deliverable                        | Status |
|--------|-------------------------------------|--------|
| VS-001 | Repository structure                | Done |
| VS-002 | Django project                      | Done |
| VS-003 | PostgreSQL connection                | Done |
| VS-004 | Redis connection                     | Done |
| VS-005 | Celery worker + test task            | Done |
| VS-006 | React + TypeScript + Tailwind        | Done |
| VS-007 | Traefik reverse proxy                | Done |
| VS-008 | DockerManager skeleton               | Done |
| VS-009 | Custom User model                    | Done |
| VS-010 | Registration API                     | Done |
| VS-011 | Login API                            | Done |
| VS-012 | Logout API                           | Done |
| VS-013 | Session middleware                   | Done |
| VS-014 | Protected routes                     | Done |
| VS-015 | React Login page                     | Done |
| VS-016 | React Registration page              | Done |
| VS-017 | Authentication tests                 | Done |
| VS-018 | Template model                       | Done |
| VS-019 | Template admin CRUD                  | Done |
| VS-020 | Template API                         | Done |
| VS-021 | Template selection UI                | Done |
| VS-022 | Instance model                       | Done |
| VS-023 | Create Instance API                  | Done |
| VS-024 | Docker create container              | Done |
| VS-026 | Subdomain assignment                 | Done |
| VS-029 | Provisioning progress UI             | Done |
| VS-030 | Dashboard statistics API             | Done |
| VS-031 | Running instances page               | Done |
| VS-032 | Instance cards                       | Done |
| VS-033 | Usage analytics widget               | Done |
| VS-034 | Launch Desktop button                | Done |
| VS-035 | Start container                      | Done |
| VS-036 | Stop container                       | Done |
| VS-037 | Restart container                    | Done |
| VS-038 | Delete container                     | Done |
| VS-039 | Auto-stop scheduler                  | Done |
| VS-040 | Error handling                       | Done |

Authentication includes registration, session login/logout, role checks,
profile management, password reset, throttling, audit events, and regression
coverage. Template management includes the JSON-validated template model,
admin-only CRUD, a development seed command, a template browsing page,
event logging, and regression coverage. Instance provisioning includes the
instance order API, Celery-driven Docker provisioning with resource limits
and persistent storage, hash-based subdomains routed by Traefik (VS-026),
provisioning events, the ordering form and progress UI, and regression
coverage. The dashboard includes the per-user statistics API
(`GET /api/v1/analytics/dashboard`), the event history API
(`GET /api/v1/events`), instance summary cards with a usage widget, and
the Launch Desktop button via `GET /api/v1/instances/{id}/launch`. Container
operations add start/stop/restart/delete endpoints with state-transition
guards (409 on conflicts), a Celery deletion task (persistent volume
retained by default), and a Celery beat auto-stop sweep for idle instances.
See
[`Code/docs/MILESTONE_READINESS_AUDIT.md`](Code/docs/MILESTONE_READINESS_AUDIT.md).

## Stack

Django 5 + DRF · PostgreSQL 16 · Redis 7 · Celery · Docker (docker-py) ·
Traefik v3 · React 18 + TypeScript + Vite · Tailwind CSS · TanStack Query

## Quick Start

Requires Docker and Docker Compose on a Linux host (or a Linux VM — see
`12_Deployment.md` Section 5 for the documented dev setup).

**One command brings the whole platform up** — it creates `.env`, builds the
images, migrates, seeds the development templates, and starts every service:

```bash
git clone <this-repo>
cd DAAS/Code
./scripts/init_dev.sh
```

Or step by step:

```bash
cp .env.example .env
docker compose build
docker compose up -d postgres redis
docker compose run --rm backend python manage.py migrate
docker compose up -d
```

Add to `/etc/hosts`:

```
127.0.0.1 app.localhost api.localhost
```

Then visit:

- **Frontend:** http://app.localhost
- **Backend health check:** http://api.localhost/api/v1/health/
- **Traefik dashboard (dev only):** http://localhost:8080
- **Django admin:** http://api.localhost/admin/

Create an admin user:

```bash
docker compose exec backend python manage.py createsuperuser
```

Create the three sample development templates:

```bash
docker compose exec backend python manage.py seed_templates
```

Confirm the Celery worker is alive:

```bash
docker compose exec backend celery -A config call dcp.debug_task
```

## Repository Structure

```
backend/          Django project (config/, apps/, services/, docker_manager/, tasks/, api/, tests/)
frontend/         React + TypeScript (Vite)
docker/traefik/   Reverse proxy static config
docs/             Repo-local documentation (runbooks, generated schemas — later milestones)
deployment/       Production deployment assets (M10)
scripts/          Dev/ops helper scripts
docker-compose.yml
.env.example
```

Backend and frontend structures intentionally mirror
`06_Backend_Architecture.md` Section 3 and `08_Frontend_Architecture.md`
Section 5.

## Engineering Rules (see `16_AI_AGENT_INSTRUCTIONS.md` and `14_Coding_Standards.md`)

- Business logic lives in `backend/services/`, never in views or React
  components.
- Only `backend/docker_manager/` talks to Docker.
- Long-running work goes through Celery, never inline in a request.
- Every completed feature is a full vertical slice: backend → API →
  frontend → tests → docs.
- No secrets committed — configuration is environment-variable driven
  (`.env`, never `.env` itself).

## Next Up

**Sprint 6 — Persistence** (`17_Project_Task_Backlog.md`, VS-041 onward):
persistent volume manager, delete confirmation workflow, and the
Retain/Delete data option. The next milestone after that is M6 — Browser
Desktop Access (noVNC session validation and friendly error pages; the
subdomain routing and launch button already work).
