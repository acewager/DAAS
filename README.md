<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.png">
  <img src="assets/banner-light.png" alt="Desktop Cloud Platform — self-hosted Linux desktops in your browser" width="840" />
</picture>

[![Release](https://img.shields.io/github/v/tag/acewager/DAAS?label=release&sort=semver&color=0EA5E9)](https://github.com/acewager/DAAS/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/acewager/DAAS/ci.yml?label=CI&color=0EA5E9)](https://github.com/acewager/DAAS/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-62%20passing-22C55E)](https://github.com/acewager/DAAS/actions/workflows/ci.yml)
[![Milestones](https://img.shields.io/badge/milestones-10%2F10%20complete-8B5CF6)](PRD%20Docs/01D_Development_Roadmap.md)
[![Stack](https://img.shields.io/badge/Django%205%20·%20DRF%20·%20React%2018%20·%20Docker-0F172A)](PRD%20Docs/02_System_Architecture.md)

**Self-hosted Linux desktops in your browser — spun up in seconds, isolated in Docker, on a single server.**

</div>

---

**Desktop Cloud Platform** is a complete, self-hosted Desktop-as-a-Service (DaaS): users pick a template, get an isolated Linux desktop in a Docker container, and open it in their browser through [noVNC](https://novnc.com) — with resource limits, persistent storage, an admin portal, and usage analytics. Think *your own private cloud-desktop service*, on one machine.

Built end-to-end from a 22-document PRD: **66 vertical slices**, **10/10 milestones**, **62 backend tests**.

## ✨ Features

| | Feature | What you get |
|---|---|---|
| 🖥️ | **Browser desktops** | Isolated XFCE desktops in Docker, accessed through noVNC via hash-based subdomains with ForwardAuth session validation |
| 🚀 | **One-click provisioning** | Order from JSON-validated templates → Celery provisions the container with CPU/memory limits, persistent storage, and a readiness gate |
| 🎛️ | **Full lifecycle** | Start / stop / restart / delete, with an auto-stop sweep for idle instances |
| 📦 | **Software on demand** | Users request extra software; admins approve; Celery installs it inside the running container |
| 📊 | **Usage analytics** | Per-instance CPU/memory sampling with a background aggregation sweep and live usage charts |
| 🛡️ | **Admin portal** | User & instance management, event log viewer, platform analytics, system health — all without touching the database |
| 🔐 | **Secure by default** | Session auth with roles, ForwardAuth-guarded desktops, strict package-name validation, production settings that pass `check --deploy` with zero warnings |
| 🌐 | **Production-ready** | HTTPS via Traefik + Let's Encrypt, gunicorn, whitenoise, backup/restore scripts, and a deployment runbook |

## 🚀 Quick Start

> Requires a Linux host with **Docker** and **Docker Compose v2**.

```bash
git clone https://github.com/acewager/DAAS.git
cd DAAS/Code
./scripts/init_dev.sh
```

That single command creates `.env`, builds the images, migrates, seeds three
development templates, and starts the full stack — then:

| | Where | What |
|---|---|---|
| 🌐 | `http://app.localhost` | The web app — register and create your first desktop |
| 🔌 | `http://api.localhost/api/v1/health/` | The API health check |
| 🛠️ | `http://api.localhost/admin/` | The Django admin |
| 📈 | `http://localhost:8080` | The Traefik dashboard (dev only) |

<details>
<summary><strong>Step by step</strong></summary>

```bash
cp .env.example .env                 # configure, or start with defaults
docker compose build                 # build all images
docker compose up -d postgres redis  # start the core services
docker compose run --rm backend python manage.py migrate
docker compose up -d                 # start the full stack
```

Add to `/etc/hosts` (desktop subdomains resolve automatically):
`127.0.0.1 app.localhost api.localhost`

Create the admin user and seed templates:

```bash
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_templates
```

</details>

## 🏗️ Architecture

```text
┌──────────┐   ┌─────────┐   ┌──────────┐   ┌───────────┐   ┌────────────┐
│  Browser │──▶│ Traefik │──▶│  Django  │──▶│   Redis   │──▶│   Celery   │
│ (noVNC)  │   │  HTTPS  │   │  + DRF   │   │  (broker) │   │ (provision)│
└──────────┘   └─────────┘   └──────────┘   └───────────┘   └─────┬──────┘
     │              │             │                               │
     │              │        ┌────▼─────┐                  ┌──────▼──────┐
     └──────────────┘        │PostgreSQL│                  │   Docker    │
      desktop subdomains     └──────────┘                  │  desktops   │
                                                           └─────────────┘
```

| Layer | Technology |
|---|---|
| Backend | Django 5 · Django REST Framework · Celery |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS · TanStack Query |
| Data | PostgreSQL 16 · Redis 7 |
| Infrastructure | Docker · Traefik v3 (TLS, ForwardAuth, desktop routing) |

**Engineering rules** — business logic lives in services, only `docker_manager/` talks to Docker, long-running work runs in Celery, and every feature ships as a full vertical slice (backend → API → frontend → tests → docs).

## 🗺️ Roadmap — MVP complete

| Milestone | Status |
|---|---|
| M1 — Project Foundation | ✅ Done |
| M2 — Authentication | ✅ Done |
| M3 — Template Management | ✅ Done |
| M4 — Instance Provisioning | ✅ Done |
| M5 — Instance Dashboard | ✅ Done |
| M6 — Browser Desktop Access | ✅ Done |
| M7 — Software Request Workflow | ✅ Done |
| M8 — Analytics & Event Logging | ✅ Done |
| M9 — Administration Portal | ✅ Done |
| M10 — Production Deployment | ✅ Done |

See [`22_Future_Roadmap.md`](PRD%20Docs/22_Future_Roadmap.md) for what's next (v1.1 quality improvements, v1.2 software catalog, v2.0 multi-host scaling, v3.0 billing & marketplace).

## 📚 Documentation

The full specification lives in [`PRD Docs/`](PRD%20Docs/) — 22 documents covering the executive summary, system architecture, database design, security, REST API, UX, deployment, and the threat model:

- [`01A_Executive_Summary.md`](PRD%20Docs/01A_Executive_Summary.md) · [`02_System_Architecture.md`](PRD%20Docs/02_System_Architecture.md) · [`03_Database_Design.md`](PRD%20Docs/03_Database_Design.md) · [`04_Authentication_and_Security.md`](PRD%20Docs/04_Authentication_and_Security.md) · [`05_Container_Architecture.md`](PRD%20Docs/05_Container_Architecture.md) · [`07_REST_API.md`](PRD%20Docs/07_REST_API.md) · [`12_Deployment.md`](PRD%20Docs/12_Deployment.md) · [`17_Project_Task_Backlog.md`](PRD%20Docs/17_Project_Task_Backlog.md) (all 66 slices)

Operational guides:

- 🚀 [Local development](Code/README.md) — the one-command setup and the engineering rules
- 🌍 [Production deployment runbook](Code/deployment/README.md) — HTTPS, backups, restore, disaster recovery
- 📦 [User guide](Code/docs/USER_GUIDE.md) — software requests (valid package names) and persistent storage (retain/re-attach)
- ✅ [Milestone readiness audit](Code/docs/MILESTONE_READINESS_AUDIT.md) — the implementation evidence for every milestone

## 🛠️ Operations

| Task | Command |
|---|---|
| Start the stack | `./scripts/init_dev.sh` |
| Back up (database + desktop volumes) | `./scripts/backup.sh` |
| Restore from a backup | `./scripts/restore.sh backups/<timestamp>/` |
| Run the tests | `docker compose exec backend pytest -q` |

---

<div align="center">

**Desktop Cloud Platform** · v1.0.0 · built from spec, slice by slice

<img src="assets/icon.png" width="64" alt="Desktop Cloud Platform logo" />

</div>
