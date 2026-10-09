#!/usr/bin/env bash
# Automated backup (VS-059, M10): the PostgreSQL database and every
# persistent desktop volume.
#
# Usage:
#   ./scripts/backup.sh                 # back up to ./backups/<timestamp>/
#   BACKUP_DIR=/srv/backups ./scripts/backup.sh
#   KEEP_DAYS=14 ./scripts/backup.sh    # prune older backups (default 7)
#
# Schedule it with cron, e.g. daily at 02:00:
#   0 2 * * * cd /srv/DAAS/Code && ./scripts/backup.sh >> /var/log/dcp-backup.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.." # always operate from the Code/ directory

BACKUP_DIR="${BACKUP_DIR:-./backups}/$(date +%Y%m%d-%H%M%S)"
KEEP_DAYS="${KEEP_DAYS:-7}"
mkdir -p "$BACKUP_DIR"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running." >&2
  exit 1
fi

echo "==> Backing up the PostgreSQL database..."
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-dcp}" "${POSTGRES_DB:-dcp}" | gzip > "$BACKUP_DIR/database.sql.gz"
echo "    database.sql.gz: $(du -h "$BACKUP_DIR/database.sql.gz" | cut -f1)"

echo "==> Backing up persistent desktop volumes..."
VOLUMES=$(docker volume ls -q | grep "^dcp-data-" || true)
if [ -n "$VOLUMES" ]; then
  for volume in $VOLUMES; do
    # Pack the volume's contents with a temporary helper container.
    docker run --rm -v "$volume":/data:ro -v "$(cd "$BACKUP_DIR" && pwd)":/backup alpine \
      tar czf "/backup/${volume}.tar.gz" -C /data .
    echo "    ${volume}.tar.gz: $(du -h "$BACKUP_DIR/${volume}.tar.gz" | cut -f1)"
  done
else
  echo "    (no persistent volumes found)"
fi

echo "==> Writing a manifest..."
{
  echo "backup: $(date -Iseconds)"
  echo "host: $(hostname)"
  echo "database: ${POSTGRES_DB:-dcp}"
  echo "volumes:"
  [ -n "$VOLUMES" ] && echo "$VOLUMES" | sed 's/^/  - /' || echo "  (none)"
} > "$BACKUP_DIR/manifest.txt"

echo "==> Pruning backups older than ${KEEP_DAYS} days..."
find "$(dirname "$BACKUP_DIR")" -maxdepth 1 -type d -name "20*" -mtime +"$KEEP_DAYS" -exec rm -rf {} \; 2>/dev/null || true

echo "==> Backup complete: $BACKUP_DIR"
