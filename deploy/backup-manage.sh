#!/usr/bin/env bash
# KIG7 online backup + retention (no restore). Safe while db/web/proxy are running.
#
# Usage:
#   backup-manage.sh daily          # scheduled / manual daily run
#   backup-manage.sh deploy         # before git pull / deploy
#   backup-manage.sh cleanup-only   # retention prune only
#   backup-manage.sh backup-only [tag]  # backup without retention (tag defaults to manual)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=backup-lib.sh
source "${SCRIPT_DIR}/backup-lib.sh"

usage() {
  echo "Usage: $(basename "$0") {daily|deploy|cleanup-only|backup-only [tag]}" >&2
  exit 1
}

write_manifest() {
  local trigger="$1"
  local dump_size fs_size
  dump_size="$(stat -c %s "${KIG7_SET_DIR}/db.dump" 2>/dev/null || echo 0)"
  fs_size="$(stat -c %s "${KIG7_SET_DIR}/filestore.tgz" 2>/dev/null || echo 0)"

  cat > "${KIG7_SET_DIR}/manifest.json" <<EOF
{
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "trigger": "${trigger}",
  "database": "${KIG7_DB_NAME}",
  "repo_root": "${KIG7_REPO_ROOT}",
  "git_commit": "${KIG7_GIT_COMMIT}",
  "git_branch": "${KIG7_GIT_BRANCH}",
  "git_dirty": ${KIG7_GIT_DIRTY},
  "files": {
    "db_dump": "db.dump",
    "filestore": "filestore.tgz"
  },
  "sizes_bytes": {
    "db_dump": ${dump_size},
    "filestore": ${fs_size}
  }
}
EOF
}

run_backup() {
  local trigger="$1"
  backup_log "backup start trigger=${trigger} db=${KIG7_DB_NAME}"
  backup_check_disk
  backup_require_compose_ready
  backup_git_metadata
  backup_new_set_dir "$trigger"

  backup_log "pg_dump -> ${KIG7_SET_DIR}/db.dump"
  docker compose exec -T db pg_dump -U odoo -Fc "$KIG7_DB_NAME" > "${KIG7_SET_DIR}/db.dump"

  if [[ ! -s "${KIG7_SET_DIR}/db.dump" ]]; then
    backup_log "ERROR: db.dump is empty"
    rm -rf "$KIG7_SET_DIR"
    return 1
  fi

  backup_log "filestore tar -> ${KIG7_SET_DIR}/filestore.tgz"
  if docker compose exec -T web test -d "/var/lib/odoo/filestore/${KIG7_DB_NAME}" 2>/dev/null; then
    docker compose exec -T web tar -czf - -C /var/lib/odoo/filestore "$KIG7_DB_NAME" \
      > "${KIG7_SET_DIR}/filestore.tgz" || {
        backup_log "WARN: filestore archive failed"
        rm -f "${KIG7_SET_DIR}/filestore.tgz"
      }
  else
    backup_log "WARN: filestore path missing in web container"
    rm -f "${KIG7_SET_DIR}/filestore.tgz"
  fi

  write_manifest "$trigger"
  backup_log "backup complete set=$(basename "$KIG7_SET_DIR")"
}

do_work() {
  local mode="${1:-}"
  shift || true

  case "$mode" in
    daily|deploy)
      run_backup "$mode"
      bash "${SCRIPT_DIR}/backup-retention.sh"
      ;;
    cleanup-only)
      bash "${SCRIPT_DIR}/backup-retention.sh"
      ;;
    backup-only)
      run_backup "${1:-manual}"
      ;;
    *)
      usage
      ;;
  esac
}

main() {
  [[ $# -ge 1 ]] || usage
  backup_lib_init
  backup_with_lock do_work "$@"
}

main "$@"
