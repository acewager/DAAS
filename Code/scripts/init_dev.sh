#!/usr/bin/env bash
# Bootstraps a fresh local environment.
# Usage: ./scripts/init_dev.sh
set -euo pipefail

if [ ! -f .env ]; then
  echo "Creating .env from .env.example"
  cp .env.example .env
fi

echo "Building images..."
docker compose build

echo "Starting core services..."
docker compose up -d postgres redis

echo "Waiting for Postgres to be healthy..."
until [ "$(docker compose ps -q postgres | xargs docker inspect -f '{{.State.Health.Status}}')" = "healthy" ]; do
  sleep 1
done

echo "Running migrations..."
docker compose run --rm backend python manage.py migrate

echo "Starting full stack..."
docker compose up -d

cat <<MSG

Done. Add these to /etc/hosts if not already present:
  127.0.0.1 app.localhost api.localhost

  Frontend:          http://app.localhost
  Backend API:       http://api.localhost/api/v1/health/
  Traefik dashboard: http://localhost:8080

Create an admin user with:
  docker compose exec backend python manage.py createsuperuser
MSG
