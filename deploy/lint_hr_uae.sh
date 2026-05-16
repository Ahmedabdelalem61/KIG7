#!/usr/bin/env bash
# Lint all first-party hr_uae_* addons (excludes thirdparty/ and manual_shell_* scripts).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HR="$ROOT/HrProject"
VENV="${ODOO_VENV:-$ROOT/../../../Odoo-Repos/Odoo-18/venv}"
PYLINTRC="${HR}/.pylintrc"
FLAKE8_CFG="${HR}/.flake8"

if [[ ! -x "$VENV/bin/pylint" ]]; then
  VENV="/home/ahmed/odoo-community-setup/Odoo-Repos/Odoo-18/venv"
fi

shopt -s nullglob
modules=("$HR"/hr_uae_*)
if [[ ${#modules[@]} -eq 0 ]]; then
  echo "No hr_uae_* modules under $HR"
  exit 1
fi

echo "== flake8 (${#modules[@]} modules) =="
"$VENV/bin/flake8" --config="$FLAKE8_CFG" "${modules[@]}"

echo "== pylint (block on E, F, W0611) =="
pylint_out="$("$VENV/bin/pylint" --rcfile="$PYLINTRC" --score=n "${modules[@]}" 2>&1)" || true
if grep -qE ': (E[0-9]+|F[0-9]+|W0611):' <<<"$pylint_out"; then
  echo "$pylint_out" | grep -E ': (E[0-9]+|F[0-9]+|W0611):'
  exit 1
fi
echo "pylint: no blocking issues (E / F / unused-import)."

echo "Lint OK."
