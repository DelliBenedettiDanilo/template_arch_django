#!/bin/sh
set -e

# -----------------------------------------------------------------------------
# Simple logging helper
# -----------------------------------------------------------------------------
log() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] [entrypoint] $*"
}

# -----------------------------------------------------------------------------
# Wait for database (optional, based on DJANGO_DB_HOST/PORT)
# -----------------------------------------------------------------------------
wait_for_db() {
  if [ -n "${DJANGO_DB_HOST:-}" ] && [ -n "${DJANGO_DB_PORT:-}" ]; then
    log "Waiting for database at ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}..."
    # nc (netcat) is commonly available; if not, you can replace with python or pg_isready
    until nc -z "${DJANGO_DB_HOST}" "${DJANGO_DB_PORT}"; do
      sleep 1
    done
    log "Database is reachable."
  else
    log "DJANGO_DB_HOST or DJANGO_DB_PORT not set, skipping database wait."
  fi
}

# -----------------------------------------------------------------------------
# Apply migrations
# -----------------------------------------------------------------------------
log "Applying database migrations..."
wait_for_db
python manage.py migrate --noinput
log "Migrations applied."

# -----------------------------------------------------------------------------
# Collect static files (controlled via DJANGO_COLLECTSTATIC)
# -----------------------------------------------------------------------------
COLLECTSTATIC_FLAG=$(echo "${DJANGO_COLLECTSTATIC:-true}" | tr '[:upper:]' '[:lower:]')
if [ "$COLLECTSTATIC_FLAG" = "true" ]; then
  log "Collecting static files..."
  python manage.py collectstatic --noinput
  log "Static files collected."
else
  log "Skipping collectstatic (DJANGO_COLLECTSTATIC=${DJANGO_COLLECTSTATIC:-false})."
fi

# -----------------------------------------------------------------------------
# Django deploy checks (production only)
# -----------------------------------------------------------------------------
if [ "${DJANGO_ENVIRONMENT:-development}" = "production" ]; then
  log "Running Django deploy checks..."
  # Non blocchiamo l'avvio se falliscono, ma logghiamo l'esito
  if python manage.py check --deploy; then
    log "Django deploy checks passed."
  else
    log "WARNING: Django deploy checks reported issues. Review configuration before going live."
  fi
fi

# -----------------------------------------------------------------------------
# Start application (delegated to CMD/command)
# -----------------------------------------------------------------------------
log "Starting application with command: $*"
exec "$@"