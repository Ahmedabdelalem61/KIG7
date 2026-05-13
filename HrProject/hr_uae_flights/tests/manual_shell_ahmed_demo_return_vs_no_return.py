# Not collected by pytest. Creates demo data for Ahmed Abdelaleem:
#   A) Special leave abroad then **Returned** + outbound / return flight tickets.
#   B) Special leave abroad **not returned** + exit flight + **draft** UAE termination
#      (reason: Vacation - Did Not Return) — termination is NOT activated so the
#      employee stays active; HR can activate when appropriate.
#
# Persists to the database: an explicit ``env.cr.commit()`` runs at the end (no rollback).
# Re-running replaces any prior rows tagged with DEMO_AHMED_RTN (cleanup at start).
#
#   cd /home/ahmed/odoo-community-setup/Odoo-Repos/Odoo-18 && source venv/bin/activate
#   python odoo-bin shell --config=/home/ahmed/odoo-community-setup/Custom-Projects/Odoo-18/configs/hr_project.conf --no-http --log-level=error \
#     < /home/ahmed/odoo-community-setup/Custom-Projects/Odoo-18/HrProject/hr_uae_flights/tests/manual_shell_ahmed_demo_return_vs_no_return.py

from datetime import date, datetime

TAG = "DEMO_AHMED_RTN"
YEAR = 2055

Leave = env["hr.leave"].sudo()
Flight = env["hr.uae.flight"].sudo()
Term = env["hr.uae.termination"].sudo()
Employee = env["hr.employee"].sudo()


def commit_db():
    """Shell stdin mode may not auto-commit; persist demo data to the current DB."""
    env.cr.commit()


def log(msg):
    print("[AHMED-DEMO]", msg)


def cleanup():
    Term.sudo().search([("note", "ilike", TAG)]).unlink()
    test_leaves = Leave.search(
        ["|", ("private_name", "ilike", TAG), ("name", "ilike", TAG)]
    )
    for lv in test_leaves:
        if lv.state == "validate":
            lv.action_refuse()
        if lv.state == "refuse":
            lv.action_reset_confirm()
        if lv.state in ("confirm", "cancel"):
            lv.unlink()
    for f in Flight.search([("agency", "=", TAG)]):
        if f.booking_state == "booked":
            f.action_cancel()
        if f.expense_id and f.expense_id.state == "draft":
            f.expense_id.with_context(hr_uae_skip_audit=True).sudo().unlink()
        if f.booking_state != "draft":
            f.action_reset_to_draft()
        f.unlink()


cleanup()

candidates = Employee.search([("name", "ilike", "ahmed")], order="id")
emp = candidates.filtered(lambda e: "abdel" in (e.name or "").lower())[:1] or candidates[:1]
if not emp:
    raise SystemExit("No employee matching Ahmed — abort.")
log("employee: %s (id=%s)" % (emp.name, emp.id))

contract = emp.sudo().contract_ids.filtered(lambda c: c.state == "open")[:1]
if not contract:
    contract = emp.sudo().contract_id
if not contract or contract.state != "open":
    raise SystemExit("Ahmed needs an open contract for termination draft link.")
log("contract: %s" % contract.name)

lt_special = env.ref("hr_uae_leaves.leave_type_special")
uae = env.ref("base.ae")
india = env.ref("base.in", raise_if_not_found=False)
if not india:
    india = env["res.country"].sudo().search([("code", "!=", "AE")], limit=1)

# ----- Scenario A: came back -----
d0_a, d1_a = date(YEAR, 5, 12), date(YEAR, 5, 26)
leave_rt = Leave.create(
    {
        "name": "%s leave returned (special permit abroad)" % TAG,
        "employee_id": emp.id,
        "holiday_status_id": lt_special.id,
        "request_date_from": d0_a,
        "request_date_to": d1_a,
        "date_from": datetime(d0_a.year, d0_a.month, d0_a.day, 7, 0, 0),
        "date_to": datetime(d1_a.year, d1_a.month, d1_a.day, 19, 0, 0),
    }
)
leave_rt.action_validate()
leave_rt.invalidate_recordset()

# Outbound before leave starts; return after leave ends
f_out = Flight.create(
    {
        "employee_id": emp.id,
        "purpose": "vacation",
        "agency": TAG,
        "notes": "%s outbound before leave; employee later returned." % TAG,
        "from_country_id": uae.id,
        "to_country_id": india.id,
        "ticket_price": 1200.0,
        "extra_charges": 50.0,
        "departure_date": date(YEAR, 5, 8),
        "arrival_date": date(YEAR, 5, 8),
        "payment_mode": "company_account",
    }
)
f_out.action_book()

f_ret = Flight.create(
    {
        "employee_id": emp.id,
        "purpose": "vacation",
        "agency": TAG,
        "notes": "%s return after leave end; employee marked Returned on leave." % TAG,
        "from_country_id": india.id,
        "to_country_id": uae.id,
        "ticket_price": 1150.0,
        "departure_date": date(YEAR, 5, 28),
        "arrival_date": date(YEAR, 5, 28),
        "payment_mode": "company_account",
    }
)
f_ret.action_book()

leave_rt.write({"hr_uae_returned": True})
leave_rt.invalidate_recordset()
log(
    "Scenario A (returned): leave id=%s Returned=%s | flights %s (out) %s (return)"
    % (leave_rt.id, leave_rt.hr_uae_returned, f_out.name, f_ret.name)
)

# ----- Scenario B: did not return (draft termination only) -----
d0_b, d1_b = date(YEAR, 9, 5), date(YEAR, 9, 25)
leave_nr = Leave.create(
    {
        "name": "%s leave no return (still abroad / not returned)" % TAG,
        "employee_id": emp.id,
        "holiday_status_id": lt_special.id,
        "request_date_from": d0_b,
        "request_date_to": d1_b,
        "date_from": datetime(d0_b.year, d0_b.month, d0_b.day, 7, 0, 0),
        "date_to": datetime(d1_b.year, d1_b.month, d1_b.day, 19, 0, 0),
    }
)
leave_nr.action_validate()
leave_nr.invalidate_recordset()
ok_nr = not leave_nr.hr_uae_returned
if not ok_nr:
    log("warning: leave_nr unexpectedly has Returned set")

f_exit = Flight.create(
    {
        "employee_id": emp.id,
        "purpose": "termination",
        "agency": TAG,
        "notes": "%s exit ticket; linked narrative: leave without return → draft termination." % TAG,
        "from_country_id": uae.id,
        "to_country_id": india.id,
        "ticket_price": 900.0,
        "departure_date": date(YEAR, 9, 28),
        "payment_mode": "company_account",
    }
)
f_exit.action_book()

term = Term.sudo().create(
    {
        "employee_id": emp.id,
        "contract_id": contract.id,
        "departure_date": date(YEAR, 9, 30),
        "arrival_date": False,
        "reason": "vacation_no_return",
        "note": "%s Draft — vacation no return (leave id=%s). Do not activate until HR confirms."
        % (TAG, leave_nr.id),
    }
)
term.invalidate_recordset()
log(
    "Scenario B (no return): leave id=%s Returned=%s | flight %s | draft termination %s (state=%s)"
    % (leave_nr.id, leave_nr.hr_uae_returned, f_exit.name, term.name, term.state)
)

log("Done. Search flights with agency containing %r; leaves/termination note containing %r." % (TAG, TAG))
log("To remove this demo later, re-run this file after replacing the body with a cleanup-only script, or delete records manually.")

commit_db()
log("Committed to database %r — refresh the UI to see leaves, flights, and termination." % env.cr.dbname)
