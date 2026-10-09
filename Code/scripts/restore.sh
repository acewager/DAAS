#!/usr/bin/env bash
# Restore procedure (VS-060, M10): restores the PostgreSQL database and the
# persistent desktop volumes from a backup made by scripts/backup.sh.
#
# Usage:
#   ./scripts/restore.sh backups/20261009-020000/
#
# The stack should be STOPPED (or at least postgres) before restoring:
#   docker compose down
#   ./scripts/restore.sh <backup-dir>
#   ./scripts/init_dev.sh     # or docker compose up -d
set -euo pipefail
cd "$(dirname "$0")/.." # always operate from the Code/ directory

BACKUP_DIR="${1:-}"
if [ -z "$BACKUP_DIR" ] || [ ! -f "$BACKUP_DIR/database.sql.gz" ]; then
  echo "Usage: ./scripts/restore.sh <backup-dir containing database.sql.gz>" >&2
  echo "       e.g. ./scripts/restore.sh backups/20261009-020000/" >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running." >&2
  exit 1
fi

cat "$BACKUP_DIR/manifest.txt" 2>/dev/null || echo "(no manifest found)"

echo "==> Restoring the PostgreSQL database..."
# Recreate the database for a clean restore.
docker compose up -d postgres
sleep 3
docker compose exec -T postgres psql -U "${POSTGRES_USER:-dcp}" -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${POSTGRES_DB:-dcp}' AND pid <> pg_backend_pid();" >/dev/null
docker compose exec -T postgres psql -U "${POSTGRES_USER:-dcp}" -d postgres -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB:-dcp}\";" >/dev/null
docker compose exec -T postgres psql -U "${POSTGRES_USER:-dcp}" -d postgres -c "CREATE DATABASE \"${POSTGRES_DB:-dcp}\";" >/dev/null
gunzip -c "$BACKUP_DIR/database.sql.gz" | docker compose exec -T postgres psql -U "${POSTGRES_USER:-dcp}" -d "${POSTGRES_DB:-dcp}" >/dev/null
echo "    database restored."

echo "==> Restoring persistent desktop volumes..."
for archive in "$BACKUP_DIR"/dcp-data-*.tar.gz; do
  [ -f "$archive" ] || { echo "    (no volume archives found)"; break; }
  volume=$(basename "$archive" .tar.gz)
  docker volume create "$volume" >/dev/null
  docker run --rm -v "$volume":/data -v "$(cd "$BACKUP_DIR" && pwd)":/backup:ro alpine \
    sh -c "tar xzf /backup/$(basename "$archive") -C /data"
  echo "    ${volume} restored."
done

echo "==> Restore complete. Restart the stack with:"
echo "    ./scripts/init_dev.sh   # or: docker compose up -d"
