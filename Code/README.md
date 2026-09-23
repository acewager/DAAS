# Desktop Cloud Platform

Self-hosted Desktop-as-a-Service (DaaS): provision isolated Linux desktop
environments in Docker containers, accessed through the browser via
noVNC. See the full specification in the project documentation
(`01A_Executive_Summary.md` through `22_Future_Roadmap.md`).

## Status

**Milestone M2 — Authentication complete** (Sprint 1,
`17_Project_Task_Backlog.md`).

Project foundation (VS-001 through VS-008) and authentication hardening
work (VS-009 through VS-017 baseline + rate-limiting/role checks) are
implemented:

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

Authentication includes registration, session login/logout, role checks,
profile management, password reset, throttling, audit events, and regression
coverage. See
[`docs/MILESTONE_READINESS_AUDIT.md`](docs/MILESTONE_READINESS_AUDIT.md).

## Stack

Django 5 + DRF · PostgreSQL 16 · Redis 7 · Celery · Docker (docker-py) ·
Traefik v3 · React 18 + TypeScript + Vite · Tailwind CSS · TanStack Query

## Quick Start

Requires Docker and Docker Compose on a Linux host (or a Linux VM — see
`12_Deployment.md` Section 5 for the documented dev setup).

```bash
git clone <this-repo>
cd DAAS
cp .env.example .env
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

**Sprint 2 — Templates** (`17_Project_Task_Backlog.md`, VS-018 onward):
template model, admin CRUD, template API, and selection UI.
