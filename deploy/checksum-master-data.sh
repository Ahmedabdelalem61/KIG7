#!/usr/bin/env bash
set -euo pipefail

DB1="${1:-18c_hr_project_test}"
DB2="${2:-kig7_init_probe}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP1="$(mktemp)"
TMP2="$(mktemp)"
trap 'rm -f "$TMP1" "$TMP2"' EXIT

python3 "$ROOT/deploy/checksum_master_data.py" "$DB1" >"$TMP1"
python3 "$ROOT/deploy/checksum_master_data.py" "$DB2" >"$TMP2"

python3 - "$TMP1" "$TMP2" <<'PY'
import json
import sys

left_path, right_path = sys.argv[1:3]
left = json.load(open(left_path, encoding="utf-8"))
right = json.load(open(right_path, encoding="utf-8"))

left_entities = {item["entity"]: item for item in left["entities"]}
right_entities = {item["entity"]: item for item in right["entities"]}
names = sorted(set(left_entities) | set(right_entities))

print(f"DB1: {left['db']} overall={left['overall_md5']}")
print(f"DB2: {right['db']} overall={right['overall_md5']}")
print()
print(f"{'Entity':32} {'DB1 Rows':>8} {'DB2 Rows':>8} {'Status':>8}")
print("-" * 62)

failed = False
diffs = []
for name in names:
    l_item = left_entities.get(name)
    r_item = right_entities.get(name)
    l_skip = not l_item or l_item.get("skipped")
    r_skip = not r_item or r_item.get("skipped")
    if l_skip or r_skip:
        status = "SKIP" if l_skip and r_skip else "FAIL"
    elif l_item["md5"] == r_item["md5"]:
        status = "PASS"
    else:
        status = "FAIL"

    if status == "FAIL":
        failed = True
        diffs.append((name, l_item, r_item))

    l_count = "-" if l_skip else str(l_item["row_count"])
    r_count = "-" if r_skip else str(r_item["row_count"])
    print(f"{name:32} {l_count:>8} {r_count:>8} {status:>8}")

if diffs:
    print()
    print("Differing rows:")
    for name, l_item, r_item in diffs:
        print(f"\n## {name}")
        print(f"-- {left['db']}")
        for row in (l_item or {}).get("rows", []):
            print(json.dumps(row, ensure_ascii=False))
        print(f"-- {right['db']}")
        for row in (r_item or {}).get("rows", []):
            print(json.dumps(row, ensure_ascii=False))

sys.exit(1 if failed else 0)
PY
