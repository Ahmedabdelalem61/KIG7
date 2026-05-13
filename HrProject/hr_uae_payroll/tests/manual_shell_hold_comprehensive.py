# Not collected by pytest. Run with odoo shell stdin (expects ``env``):
#
#   cd /home/ahmed/odoo-community-setup/Odoo-Repos/Odoo-18 && source venv/bin/activate
#   python odoo-bin shell --config=/home/ahmed/odoo-community-setup/Custom-Projects/Odoo-18/configs/hr_project.conf --no-http --log-level=error \
#     < /home/ahmed/odoo-community-setup/Custom-Projects/Odoo-18/HrProject/hr_uae_payroll/tests/manual_shell_hold_comprehensive.py
#
# Employee: first match on ilike "ahmed", preferring name containing "abdel".
# See inline T01–T14 descriptions in the try block below.

from calendar import monthrange
from datetime import date, datetime

from odoo.exceptions import UserError

TAG = "__UAE_HOLD_SHELL__"
YEAR = 2036

Leave = env["hr.leave"].sudo()
Pay = env["hr.payslip"].sudo()
Alloc = env["hr.leave.allocation"].sudo()


def log(msg):
    print("[UAE-HOLD-SHELL]", msg)


def ok(cond, msg):
    if not cond:
        raise AssertionError(msg)


def month_end(y, m):
    return date(y, m, monthrange(y, m)[1])


def cleanup():
    """Remove test artifacts (TAG in name). Safe to run repeatedly."""
    for p in Pay.search([("name", "ilike", TAG)]):
        if p.state == "done":
            p.action_payslip_draft()
        if p.state in ("verify", "on_hold", "cancel"):
            p.action_payslip_draft()
        p.unlink()
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
    for a in Alloc.search([("name", "ilike", TAG)]):
        if a.state == "validate":
            a.action_refuse()
        if a.state == "refuse":
            a.action_set_to_confirm()
        a.unlink()


def mk_leave(label, leave_type, d0, d1):
    return Leave.create(
        {
            "name": "%s %s" % (TAG, label),
            "employee_id": emp.id,
            "holiday_status_id": leave_type.id,
            "request_date_from": d0,
            "request_date_to": d1,
            "date_from": datetime(d0.year, d0.month, d0.day, 7, 0, 0),
            "date_to": datetime(d1.year, d1.month, d1.day, 19, 0, 0),
        }
    )


def confirm_validate(lv):
    """Default time off state is already ``confirm`` (To Approve)."""
    lv.action_validate()


def mk_slip(month, label):
    df = date(YEAR, month, 1)
    dt = month_end(YEAR, month)
    return Pay.create(
        {
            "name": "%s %s" % (TAG, label),
            "employee_id": emp.id,
            "contract_id": contract.id,
            "struct_id": struct.id,
            "date_from": df,
            "date_to": dt,
        }
    )


log("cleanup previous TAG rows")
cleanup()

candidates = env["hr.employee"].sudo().search([("name", "ilike", "ahmed")], order="id")
ok(candidates, "No employee matching 'ahmed' — create or rename employee for this test.")
emp = candidates.filtered(lambda e: "abdel" in (e.name or "").lower())[:1] or candidates[:1]
log("using employee id=%s name=%r" % (emp.id, emp.name))

contract = emp.sudo().contract_id
if not contract or contract.state != "open":
    contract = emp.sudo().contract_ids.filtered(lambda c: c.state == "open")[:1]
ok(contract, "Employee %s has no open contract — need contract for payslip." % emp.name)

struct = env.ref("hr_uae_payroll.hr_payroll_structure_uae", raise_if_not_found=False)
ok(struct, "Missing hr_uae_payroll.hr_payroll_structure_uae")
if contract.struct_id:
    struct = contract.struct_id

lt_special = env.ref("hr_uae_leaves.leave_type_special")
lt_medical = env.ref("hr_uae_leaves.leave_type_medical")
lt_unpaid = env.ref("hr_uae_leaves.leave_type_unpaid")
lt_annual = env.ref("hr_uae_leaves.leave_type_annual")

results = []

try:
    # ----- T01: payslip month with no leave → no hold -----
    s = mk_slip(1, "T01_jan")
    s.compute_sheet()
    ok(not s.hr_uae_hold_active, "T01 hold flag")
    ok(s.state in ("draft", "verify"), "T01 state %s" % s.state)
    results.append("T01 no-leave no-hold OK")

    # ----- T02: validate overlapping special after slip computed → sync → on_hold -----
    s02 = mk_slip(2, "T02_feb_special")
    s02.compute_sheet()
    lv2 = mk_leave("T02_special", lt_special, date(YEAR, 2, 10), date(YEAR, 2, 20))
    confirm_validate(lv2)
    s02.invalidate_recordset()
    ok(s02.hr_uae_hold_active, "T02 should hold after leave validate")
    ok(s02.state == "on_hold", "T02 state on_hold got %s" % s02.state)
    ok(s02.hr_uae_held_leave_id == lv2, "T02 held leave link")
    results.append("T02 special overlap → on_hold OK")

    # ----- T03: Returned releases hold -----
    lv2.write({"hr_uae_returned": True})
    s02.invalidate_recordset()
    ok(not s02.hr_uae_hold_active, "T03 hold cleared")
    ok(s02.state == "verify", "T03 back to verify got %s" % s02.state)
    results.append("T03 returned → verify OK")

    # ----- T04: medical (sick_leave) does not hold -----
    s04 = mk_slip(3, "T04_mar_medical")
    s04.compute_sheet()
    lv4 = mk_leave("T04_med", lt_medical, date(YEAR, 3, 5), date(YEAR, 3, 25))
    confirm_validate(lv4)
    s04.invalidate_recordset()
    ok(not s04.hr_uae_hold_active, "T04 medical must not hold")
    ok(s04.state != "on_hold", "T04 state not on_hold")
    results.append("T04 medical no-hold OK")

    # ----- T05: done payslip not touched by overlapping special -----
    s05 = mk_slip(4, "T05_apr_done")
    s05.compute_sheet()
    s05.with_context(without_compute_sheet=True).action_payslip_done()
    ok(s05.state == "done", "T05 slip done")
    lv5 = mk_leave("T05_special_after_done", lt_special, date(YEAR, 4, 8), date(YEAR, 4, 22))
    confirm_validate(lv5)
    s05.invalidate_recordset()
    ok(s05.state == "done", "T05 stays done")
    ok(not s05.hr_uae_hold_active, "T05 no hold on done slip")
    results.append("T05 done slip immune OK")

    # ----- T06: unpaid (vacations code) triggers hold -----
    s06 = mk_slip(5, "T06_may_unpaid")
    s06.compute_sheet()
    lv6 = mk_leave("T06_unpaid", lt_unpaid, date(YEAR, 5, 12), date(YEAR, 5, 18))
    confirm_validate(lv6)
    s06.invalidate_recordset()
    ok(s06.hr_uae_hold_active and s06.state == "on_hold", "T06 unpaid hold")
    lv6.write({"hr_uae_returned": True})
    s06.invalidate_recordset()
    ok(not s06.hr_uae_hold_active, "T06 returned clears")
    results.append("T06 unpaid hold + returned OK")

    # ----- T07: annual leave (requires allocation) triggers hold -----
    alloc = Alloc.create(
        {
            "name": "%s T07_alloc" % TAG,
            "holiday_status_id": lt_annual.id,
            "number_of_days": 25,
            "employee_id": emp.id,
            "date_from": date(YEAR, 1, 1),
            "date_to": date(YEAR, 12, 31),
            "state": "confirm",
        }
    )
    alloc.action_validate()
    s07 = mk_slip(6, "T07_jun_annual")
    s07.compute_sheet()
    lv7 = mk_leave("T07_annual", lt_annual, date(YEAR, 6, 3), date(YEAR, 6, 14))
    confirm_validate(lv7)
    s07.invalidate_recordset()
    ok(s07.hr_uae_hold_active and s07.state == "on_hold", "T07 annual hold")
    results.append("T07 annual+allocation hold OK")

    # ----- T08: leave in different month than payslip → no overlap → no hold -----
    s08 = mk_slip(7, "T08_jul_slip")
    s08.compute_sheet()
    lv8 = mk_leave("T08_aug_leave", lt_special, date(YEAR, 8, 5), date(YEAR, 8, 12))
    confirm_validate(lv8)
    s08.invalidate_recordset()
    ok(not s08.hr_uae_hold_active, "T08 no overlap no hold")
    results.append("T08 disjoint periods OK")

    # ----- T09: cannot confirm payslip while on hold -----
    s09 = mk_slip(9, "T09_sep_hold_block")
    s09.compute_sheet()
    lv9 = mk_leave("T09_special", lt_special, date(YEAR, 9, 10), date(YEAR, 9, 20))
    confirm_validate(lv9)
    s09.invalidate_recordset()
    ok(s09.hr_uae_hold_active, "T09 pre assert hold")
    try:
        s09.action_payslip_done()
        raise AssertionError("T09 expected UserError on confirm while held")
    except UserError as e:
        ok("hold" in (e.args[0] or "").lower() or "returned" in (e.args[0] or "").lower(), "T09 msg %s" % e)
    results.append("T09 confirm blocked while hold OK")

    # ----- T10: explicit recompute from leave -----
    s10 = mk_slip(10, "T10_oct_recompute")
    s10.compute_sheet()
    lv10 = mk_leave("T10_special", lt_special, date(YEAR, 10, 7), date(YEAR, 10, 15))
    confirm_validate(lv10)
    s10.invalidate_recordset()
    ok(s10.state == "on_hold", "T10 on hold before recompute")
    act = lv10.action_hr_uae_recompute_overlapping_payslips()
    ok(isinstance(act, dict) and act.get("type") == "ir.actions.client", "T10 notification action")
    s10.invalidate_recordset()
    ok(s10.hr_uae_hold_active, "T10 still hold after recompute (leave not returned)")
    results.append("T10 recompute overlapping OK")

    # ----- T11: unlink validated leave clears hold -----
    s11 = mk_slip(11, "T11_nov_unlink")
    s11.compute_sheet()
    lv11 = mk_leave("T11_special", lt_special, date(YEAR, 11, 4), date(YEAR, 11, 12))
    confirm_validate(lv11)
    s11.invalidate_recordset()
    ok(s11.hr_uae_hold_active, "T11 hold before unlink")
    lv11.action_refuse()
    s11.invalidate_recordset()
    ok(not s11.hr_uae_hold_active, "T11 hold cleared after refuse (state sync)")
    ok(s11.state in ("draft", "verify"), "T11 state after clear %s" % s11.state)
    results.append("T11 refuse clears hold OK")

    # ----- T12: action_hr_uae_release_hold reapplies logic (leave still out) -----
    s12 = mk_slip(12, "T12_dec_release")
    s12.compute_sheet()
    lv12a = mk_leave("T12_special", lt_special, date(YEAR, 12, 2), date(YEAR, 12, 10))
    confirm_validate(lv12a)
    s12.invalidate_recordset()
    ok(s12.hr_uae_hold_active, "T12 hold")
    s12.action_hr_uae_release_hold()
    s12.invalidate_recordset()
    ok(s12.hr_uae_hold_active, "T12 release_hold with active leave must keep hold")
    lv12a.write({"hr_uae_returned": True})
    s12.invalidate_recordset()
    ok(not s12.hr_uae_hold_active, "T12 cleared after returned")
    s12.action_hr_uae_release_hold()
    results.append("T12 release_hold semantics OK")

    # ----- T13: payslip date change moves out of leave window → hold clears -----
    y2 = YEAR + 2
    s13 = Pay.create(
        {
            "name": "%s T13_dates" % TAG,
            "employee_id": emp.id,
            "contract_id": contract.id,
            "struct_id": struct.id,
            "date_from": date(y2, 1, 1),
            "date_to": month_end(y2, 1),
        }
    )
    s13.compute_sheet()
    lv13 = mk_leave("T13_special", lt_special, date(y2, 1, 10), date(y2, 1, 20))
    confirm_validate(lv13)
    s13.invalidate_recordset()
    ok(s13.hr_uae_hold_active, "T13 hold when overlapping")
    s13.write(
        {
            "date_from": date(y2, 2, 1),
            "date_to": month_end(y2, 2),
        }
    )
    s13.invalidate_recordset()
    ok(not s13.hr_uae_hold_active, "T13 hold cleared when slip moved away")
    results.append("T13 slip date write sync OK")

    # ----- T14: two hold-eligible leaves same window — one is linked (limit=1) -----
    s14 = Pay.create(
        {
            "name": "%s T14_two_lv" % TAG,
            "employee_id": emp.id,
            "contract_id": contract.id,
            "struct_id": struct.id,
            "date_from": date(y2, 3, 1),
            "date_to": month_end(y2, 3),
        }
    )
    s14.compute_sheet()
    la = mk_leave("T14_a", lt_special, date(y2, 3, 5), date(y2, 3, 9))
    confirm_validate(la)
    lb = mk_leave("T14_b", lt_unpaid, date(y2, 3, 18), date(y2, 3, 22))
    confirm_validate(lb)
    s14.invalidate_recordset()
    ok(s14.hr_uae_hold_active, "T14 hold with two leaves")
    ok(s14.hr_uae_held_leave_id in (la | lb), "T14 held leave is one of the two")
    results.append("T14 dual leave hold OK")

finally:
    log("cleanup after run")
    cleanup()

log("--- ALL CASES PASSED ---")
for r in results:
    log("PASS: %s" % r)
