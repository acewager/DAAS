#!/usr/bin/env bash
# One-command local startup for the whole platform.
#
# Usage:
#   ./scripts/init_dev.sh          # bring the stack up (idempotent — safe to re-run)
#
# Requires Docker and Docker Compose on a Linux host (or a Linux VM — see
# 12_Deployment.md Section 5). Configuration comes from .env (created from
# .env.example on first run).
set -euo pipefail
cd "$(dirname "$0")/.." # always operate from the Code/ directory

if [ ! -f .env ]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running. Start Docker Engine and try again." >&2
  exit 1
fi

echo "==> Building images (cached after the first run)..."
docker compose build

echo "==> Starting core services (postgres, redis)..."
docker compose up -d postgres redis

echo "==> Waiting for Postgres and Redis to be healthy..."
until [ "$(docker compose ps -q postgres | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null)" = "healthy" ] \
  && [ "$(docker compose ps -q redis | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null)" = "healthy" ]; do
  sleep 2
done

echo "==> Applying migrations..."
docker compose run --rm backend python manage.py migrate

echo "==> Seeding development templates..."
docker compose run --rm backend python manage.py seed_templates

echo "==> Starting the full stack (backend, celery, frontend, traefik)..."
docker compose up -d

echo "==> Waiting for the backend health check..."
HEALTH_URL="http://api.localhost/api/v1/health/"
for _ in $(seq 1 30); do
  if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
    echo "    Backend healthy."
    break
  fi
  sleep 2
done

if ! grep -q "app.localhost" /etc/hosts 2>/dev/null || ! grep -q "api.localhost" /etc/hosts 2>/dev/null; then
  echo ""
  echo "WARNING: /etc/hosts is missing the local routing entries. Add them with:"
  echo "  echo '127.0.0.1 app.localhost api.localhost' | sudo tee -a /etc/hosts"
fi

cat <<MSG

==> Done. The platform is up.

    Frontend:          http://app.localhost
    Backend API:       http://api.localhost/api/v1/health/
    Django admin:      http://api.localhost/admin/
    Traefik dashboard: http://localhost:8080 (dev only)

    Create an admin user:
      docker compose exec backend python manage.py createsuperuser

    Stop everything:
      docker compose down
MSG
