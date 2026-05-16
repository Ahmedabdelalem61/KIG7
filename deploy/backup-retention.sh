#!/usr/bin/env bash
# Prune backup sets older than KIG7_RETENTION_DAYS; always keep the newest set.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=backup-lib.sh
source "${SCRIPT_DIR}/backup-lib.sh"

backup_lib_init

prune_sets() {
  local sets=() dir age_secs cutoff deleted=0 kept=0

  if [[ ! -d "$KIG7_BACKUP_SETS" ]]; then
    backup_log "retention: no sets directory ($KIG7_BACKUP_SETS)"
    return 0
  fi

  mapfile -t sets < <(find "$KIG7_BACKUP_SETS" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null | sort -rn | cut -d' ' -f2-)
  if [[ ${#sets[@]} -eq 0 ]]; then
    backup_log "retention: no backup sets to prune"
    return 0
  fi

  cutoff=$((KIG7_RETENTION_DAYS * 86400))
  local newest="${sets[0]}"
  backup_log "retention: newest set (always kept): $(basename "$newest")"

  for dir in "${sets[@]}"; do
    if [[ "$dir" == "$newest" ]]; then
      kept=$((kept + 1))
      continue
    fi
    age_secs=$(( $(date +%s) - $(stat -c %Y "$dir") ))
    if [[ "$age_secs" -gt "$cutoff" ]]; then
      backup_log "retention: removing $(basename "$dir") (age ${age_secs}s > ${cutoff}s)"
      rm -rf "$dir"
      deleted=$((deleted + 1))
    else
      kept=$((kept + 1))
    fi
  done

  backup_log "retention: done (deleted=$deleted kept=$kept newest preserved)"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  prune_sets
fi
