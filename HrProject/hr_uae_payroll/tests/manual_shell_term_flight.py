# Not collected by pytest. Run with odoo shell (expects ``env``):
#
#   cd /home/ahmed/odoo-community-setup/Odoo-Repos/Odoo-18 && source venv/bin/activate
#   python odoo-bin shell --config=/home/ahmed/odoo-community-setup/Custom-Projects/Odoo-18/configs/hr_project.conf --no-http --log-level=error \
#     < /home/ahmed/odoo-community-setup/Custom-Projects/Odoo-18/HrProject/hr_uae_payroll/tests/manual_shell_term_flight.py
#
# Covers: (1) hr.uae.termination + payslip cancellation, (2) FLIGHT_DED payroll input,
# (3) hr.uae.flight booking / expense / cancel. Uses disposable employees for (1)-(2);
# flight markers use employee Ahmed + agency marker TAG.

from calendar import monthrange
from datetime import date, timedelta

TAG = "__UAE_SHELL_TERM_FLIGHT__"
YEAR_TERM = 2045
YEAR_DED = 2046
YEAR_FLIGHT = 2047

Employee = env["hr.employee"].sudo()
Contract = env["hr.contract"].sudo()
Pay = env["hr.payslip"].sudo()
PayInput = env["hr.payslip.input"].sudo()
Term = env["hr.uae.termination"].sudo()
Flight = env["hr.uae.flight"].sudo()


def log(msg):
    print("[UAE-TERM-FLIGHT-SHELL]", msg)


def ok(cond, msg):
    if not cond:
        raise AssertionError(msg)


def month_end(y, m):
    return date(y, m, monthrange(y, m)[1])


def default_calendar():
    cal = env.ref("resource.resource_calendar_std", raise_if_not_found=False)
    if cal:
        return cal
    return env.company.resource_calendar_id


def unlink_all_payslips_for_employee(emp):
    """Payslips may only be deleted in draft or cancel (thirdparty payroll)."""
    for p in Pay.search([("employee_id", "=", emp.id)]):
        if p.state == "done":
            p.action_payslip_draft()
        elif p.state in ("verify", "on_hold"):
            p.action_payslip_draft()
        elif p.state not in ("draft", "cancel"):
            p.action_payslip_cancel()
        p.unlink()


def cleanup_tagged():
    """Best-effort cleanup from prior failed runs."""
    for name_pat in (TAG + "%", "%" + TAG + "%"):
        for e in Employee.search([("name", "ilike", name_pat)]):
            for t in Term.search([("employee_id", "=", e.id)]):
                if t.state == "active":
                    t.action_close()
                t.unlink()
            unlink_all_payslips_for_employee(e)
            for c in e.contract_ids:
                end_ok = c.date_start + timedelta(days=30)
                c.write({"state": "close", "date_end": end_ok})
                c.unlink()
            e.unlink()
    for f in Flight.search([("agency", "=", TAG)]):
        if f.booking_state == "booked":
            f.action_cancel()
        if f.expense_id and f.expense_id.state == "draft":
            f.expense_id.with_context(hr_uae_skip_audit=True).sudo().unlink()
        f.sudo().unlink()


def restore_term_employee(emp, contract, term):
    """Undo termination effects for disposable test employee."""
    if term.exists():
        if term.state == "active":
            term.action_close()
        term.unlink()
    unlink_all_payslips_for_employee(emp)
    contract.write({"state": "open", "date_end": False})
    emp.write(
        {
            "active": True,
            "hr_uae_status_manual": False,
        }
    )
    emp.invalidate_recordset()


results = []

try:
    cleanup_tagged()

    struct = env.ref("hr_uae_payroll.hr_payroll_structure_uae")
    cal = default_calendar()
    ok(cal, "Need a resource calendar on company or resource.resource_calendar_std")

    # ----- Disposable employee for termination -----
    emp_t = Employee.create({"name": "%s TermPay" % TAG})
    c_t = Contract.create(
        {
            "name": "%s C1" % TAG,
            "employee_id": emp_t.id,
            "wage": 4000.0,
            "date_start": date(YEAR_TERM, 1, 1),
            "state": "open",
            "struct_id": struct.id,
            "resource_calendar_id": cal.id,
        }
    )
    emp_t.contract_id = c_t

    slip_draft = Pay.create(
        {
            "name": "%s slip draft" % TAG,
            "employee_id": emp_t.id,
            "contract_id": c_t.id,
            "struct_id": struct.id,
            "date_from": date(YEAR_TERM, 6, 1),
            "date_to": month_end(YEAR_TERM, 6),
        }
    )
    slip_verify = Pay.create(
        {
            "name": "%s slip verify" % TAG,
            "employee_id": emp_t.id,
            "contract_id": c_t.id,
            "struct_id": struct.id,
            "date_from": date(YEAR_TERM, 7, 1),
            "date_to": month_end(YEAR_TERM, 7),
        }
    )
    slip_verify.compute_sheet()
    slip_done = Pay.create(
        {
            "name": "%s slip done" % TAG,
            "employee_id": emp_t.id,
            "contract_id": c_t.id,
            "struct_id": struct.id,
            "date_from": date(YEAR_TERM, 8, 1),
            "date_to": month_end(YEAR_TERM, 8),
        }
    )
    slip_done.compute_sheet()
    slip_done.with_context(without_compute_sheet=True).action_payslip_done()

    term = Term.create(
        {
            "employee_id": emp_t.id,
            "contract_id": c_t.id,
            "departure_date": date(YEAR_TERM, 6, 15),
            "reason": "resignation",
        }
    )
    term.action_activate()
    term.invalidate_recordset()
    slip_draft.invalidate_recordset()
    slip_verify.invalidate_recordset()
    slip_done.invalidate_recordset()
    c_t.invalidate_recordset()
    emp_t.invalidate_recordset()

    ok(term.state == "active", "termination state")
    ok(slip_draft.state == "cancel", "draft slip cancelled got %s" % slip_draft.state)
    ok(slip_verify.state == "cancel", "verify slip cancelled got %s" % slip_verify.state)
    ok(slip_done.state == "done", "done slip unchanged got %s" % slip_done.state)
    ok(c_t.state == "close", "contract closed")
    ok(not emp_t.active, "employee archived")
    ok(emp_t.hr_uae_status == "terminated", "UAE status terminated")
    results.append("P1 termination cancels editable payslips; preserves done")

    restore_term_employee(emp_t, c_t, term)

    # ----- FLIGHT_DED on separate disposable employee -----
    emp_d = Employee.create({"name": "%s Ded" % TAG})
    c_d = Contract.create(
        {
            "name": "%s C2" % TAG,
            "employee_id": emp_d.id,
            "wage": 3000.0,
            "date_start": date(YEAR_DED, 1, 1),
            "state": "open",
            "struct_id": struct.id,
            "resource_calendar_id": cal.id,
        }
    )
    emp_d.contract_id = c_d
    slip_d = Pay.create(
        {
            "name": "%s slip ded" % TAG,
            "employee_id": emp_d.id,
            "contract_id": c_d.id,
            "struct_id": struct.id,
            "date_from": date(YEAR_DED, 3, 1),
            "date_to": month_end(YEAR_DED, 3),
        }
    )
    PayInput.create(
        {
            "payslip_id": slip_d.id,
            "contract_id": c_d.id,
            "name": "Flight deduction (test)",
            "code": "FLIGHT_DED",
            "amount": 750.0,
            "sequence": 90,
        }
    )
    slip_d.compute_sheet()
    slip_d.invalidate_recordset()
    flight_line = slip_d.line_ids.filtered(lambda l: l.code == "FLIGHT_DED")
    ok(flight_line, "FLIGHT_DED payslip line missing")
    ok(abs(flight_line[:1].total + 750.0) < 0.02, "FLIGHT_DED total %s" % flight_line[:1].total)
    basic_line = slip_d.line_ids.filtered(lambda l: l.code == "BASIC")
    net_line = slip_d.line_ids.filtered(lambda l: l.code == "NET")
    ok(basic_line and net_line, "BASIC/NET lines")
    ok(abs(net_line[:1].total - (basic_line[:1].total - 750.0)) < 0.02, "NET mismatch")
    results.append("P2 FLIGHT_DED input reduces net on UAE structure")

    unlink_all_payslips_for_employee(emp_d)
    c_d.unlink()
    emp_d.unlink()

    # ----- Flight tickets (Ahmed + agency marker) -----
    ahmed = Employee.search([("name", "ilike", "ahmed")], limit=1)
    ok(ahmed, "No employee ilike 'ahmed' for flight tests")
    ae = ahmed[:1]
    uae = env.ref("base.ae")
    usc = env.ref("base.us")

    f1 = Flight.create(
        {
            "employee_id": ae.id,
            "ticket_price": 400.0,
            "extra_charges": 25.0,
            "departure_date": date(YEAR_FLIGHT, 2, 10),
            "agency": TAG,
            "purpose": "termination",
            "from_country_id": uae.id,
            "to_country_id": usc.id,
            "payment_mode": "company_account",
        }
    )
    ok(abs(f1.total - 425.0) < 0.01, "flight total")
    f1.action_book()
    f1.invalidate_recordset()
    ok(f1.booking_state == "booked", "booking state")
    ok(f1.expense_id, "linked expense")
    ok(abs(f1.expense_id.total_amount_currency - 425.0) < 0.01, "expense amount")
    ok(f1.expense_id.payment_mode == "company_account", "expense payment_mode company")
    results.append("P3 flight book creates expense (company pays)")

    f2 = Flight.create(
        {
            "employee_id": ae.id,
            "ticket_price": 200.0,
            "departure_date": date(YEAR_FLIGHT, 3, 5),
            "agency": TAG,
            "payment_mode": "own_account",
        }
    )
    f2.action_book()
    f2.invalidate_recordset()
    ok(f2.expense_id.payment_mode == "own_account", "own_account on expense")
    results.append("P4 own_account maps to expense reimbursement mode")

    f3 = Flight.create(
        {
            "employee_id": ae.id,
            "ticket_price": 100.0,
            "departure_date": date(YEAR_FLIGHT, 4, 1),
            "agency": TAG,
        }
    )
    f3.action_book()
    exp = f3.expense_id
    f3.action_cancel()
    f3.invalidate_recordset()
    ok(f3.booking_state == "cancelled", "cancelled state")
    ok(not f3.expense_id, "expense cleared")
    ok(not exp.exists(), "expense row removed")
    results.append("P5 cancel removes draft expense link")

    for f in Flight.search([("agency", "=", TAG)]):
        if f.expense_id and f.expense_id.state == "draft":
            f.expense_id.with_context(hr_uae_skip_audit=True).sudo().unlink()
        if f.booking_state != "draft":
            f.action_reset_to_draft()
        f.unlink()

finally:
    cleanup_tagged()

log("--- ALL CASES PASSED ---")
for r in results:
    log("PASS: %s" % r)
