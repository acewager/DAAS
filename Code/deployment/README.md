# Production Deployment Runbook (M10)

How to deploy the platform on a production Ubuntu server. See the full
specification in `12_Deployment.md` and the architecture documents.

## 1. Server requirements

- Ubuntu 22.04+ with Docker Engine and Docker Compose v2
- A domain (e.g. `platform.example.com`) with an A/AAAA record pointing at
  the server — wildcard `*.platform.example.com` is recommended so desktop
  subdomains resolve without extra DNS records
- Ports 80 and 443 open (Let's Encrypt HTTP-01 challenge + HTTPS)

## 2. Configure

```bash
git clone <this-repo> && cd DAAS/Code
cp .env.production.example .env.production
```

Edit `.env.production`:

- `SECRET_KEY` — a strong random value (required; the server refuses to
  start without one):
  `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `TRAEFIK_DOMAIN` — the platform domain (desktop subdomains derive from it)
- `ACME_EMAIL` — the Let's Encrypt certificate contact
- `POSTGRES_PASSWORD` — a strong database password
- `SENTRY_DSN` (optional) — error tracking

## 3. Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

That starts postgres, redis, the backend (gunicorn + migrations +
collectstatic), the celery worker/beat, the frontend (nginx serving the
production bundle), and Traefik (HTTPS via Let's Encrypt).

## 4. Verify (VS-064)

```bash
docker compose -f docker-compose.prod.yml ps
curl -fsS https://<domain>/api/v1/health/ | grep '"healthy"'
docker compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
docker compose -f docker-compose.prod.yml logs backend | grep -i error
```

- HTTPS is served with a valid certificate; HTTP redirects to HTTPS
- Create an admin: `docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser`
- Seed templates: `docker compose -f docker-compose.prod.yml exec backend python manage.py seed_templates`
- Register a user, create an instance, launch the desktop at
  `https://<hash>.<domain>/` — the ForwardAuth validates the session

## 5. Backups and restore (VS-059/VS-060)

```bash
# Daily at 02:00 with 14-day retention (cron):
0 2 * * * cd /srv/DAAS/Code && ./scripts/backup.sh >> /var/log/dcp-backup.log 2>&1

# Manual backup / restore:
./scripts/backup.sh
docker compose -f docker-compose.prod.yml down
./scripts/restore.sh backups/<timestamp>/
./scripts/init_dev.sh   # or: docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

Backups include the database dump and every persistent desktop volume, with
a manifest and retention pruning.

## 6. Monitoring and logging (VS-058)

- `GET /api/v1/admin/health/` — database/Redis/Docker checks (admin session)
- Traefik access logs on stdout (`docker compose logs traefik`)
- Sentry error tracking when `SENTRY_DSN` is configured

## 7. Disaster recovery

1. Provision a fresh server (Section 1) and restore DNS
2. Configure `.env.production` (the same `SECRET_KEY` and `TRAEFIK_DOMAIN`
   keep sessions and desktop hashes valid)
3. Restore from the latest backup (Section 5)
4. Verify (Section 4)

## 8. Security review summary (VS-061)

- `DEBUG=False`, strict `ALLOWED_HOSTS`, HSTS (preload + subdomains),
  SSL redirect, secure/HttpOnly SameSite=Strict cookies
- A strong `SECRET_KEY` is enforced at startup
- No database/Redis ports exposed; the Traefik dashboard is disabled
- The Docker socket is mounted read-only into backend/celery only
- Desktop access is ForwardAuth-guarded (owner + RUNNING only)
- Package installation validates names strictly (no shell, no
  metacharacters)
- `python manage.py check --deploy` passes with zero warnings
