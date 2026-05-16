#!/usr/bin/env bash
# Shared helpers for KIG7 backup management (sourced, not executed directly).
set -euo pipefail

KIG7_BACKUP_ROOT="${KIG7_BACKUP_ROOT:-/var/backups/kig7-odoo18}"
KIG7_BACKUP_SETS="${KIG7_BACKUP_SETS:-${KIG7_BACKUP_ROOT}/sets}"
KIG7_BACKUP_LOGS="${KIG7_BACKUP_LOGS:-${KIG7_BACKUP_ROOT}/logs}"
KIG7_BACKUP_LOCK="${KIG7_BACKUP_LOCK:-${KIG7_BACKUP_ROOT}/.backup.lock}"
KIG7_RETENTION_DAYS="${KIG7_RETENTION_DAYS:-7}"
KIG7_MIN_FREE_MB="${KIG7_MIN_FREE_MB:-2048}"

backup_lib_init() {
  local root
  root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  KIG7_REPO_ROOT="$root"
  cd "$KIG7_REPO_ROOT"

  KIG7_ODOO_CONF="${KIG7_ODOO_CONF:-${KIG7_REPO_ROOT}/configs/docker.odoo.conf}"
  if [[ ! -f "$KIG7_ODOO_CONF" ]]; then
    echo "Missing Odoo config: $KIG7_ODOO_CONF" >&2
    return 1
  fi

  KIG7_DB_NAME="$(awk -F= '/^[[:space:]]*db_name[[:space:]]*=/ { gsub(/[[:space:]]/, "", $2); print $2; exit }' "$KIG7_ODOO_CONF")"
  if [[ -z "${KIG7_DB_NAME:-}" ]]; then
    echo "Could not read db_name from $KIG7_ODOO_CONF" >&2
    return 1
  fi

  mkdir -p "$KIG7_BACKUP_SETS" "$KIG7_BACKUP_LOGS"
  chmod 700 "$KIG7_BACKUP_ROOT" 2>/dev/null || true
}

backup_log() {
  local msg="[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
  echo "$msg"
  echo "$msg" >> "${KIG7_BACKUP_LOGS}/backup-manage.log"
}

backup_require_compose_ready() {
  if ! docker compose version >/dev/null 2>&1; then
    backup_log "ERROR: docker compose not available"
    return 1
  fi
  if ! docker compose ps --status running 2>/dev/null | grep -q 'db'; then
    backup_log "ERROR: db service is not running"
    return 1
  fi
  local i
  for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready -U odoo -d postgres >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  backup_log "ERROR: Postgres not ready after 30s"
  return 1
}

backup_check_disk() {
  local avail_mb
  avail_mb="$(df -Pm "$KIG7_BACKUP_ROOT" 2>/dev/null | awk 'NR==2 {print $4}')"
  if [[ -z "$avail_mb" ]]; then
    avail_mb="$(df -Pm /var/backups 2>/dev/null | awk 'NR==2 {print $4}')"
  fi
  if [[ -n "$avail_mb" && "$avail_mb" -lt "$KIG7_MIN_FREE_MB" ]]; then
    backup_log "WARN: low disk space (${avail_mb}MB free, want >= ${KIG7_MIN_FREE_MB}MB)"
  fi
}

backup_git_metadata() {
  KIG7_GIT_COMMIT="unknown"
  KIG7_GIT_BRANCH="unknown"
  KIG7_GIT_DIRTY="false"
  if [[ -d "${KIG7_REPO_ROOT}/.git" ]]; then
    KIG7_GIT_COMMIT="$(git -C "$KIG7_REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
    KIG7_GIT_BRANCH="$(git -C "$KIG7_REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
    if [[ -n "$(git -C "$KIG7_REPO_ROOT" status --porcelain 2>/dev/null)" ]]; then
      KIG7_GIT_DIRTY="true"
    fi
  fi
}

backup_new_set_dir() {
  local trigger="${1:-daily}"
  local ts
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  KIG7_SET_DIR="${KIG7_BACKUP_SETS}/${ts}-${trigger}"
  mkdir -p "$KIG7_SET_DIR"
}

backup_with_lock() {
  local rc=0
  exec 9>"$KIG7_BACKUP_LOCK"
  if ! flock -n 9; then
    backup_log "ERROR: another backup is already running (lock: $KIG7_BACKUP_LOCK)"
    return 2
  fi
  "$@" || rc=$?
  return "$rc"
}
