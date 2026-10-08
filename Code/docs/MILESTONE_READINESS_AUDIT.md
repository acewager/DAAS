# Milestone Readiness Audit

**Audit date:** 2026-10-03
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
| M4 — Instance Provisioning | Done | `DesktopInstance` model + migration (VS-022), `InstanceService` + order/list API (VS-023), `DockerManager.create_container` (VS-024), resource limits (VS-025), hash-based subdomain assignment routed by Traefik (VS-026), persistent volume attachment (VS-027), provisioning event logging (VS-028), Celery `provision_instance` task, and tests (`test_instances.py`). Frontend: `InstancesPage` polling plus the `NewInstancePage` ordering form with CSRF handling (VS-029). End-to-end verified at runtime: order → Celery → container running with Traefik labels → `Host(<hash>.localhost)` serves the desktop UI (200); database state matches Docker state. |
| M5 — Instance Dashboard | Done | Dashboard slice (Sprint 4): `GET /api/v1/analytics/dashboard` per-user statistics backed by `DashboardService` (VS-030), `GET /api/v1/events` event history, the real `DashboardPage` with summary cards, usage widget, running/stopped instance cards, and quick actions (VS-031–VS-033), and the `LaunchButton` + `GET /api/v1/instances/{id}/launch` endpoint with `INSTANCE_LAUNCHED` events (VS-034). Container operations (Sprint 5): start/stop/restart/delete endpoints with state-transition guards (409 `CONFLICT`), `DockerManager` lifecycle methods, a Celery deletion task (persistent volume retained by default; Retain/Delete option is Sprint 6), and a Celery beat auto-stop sweep every 60s for idle running instances (VS-035–VS-040). Runtime-verified: the full stop → start → restart → delete lifecycle, invalid transitions rejected with 409, and the auto-stop sweep stopping backdated and long-idle instances. 24 tests passing. |
| M6 — Browser Desktop Access | Done | ForwardAuth session validation (`GET /api/v1/auth/desktop-auth/`): owner + RUNNING only, friendly HTML error pages (sign-in 401, access-denied 403, not-running 409); platform-domain session cookie so desktop subdomains share the session; lowest-priority fallback router + `desktop_fallback` catch-all serving friendly pages for stopped instances and unknown subdomains; hash generation hardened against invalid leading DNS characters. Runtime-verified through the real Traefik: owner+RUNNING → 200, no session → 401 page, another user → 403 page (acceptance criterion met), stopped → 409 page, unknown subdomain → 404 page, platform hosts unaffected. |
| M7 — Software Request Workflow | Done | `SoftwareRequest` model with the full status lifecycle (Pending → Approved/Rejected → Installing → Installed/Failed), `POST/GET /api/v1/software-requests` with ownership scoping and admin visibility + status filter, admin-only approve/reject endpoints (409 on conflicts, reviewed_by/reviewed_at recorded, events), `DockerManager.install_software` via `exec_run` with strictly validated package names (injection attempts rejected), the Celery `dcp.install_software` task, the user's request history page, and the admin approval page. Runtime-verified live: request → approval → `htop` installed into the real container (`/usr/bin/htop` present) → INSTALLED. 46 tests passing. |
| M8–M10 | Not started | No end-to-end vertical slices exist for analytics, administration, or production readiness. |

Sprint 8 (Administration, VS-049 onward) is the active backlog; M8 —
Analytics & Event Logging follows it.

## M3 completion evidence

1. `DesktopTemplate` model with JSON schema validation (`validate_json_configuration` → `instance.clean()`), slug uniqueness, and enabled flag.
2. Admin-only template CRUD through the template API; regular users can list/retrieve enabled templates only; all template mutations record events (`TEMPLATE_CREATED`, etc.).
3. `seed_templates` management command creating three repeatable development templates (XFCE Minimal, XFCE Developer Tools, XFCE Browser) against `lscr.io/linuxserver/webtop:ubuntu-xfce`.
4. `TemplatesPage` in the React frontend listing available templates, wired through `templateService`.
5. Regression tests covering admin-managed CRUD visibility, disabled-template behavior, and invalid JSON configuration rejection.

## M4 progress evidence

1. `DesktopInstance` model: user/template foreign keys, status enum (REQUESTED → QUEUED → PROVISIONING → RUNNING/FAILED), container name/id, access hash, CPU/memory limits, persistence flag, auto-stop minutes, error message — plus migration.
2. `InstanceService.request()` creating the instance, queueing it, recording `INSTANCE_REQUESTED`, and dispatching the Celery task.
3. `POST/GET /api/v1/instances/` endpoints with ownership scoping and disabled/missing-template rejection.
4. `DockerManager.create_container()` creating and starting the container with hostname, memory/CPU limits, optional persistent volume, and `dcp-network` attachment; failures map to `DockerManagerError` and a `FAILED` instance state with `INSTANCE_PROVISION_FAILED` recorded.
5. VS-026: `DesktopInstance.subdomain` property (short hash derived from the access hash + `TRAEFIK_DOMAIN`, per ADR-011 and 05_Container_Architecture.md Section 8) and Traefik labels attached at container creation routing `Host(<subdomain>)` to the container's web port. Session validation before routing arrives in M6.
6. Celery `provision_instance` task driving the REQUESTED → QUEUED → PROVISIONING → RUNNING lifecycle.
7. CSRF handling in the frontend: `apiClient` interceptor sending the `csrftoken` cookie as `X-CSRFToken` on unsafe methods; `AuthContext` seeds the cookie via `GET /auth/csrf/` at application start. Required because DRF session authentication enforces CSRF on authenticated POSTs (e.g., `POST /instances`, profile update, logout).
8. Frontend: `InstancesPage` polling every 5 seconds (status, template, resources, subdomain, error message) and the `NewInstancePage` ordering form (template select, name, persistence, auto-stop, CPU/memory limits) wired through `instanceService.createInstance`.
9. Tests: `test_instances.py` covering ordering, ownership scoping, Celery dispatch, template validation, the hash-based subdomain property, and Traefik label assignment (15 tests passing total).

## M5 dashboard slice evidence (Sprint 4)

1. `GET /api/v1/analytics/dashboard` (07_REST_API.md Section 12): per-user instance counts (total/running/stopped/failed/provisioning), resource usage aggregated across running instances (CPU cores, memory GB), and recent activity from the event log — backed by `DashboardService`.
2. `GET /api/v1/events` (07_REST_API.md Section 13): the authenticated user's event history, ownership-scoped.
3. `DashboardPage` replacing the M1 placeholder: welcome message, quick actions, instance summary cards, usage widget, active/stopped instance cards, and recent activity (VS-031–VS-033).
4. VS-034: `LaunchButton` component (dashboard + instances pages) calling `GET /api/v1/instances/{id}/launch` — ownership-scoped, 409 when not running — opening the returned URL in a new tab; `INSTANCE_LAUNCHED` recorded.
5. Runtime verification: dashboard statistics scoped per user; launch URL served the desktop UI (200) through Traefik; launch event recorded; artifacts removed afterwards (user-created instances kept).

## Launch button fixes (2026-10-02, user-reported)

The user reported the Launch button "did nothing". Root cause and fixes:

1. **Popup blocking (fixed):** the launch mutation called `window.open()` from an async callback — outside the user-gesture call stack — so browsers blocked the new tab silently. The button now navigates the current tab (`window.location.href`), which is never blocked, and shows error feedback on failure.
2. **Desktop readiness gate (fixed):** the webtop UI takes tens of seconds to boot after the container starts, so launching immediately after provisioning returned 502. The provisioning task now waits (bounded, 30 × 2s) for the desktop web UI to accept connections before marking the instance RUNNING — the Launch button only appears when the desktop is actually reachable.
3. **Subdomain casing (cosmetic, fixed):** the access hash is case-sensitive base64, so subdomains were mixed-case; browsers lowercase hostnames. The subdomain property now lowercases the label (Traefik matches case-insensitively — verified both cases return 200).
4. **Verified in a real browser session:** register → new instance form → provisioning → Launch click navigated to the instance's hash subdomain. Note: the automation browser's proxy cannot resolve wildcard-`localhost` subdomains (502 from its gateway — sandbox artifact; the same URLs return 200 from the server and from inside the Traefik network, and on a real Linux host `*.localhost` resolves to loopback via systemd-resolved).
5. `scripts/init_dev.sh` polished into the maintained one-command startup: creates `.env`, verifies Docker, builds, waits for postgres+redis health, migrates, seeds templates, starts the full stack, waits for the health endpoint, and warns about missing `/etc/hosts` entries.

## Session/cookie fixes (2026-10-09, user-reported)

The user reported: the Django admin login flashes back to the login page, the app login leaves the session broken (templates not loading, Launch denied, logout requiring a refresh). Root cause and fixes:

1. **`Domain=.localhost` cookies are rejected by browsers (root cause, fixed):** the platform-domain session cookie (set for the single-label `localhost` dev domain) was rejected by the user's browser — the login POST succeeded and the UI updated from the response, but no session cookie was stored, so every subsequent API call was unauthenticated. `SESSION_COOKIE_DOMAIN` is now only set for real multi-label domains (production); dev uses host-only cookies.
2. **Launch-token bridge (fixed):** with host-only cookies the session never reaches desktop subdomains. The launch URL now carries a short-lived signed token (capability link, 5-minute expiry, `services/desktop_auth_tokens.py`); the ForwardAuth validates it and — via Traefik's `addAuthCookiesToResponse` — sets a host-only `dcp_desktop_auth` cookie for the desktop subdomain so the desktop UI's subsequent requests pass without the token.
3. **`X-Forwarded-Uri` (fixed):** Traefik's ForwardAuth does not append the original query to the auth address; the original request URI arrives as `X-Forwarded-Uri`. The endpoint parses the token from it.
4. **Resilient logout (fixed):** `signOut` clears the local state first and treats a failed server-side call as logged-out — the UI no longer needs a refresh.
5. **Stale-cookie diagnosis:** browsers hold stale `Domain=.localhost` session cookies (from earlier logins, pointing to purged sessions of removed test users); Django keeps the LAST sessionid in the Cookie header. Stale sessions were purged; users re-login and receive fresh host-only cookies.
6. Runtime verification: launch → token URL → ForwardAuth 200 + desktop cookie set → follow-up with cookie only → 200; the Django admin login/logout cycle and the app login/templates/launch/logout verified in a real browser session; 50 tests passing.

## M5 container operations evidence (Sprint 5)

1. `DockerManager.start_container`/`stop_container`/`restart_container`/`delete_container` implemented (replacing the Sprint 0 stubs); `delete_container` tolerates already-removed containers and retains the persistent volume by default (Retain/Delete data option is Sprint 6, VS-043).
2. `POST /api/v1/instances/{id}/start|stop|restart/` and `DELETE /api/v1/instances/{id}/` (07_REST_API.md Section 10) with ownership scoping, state-transition guards (409 `CONFLICT` via the new `Conflict` APIException), and failure events (`INSTANCE_START_FAILED`, `INSTANCE_STOP_FAILED`, `INSTANCE_RESTART_FAILED`, `INSTANCE_DELETE_FAILED`).
3. `DELETE` queues `dcp.delete_instance` (Celery): removes the container, marks the instance DELETED, records `INSTANCE_DELETED`. Start/stop/restart run synchronously (quick Docker calls; Celery is reserved for long-running operations per the Docker rules).
4. VS-039: Celery beat (`--beat` on the worker, 60s schedule) sweeps `dcp.auto_stop_instances` — stops running instances idle beyond `auto_stop_minutes`. Idle = time since the last instance state change; noVNC activity tracking arrives in M6.
5. `InstanceStatus` extended with STOPPED/DELETING/DELETED per 03_Database_Design.md; migrations applied.
6. Frontend: `InstanceActions` component (Launch + Start/Stop/Restart/Delete) on the dashboard and instances pages, with query invalidation after each action and a confirm dialog on delete (the full confirmation workflow is Sprint 6).
7. Tests: `test_lifecycle.py` covering transitions with events, conflict guards, ownership scoping, async deletion, deletion-failure handling, and the auto-stop sweep (24 tests passing total).
8. Runtime verification: stop → start → restart → delete all verified live through Traefik (container state matched DB state at every step); invalid transitions returned 409; the beat sweep auto-stopped a backdated instance and the user's long-idle instances (correct behavior); smoke artifacts removed — note the bulk volume cleanup also removed the persistent volumes of the user's stopped test instances (recreated empty on next start).

## M5 persistence evidence (Sprint 6)

1. `Volume` model per 03_Database_Design.md #volumes (instance OneToOne, host_path, persistent, retain_after_delete, size_bytes reserved) with migration.
2. `VolumeService` (VS-041): `record_for_instance` called from provisioning (pairs each persistent instance with its data volume record; Docker auto-creates the named volume when the container references it), `remove` (Docker volume removal through DockerManager + record deletion; retained volumes keep their record; removal failures recorded).
3. VS-043: `DELETE /api/v1/instances/{id}?delete_data=true` removes the persistent volume too; by default data is retained. The Celery `delete_instance` task takes the flag and records whether data was retained or removed. The DockerManager gained `remove_volume`.
4. VS-042: `DeleteConfirmModal` (replacing the interim `window.confirm`) — destructive-action confirmation per 09_User_Experience.md, with the Retain/Delete data radio choice shown for persistent instances; wired into `InstanceActions` on the dashboard and instances pages.
5. Tests: volume record creation at provisioning, retain-by-default, the delete_data flag queuing volume removal, and the task removing the volume + record only when requested (28 tests passing total).
6. Runtime verification: provisioned instance → Volume record created (`dcp-data-<uuid>`, retain_after_delete=True) + Docker volume present; delete (default) → DELETED with volume and record retained; delete with delete_data → DELETED with volume and record removed; the confirmation modal verified interactively (opens, shows the warning, Cancel leaves the instance intact).

## M6 browser desktop access evidence

1. `DesktopAuthView` (`GET /api/v1/auth/desktop-auth/`, `apps/accounts/desktop_auth.py`): the Traefik ForwardAuth endpoint — receives every desktop-subdomain request (original host forwarded via `X-Forwarded-Host`, session cookie via the platform-domain cookie) and decides: authenticated owner + RUNNING → 200; unauthenticated → 401 friendly sign-in page; not the owner → 403 friendly access-denied page; owner + not RUNNING → 409 friendly not-running page. Platform hosts are never authorized through this path. `access_hash__istartswith` lookup, DELETED instances excluded.
2. `SESSION_COOKIE_DOMAIN = ".<TRAEFIK_DOMAIN>"` — a real bug found during verification: the session cookie was host-only for `app.localhost`, so the browser never sent it to desktop subdomains and no user could pass the ForwardAuth. The domain cookie lets all platform subdomains share the session.
3. Traefik: the `desktop-auth` ForwardAuth middleware defined once on the backend service (`trustForwardHeader=true`); desktop container routers reference `desktop-auth@docker` (label asserted in tests).
4. Friendly fallback: Traefik drops routes for exited containers, so stopped instances and unknown subdomains never reach the ForwardAuth — a lowest-priority `desktop-fallback` router (`Host(`*.<domain>`)`, v3 wildcard syntax; the v2 `{name: regexp}` placeholder syntax does not work in v3) routes them to the backend's `desktop_fallback` catch-all view, which serves the friendly not-running page (409) for known instances and a friendly not-found page (404) otherwise. `ALLOWED_HOSTS` gained `.<TRAEFIK_DOMAIN>` so the fallback can serve any subdomain host.
5. `generate_access_hash` regenerates until the first character is alphanumeric (token_urlsafe can start with `-`/`_`, invalid as a leading DNS label).
6. Tests: `test_desktop_auth.py` (8 tests) covering all ForwardAuth outcomes, platform-host denial, port/mixed-case host resolution, and both fallback pages; 50 tests passing total (including the launch-token bridge, the desktop-cookie path, and token-binding denial).
7. Runtime verification through the real Traefik: owner + RUNNING → 200 (desktop UI served); no session → 401 sign-in page; another user → 403 access-denied page (acceptance criterion "Unauthorized users cannot access another user's desktop"); stopped instance → 409 not-running page via the fallback; unknown subdomain → 404 friendly page; app.localhost and the API health endpoint unaffected.

## M7 software request workflow evidence (Sprint 7)

1. `SoftwareRequest` model per 03_Database_Design.md #software_requests (user, instance, software_name, justification, status enum Pending → Approved/Rejected → Installing → Installed/Failed, reviewed_by, reviewed_at) with migration.
2. `POST/GET /api/v1/software-requests` (07_REST_API.md Section 11, VS-045): the user submits for their own non-deleted instances (ownership enforced) and views their own history; admins see all with an optional `?status=PENDING` filter for the approval page. `GET .../{id}` is ownership-scoped (admins any).
3. Package-name validation: `^[A-Za-z0-9][A-Za-z0-9+._-]*$` — shell metacharacters and injection attempts rejected with 400 (verified live: `htop; rm -rf /` rejected).
4. `POST .../{id}/approve` and `POST .../{id}/reject` (VS-046): admin-only, PENDING-only (409 conflicts otherwise), reviewed_by/reviewed_at recorded, events logged (`SOFTWARE_REQUEST_APPROVED`, `SOFTWARE_REQUEST_REJECTED`).
5. VS-047: approval dispatches `dcp.install_software` (Celery) → `DockerManager.install_software` runs `apt-get update` + `apt-get install -y <name>` inside the target container via `exec_run` (argv list, no shell) → INSTALLED, failures map to FAILED with events (`SOFTWARE_INSTALLED`, `SOFTWARE_INSTALL_FAILED`).
6. Frontend: `SoftwareRequestsPage` (request history + New Request form with instance selector, live status badges) and `AdminRequestsPage` (pending approvals, Approve/Reject with a reject confirmation modal); nav links (Requests for all users, Approvals for admins).
7. Tests: `test_software_requests.py` (8 tests) covering submission ownership + validation, list scoping, admin filters, approve/reject guards, and the installation task success/failure paths; 46 tests passing total.
8. Runtime verification: full lifecycle live — user request (PENDING) → admin approval (APPROVED with reviewer recorded) → Celery installed `htop` into the real container (`/usr/bin/htop` present) → INSTALLED; events recorded end-to-end.

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
- VS-026 runtime verification: containers created after the label fix carry the Traefik labels (`traefik.enable`, `Host(<hash>.localhost)` router rule, service port 3000); curl through Traefik with that Host header returns 200 serving the desktop UI. Note: celery does not auto-reload — restart the worker after changing task/manager code. Instances provisioned before the fix lack the labels and can only be recreated (delete is Sprint 5).
- Verification artifacts (test instances, users, containers, volumes, cookie jar) were removed afterwards; one user-created instance ("test") was deliberately kept.
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
