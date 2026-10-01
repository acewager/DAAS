# Milestone Readiness Audit

**Audit date:** 2026-10-01
**Scope:** implementation in `Code/` compared with the MVP PRD.
**Verification state:** static review completed. Runtime checks are being
executed separately (Docker, Node/npm, and the backend Python dependencies
are available as of this audit — see the verification log at the bottom).

## Current milestone decision

| Milestone | Decision | Evidence |
| --- | --- | --- |
| M1 — Project Foundation | Done | Django, React/Vite, Compose services for PostgreSQL/Redis/Celery/Traefik, DockerManager, environment template, health endpoint, and CI workflow are present (VS-001–VS-008). |
| M2 — Authentication | Done | Registration, session authentication, roles, protected routes, profile management, password reset, password policy, throttling, event logging, UI, and regression tests are implemented (VS-009–VS-017). |
| M3 — Template Management | Done | `apps/templates/` provides the JSON-validated `DesktopTemplate` model with migration, admin CRUD, template API (list/retrieve for users, create/update/delete for admins), JSON configuration validation, a `seed_templates` development command, a template browsing page, template event logging, and regression tests (`test_templates.py`) (VS-018–VS-021). |
| M4 — Instance Provisioning | In progress | `DesktopInstance` model + migration (VS-022), `InstanceService` + order/list API (VS-023), `DockerManager.create_container` (VS-024), resource limits (VS-025), persistent volume attachment (VS-027), provisioning event logging (VS-028), Celery `provision_instance` task, and tests (`test_instances.py`). Frontend: read-only `InstancesPage` with polling plus the `NewInstancePage` ordering form (template selection, instance settings, resource limits — VS-029). End-to-end provisioning verified at runtime twice (see verification log). Outstanding: subdomain assignment (VS-026) and the commit of the working tree. |
| M5–M10 | Not started | No end-to-end vertical slices exist for the dashboard, browser desktop access, requests, analytics, administration, or production readiness. |

Instance Provisioning (M4) is the active milestone; VS-024 runtime
verification and VS-029 are closed. VS-026 (subdomain assignment) and
committing the Sprint 3 working tree are the immediate next steps.

## M3 completion evidence

1. `DesktopTemplate` model with JSON schema validation (`validate_json_configuration` → `instance.clean()`), slug uniqueness, and enabled flag.
2. Admin-only template CRUD through the template API; regular users can list/retrieve enabled templates only; all template mutations record events (`TEMPLATE_CREATED`, etc.).
3. `seed_templates` management command creating three repeatable development templates (XFCE Minimal, XFCE Developer Tools, XFCE Browser) against `lscr.io/linuxserver/webtop:ubuntu-xfce`.
4. `TemplatesPage` in the React frontend listing available templates, wired through `templateService`.
5. Regression tests covering admin-managed CRUD visibility, disabled-template behavior, and invalid JSON configuration rejection.

## M4 progress evidence (uncommitted working tree)

1. `DesktopInstance` model: user/template foreign keys, status enum (REQUESTED → QUEUED → PROVISIONING → RUNNING/FAILED), container name/id, access hash, CPU/memory limits, persistence flag, auto-stop minutes, error message — plus migration.
2. `InstanceService.request()` creating the instance, queueing it, recording `INSTANCE_REQUESTED`, and dispatching the Celery task.
3. `POST/GET /api/v1/instances/` endpoints with ownership scoping and disabled/missing-template rejection.
4. `DockerManager.create_container()` creating and starting the container with hostname, memory/CPU limits, optional persistent volume, and `dcp-network` attachment; failures map to `DockerManagerError` and a `FAILED` instance state with `INSTANCE_PROVISION_FAILED` recorded.
5. Celery `provision_instance` task driving the REQUESTED → QUEUED → PROVISIONING → RUNNING lifecycle.
6. `InstancesPage` polling every 5 seconds showing instance status, template, resources, and error message, plus the `NewInstancePage` ordering form (template select, name, persistence, auto-stop, CPU/memory limits) wired through `instanceService.createInstance`.
7. CSRF handling in the frontend: `apiClient` interceptor sending the `csrftoken` cookie as `X-CSRFToken` on unsafe methods; `AuthContext` seeds the cookie via `GET /auth/csrf/` at application start. Required because DRF session authentication enforces CSRF on authenticated POSTs (e.g., `POST /instances`, profile update, logout).
8. `test_instances.py` covering ordering, ownership scoping, Celery dispatch, and template validation.

## Automation

`.github/workflows/ci.yml` prevents regressions by running Django migration checks, migrations, and pytest against PostgreSQL and Redis, plus a clean frontend dependency install and production build for pull requests and pushes to `main`.

## Runtime verification log (2026-10-01)

- Environment: Docker Engine 29.8.1, Docker Compose v5.5.1, Node/npm, and frontend `node_modules` installed. `/etc/hosts` already contains `127.0.0.1 app.localhost api.localhost`.
- **Gap fixed:** `docker-compose.yml` did not mount the Docker socket into the `backend`/`celery` services, but `docker_manager` connects to `unix:///var/run/docker.sock` from `settings.DOCKER_HOST`. The socket is now mounted read-only for the dev environment.
- **Gap fixed:** the Celery worker registered only `dcp.debug_task` — `autodiscover_tasks()` imports `apps.<name>.tasks` and does not cover the top-level `tasks/` package, so `dcp.provision_instance` was never registered and provisioning requests sat in the queue. `CELERY_IMPORTS = ("tasks.provisioning",)` now registers the task module after `django.setup()`.
- **Gap fixed:** the frontend sent no CSRF token, so authenticated POSTs (instance creation, profile update, logout) would fail with 403 under DRF session authentication. `apiClient` now sends the `csrftoken` cookie as `X-CSRFToken` on unsafe methods and `AuthContext` seeds the cookie at start.
- Compose smoke test: images build; migrations apply (schema current: `accounts_user`, `events_eventlog`, `instances_desktopinstance`, `templates_desktoptemplate`); all six services come up; `/api/v1/health/` returns 200 healthy through Traefik.
- `python manage.py check --deploy`: 6 warnings (HSTS, SSL redirect, dev SECRET_KEY, secure cookies, DEBUG) — expected in development; production hardening is part of M10.
- `pytest`: 13 passed (auth, templates, instances, health, tasks).
- Frontend production build (`tsc -b && vite build`): passes, including the `NewInstancePage` ordering form.
- End-to-end provisioning verification (run twice — before and after the frontend CSRF fix, the second simulating the exact React app flow: register → login → `POST /api/v1/instances/` with the cookie-seeded `X-CSRFToken` header): 202 QUEUED → Celery worker → `DockerManager.create_container` → webtop container running on `dcp-network` with a persistent volume → instance status RUNNING → `INSTANCE_REQUESTED` and `INSTANCE_PROVISIONED` events recorded → instance list API reflects state. Acceptance criterion "Database state matches Docker state" verified.
- Verification artifacts (test instances, users, containers, volumes, cookie jar) were removed afterwards.
- Note: if a provisioning request is dispatched while the worker does not have the task registered (e.g., worker started before task registration), the message is discarded and the instance remains QUEUED; re-dispatch by ordering a new instance after the worker is up.

## Local environment preparation

Prepare and verify the stack with:

```bash
cd Code
./scripts/init_dev.sh
docker compose ps
docker compose exec backend python manage.py check --deploy
docker compose exec backend pytest -q
docker compose exec frontend npm run build
```

Do not start M5 until the M4 gate is closed.
