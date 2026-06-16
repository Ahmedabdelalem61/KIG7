#!/usr/bin/env python3
"""Fingerprint non-transactional KIG7 master data in an Odoo database."""
# Standalone CLI utility (not an Odoo module): print output and terse helpers
# are intentional.
# pylint: disable=missing-function-docstring,print-used,raise-missing-from

import csv
import hashlib
import io
import json
import subprocess
import sys


def run_sql(db_name, sql):
    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "db",
        "psql",
        "-U",
        "odoo",
        "-d",
        db_name,
        "--csv",
        "--tuples-only",
        "-c",
        sql,
    ]
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def md5_text(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def row_key(row):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="")
    writer.writerow(["" if value is None else value for value in row])
    return out.getvalue()


def parse_rows(stdout):
    rows = []
    reader = csv.reader(io.StringIO(stdout))
    for row in reader:
        if row:
            rows.append(row)
    return sorted(rows, key=row_key)


def fingerprint(entity, db_name, sql, skip_on_missing=True):
    proc = run_sql(db_name, sql)
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        if skip_on_missing and "does not exist" in stderr:
            return {
                "entity": entity,
                "md5": None,
                "row_count": 0,
                "rows": [],
                "skipped": True,
            }
        raise RuntimeError(f"{entity}: {stderr}")

    rows = parse_rows(proc.stdout)
    joined = "\n".join(row_key(row) for row in rows)
    return {
        "entity": entity,
        "md5": md5_text(joined),
        "row_count": len(rows),
        "rows": rows,
        "skipped": False,
    }


def xlsx_templates(db_name):
    primary = fingerprint(
        "xlsx_templates",
        db_name,
        "SELECT name FROM hr_uae_xlsx_template ORDER BY name",
    )
    if not primary["skipped"]:
        return primary
    fallback = fingerprint(
        "xlsx_templates",
        db_name,
        "SELECT name FROM hr_uae_report_template ORDER BY name",
    )
    return fallback


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 deploy/checksum_master_data.py <DB_NAME>", file=sys.stderr)
        return 2

    db_name = argv[1]
    queries = [
        (
            "res_company",
            "SELECT name FROM res_company WHERE id=1 ORDER BY name",
            False,
        ),
        (
            "res_currency",
            "SELECT name FROM res_currency WHERE active=true ORDER BY name",
            False,
        ),
        (
            "hr_uae_rank",
            "SELECT code, name FROM hr_uae_rank ORDER BY code",
            True,
        ),
        (
            "hr_uae_position",
            "SELECT name FROM hr_uae_position ORDER BY name",
            True,
        ),
        (
            "hr_uae_employee_state",
            "SELECT code, name, color FROM hr_uae_employee_state ORDER BY code",
            True,
        ),
        (
            "hr_leave_type",
            "SELECT name->>'en_US' FROM hr_leave_type ORDER BY 1",
            True,
        ),
        (
            "resource_calendar",
            """
            SELECT
                rc.name,
                rc.hours_per_day,
                rc.tz,
                (
                    SELECT COUNT(*)
                    FROM resource_calendar_attendance rca
                    WHERE rca.calendar_id=rc.id
                ) AS att_count
            FROM resource_calendar rc
            WHERE rc.name ILIKE '%UAE%'
            ORDER BY rc.name
            """,
            True,
        ),
        (
            "resource_calendar_leaves",
            """
            SELECT name, date_from::date
            FROM resource_calendar_leaves
            WHERE calendar_id IS NULL
            ORDER BY date_from, name
            """,
            True,
        ),
        (
            "hr_payroll_structure",
            "SELECT code FROM hr_payroll_structure ORDER BY code",
            True,
        ),
        (
            "hr_salary_rule_category",
            "SELECT code, name->>'en_US' FROM hr_salary_rule_category ORDER BY code",
            True,
        ),
        (
            "hr_salary_rule",
            """
            SELECT
                hsr.code,
                (
                    SELECT hsrc.code
                    FROM hr_salary_rule_category hsrc
                    WHERE hsrc.id=hsr.category_id
                ) AS cat_code,
                hsr.sequence,
                hsr.amount_select,
                hsr.condition_select,
                hsr.appears_on_payslip,
                BTRIM(COALESCE(hsr.amount_python_compute, '')),
                BTRIM(COALESCE(hsr.condition_python, ''))
            FROM hr_salary_rule hsr
            ORDER BY hsr.code
            """,
            True,
        ),
        (
            "account_analytic_account",
            """
            SELECT aaa.name
            FROM account_analytic_account aaa
            JOIN ir_model_data imd
                ON imd.res_id=aaa.id
               AND imd.model='account.analytic.account'
               AND imd.module LIKE 'hr_uae%'
            ORDER BY aaa.name
            """,
            True,
        ),
        (
            "hr_department",
            "SELECT name->>'en_US' FROM hr_department ORDER BY 1",
            True,
        ),
        (
            "ir_sequence",
            """
            SELECT prefix
            FROM ir_sequence
            WHERE code LIKE 'hr.uae.%' OR code LIKE 'hr_uae%'
            ORDER BY code
            """,
            True,
        ),
        (
            "ir_cron",
            """
            SELECT ic.name, ic.interval_number, ic.interval_type
            FROM ir_cron ic
            JOIN ir_model_data imd
                ON imd.res_id=ic.id
               AND imd.model='ir.cron'
               AND imd.module LIKE 'hr_uae%'
            ORDER BY ic.name
            """,
            True,
        ),
        (
            "res_groups",
            """
            SELECT
                CASE
                    WHEN jsonb_typeof(to_jsonb(rg.name)) = 'object'
                    THEN to_jsonb(rg.name)->>'en_US'
                    ELSE trim(both '"' from to_jsonb(rg.name)::text)
                END AS name
            FROM res_groups rg
            JOIN ir_module_category imc ON imc.id=rg.category_id
            WHERE
                CASE
                    WHEN jsonb_typeof(to_jsonb(imc.name)) = 'object'
                    THEN to_jsonb(imc.name)->>'en_US'
                    ELSE trim(both '"' from to_jsonb(imc.name)::text)
                END IN ('KIG7 Access Rights','Human Resources UAE')
            ORDER BY 1
            """,
            True,
        ),
    ]

    entities = []
    for entity, sql, skip_on_missing in queries:
        entities.append(fingerprint(entity, db_name, sql, skip_on_missing))
    entities.append(xlsx_templates(db_name))

    overall_input = "\n".join(
        f"{entity['entity']}:{entity['md5'] or 'SKIP'}"
        for entity in sorted(entities, key=lambda item: item["entity"])
    )
    result = {
        "db": db_name,
        "entities": entities,
        "overall_md5": md5_text(overall_input),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
