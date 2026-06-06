from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_LEAVE_HOLD_TRACK = frozenset(
    {
        "employee_id",
        "date_from",
        "date_to",
        "request_date_from",
        "request_date_to",
        "holiday_status_id",
        "state",
        "hr_uae_returned",
    }
)

_AUTO_FLIGHT_INPUT_NAME = "Flight Ticket Deduction (UAE Auto)"


def _hr_uae_recompute_notify(env, count):
    """Browser toast after batch payslip recompute."""
    if not count:
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": env._("No payslips"),
                "message": env._(
                    "There are no payslips in Draft, Waiting, or On Hold that "
                    "overlap the selected period for the same employee."
                ),
                "type": "warning",
                "sticky": False,
            },
        }
    return {
        "type": "ir.actions.client",
        "tag": "display_notification",
        "params": {
            "title": env._("Payslips recomputed"),
            "message": env._("%s payslip(s) updated.", count),
            "type": "success",
            "sticky": False,
        },
    }


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ["hr.payslip", "hr.uae.audit.mixin"]

    state = fields.Selection(
        selection_add=[
            ("on_hold", "On Hold (Vacation)"),
        ],
        ondelete={"on_hold": "set default"},
    )

    hr_uae_hold_active = fields.Boolean(
        string="On Hold",
        copy=False,
        tracking=True,
    )
    hr_uae_held_leave_id = fields.Many2one(
        "hr.leave",
        string="Held Leave",
        copy=False,
        readonly=True,
        help="Leave that triggered this payslip's hold.",
    )
    hr_uae_held_amount = fields.Monetary(
        string="Total Held",
        currency_field="currency_id",
        copy=False,
        help="Portion of the salary held until the employee returns.",
    )
    hr_uae_payable_now = fields.Monetary(
        string="Total to Pay (Now)",
        currency_field="currency_id",
        copy=False,
        help="Pro-rated amount payable for worked days before vacation.",
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
        readonly=True,
    )
    hr_uae_basic = fields.Monetary(
        string="Basic",
        compute="_compute_hr_uae_basic_net",
        currency_field="currency_id",
    )
    hr_uae_net = fields.Monetary(
        string="Net",
        compute="_compute_hr_uae_basic_net",
        currency_field="currency_id",
    )

    @api.depends(
        "line_ids.total",
        "line_ids.code",
        "hr_uae_hold_active",
        "hr_uae_payable_now",
    )
    def _compute_hr_uae_basic_net(self):
        for slip in self:
            basic_line = slip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
            slip.hr_uae_basic = basic_line.total if basic_line else 0.0
            if slip.hr_uae_hold_active:
                slip.hr_uae_net = slip.hr_uae_payable_now or 0.0
            else:
                net_line = slip.line_ids.filtered(lambda line: line.code == "NET")[:1]
                slip.hr_uae_net = net_line.total if net_line else 0.0

    # ---------- Payroll inputs / worked days ----------

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """Keep standard worked days, then add UAE unpaid leave lines.

        The upstream payroll module only deducts leave if the leave type has a
        work entry type with a matching code. UAE setup keeps an explicit
        checkbox on the leave type so standard unpaid leave configuration keeps
        working, and missing work-entry mapping still generates ``UNPAID``.
        """
        lines = list(super().get_worked_day_lines(contracts, date_from, date_to))
        contracts_with_unpaid = {
            line.get("contract_id")
            for line in lines
            if line.get("code") == "UNPAID"
            and abs(line.get("number_of_days") or 0.0) > 0.0
        }
        for line in lines:
            if line.get("code") == "UNPAID":
                line["number_of_days"] = abs(line.get("number_of_days") or 0.0)
                line["number_of_hours"] = abs(line.get("number_of_hours") or 0.0)
                line["name"] = line.get("name") or _("Unpaid Leave")
        for contract in contracts:
            if contract.id in contracts_with_unpaid:
                continue
            days = self._hr_uae_unpaid_leave_days(contract, date_from, date_to)
            if not days:
                continue
            hours_per_day = getattr(contract.resource_calendar_id, "hours_per_day", 0.0) or 8.0
            lines.append(
                {
                    "name": _("Unpaid Leave"),
                    "sequence": 50,
                    "code": "UNPAID",
                    "number_of_days": days,
                    "number_of_hours": days * hours_per_day,
                    "contract_id": contract.id,
                }
            )
        return lines

    def _hr_uae_unpaid_leave_days(self, contract, date_from, date_to):
        """Return positive calendar days for validated unpaid leave overlaps."""
        if not contract.employee_id or not date_from or not date_to:
            return 0.0
        Leave = self.env["hr.leave"].sudo()
        leaves = Leave.search(
            [
                ("employee_id", "=", contract.employee_id.id),
                ("state", "=", "validate"),
                ("holiday_status_id.hr_uae_unpaid", "=", True),
                ("date_from", "<=", date_to),
                ("date_to", ">=", date_from),
            ]
        )
        days = set()
        for leave in leaves:
            leave_start = leave.request_date_from or fields.Date.to_date(leave.date_from)
            leave_end = leave.request_date_to or fields.Date.to_date(leave.date_to)
            if not leave_start or not leave_end:
                continue
            current = max(date_from, leave_start)
            last = min(date_to, leave_end)
            while current <= last:
                days.add(current)
                current += timedelta(days=1)
        return float(len(days))

    def _hr_uae_refresh_worked_days(self):
        for slip in self.filtered(lambda s: s.state in ("draft", "verify", "on_hold")):
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue
            contracts = slip._get_employee_contracts()
            if not contracts:
                continue
            worked_days = slip.get_worked_day_lines(contracts, slip.date_from, slip.date_to)
            slip.with_context(hr_uae_skip_audit=True).write(
                {
                    "worked_days_line_ids": [(5, 0, 0)]
                    + [(0, 0, line) for line in worked_days],
                }
            )

    def _hr_uae_flight_deduction_date(self, flight):
        self.ensure_one()
        return (
            flight.departure_date
            or flight.requested_date
            or fields.Date.to_date(flight.create_date)
        )

    def _hr_uae_flight_deduction_amount(self):
        self.ensure_one()
        if (
            not self.employee_id
            or not self.employee_id.hr_uae_deduct_employee_paid_tickets
            or not self.date_from
            or not self.date_to
        ):
            return 0.0
        flights = self.env["hr.uae.flight"].sudo().search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("payment_mode", "=", "own_account"),
                ("booking_state", "in", ("booked", "completed")),
                ("total", ">", 0.0),
            ]
        )
        amount = 0.0
        for flight in flights:
            deduction_date = self._hr_uae_flight_deduction_date(flight)
            if deduction_date and self.date_from <= deduction_date <= self.date_to:
                amount += flight.total
        return amount

    def _hr_uae_sync_flight_deduction_inputs(self):
        Input = self.env["hr.payslip.input"].sudo()
        for slip in self.filtered(lambda s: s.state in ("draft", "verify", "on_hold")):
            if not slip.contract_id:
                continue
            existing = Input.search(
                [("payslip_id", "=", slip.id), ("code", "=", "FLIGHT_DED")],
                order="id",
            )
            auto_inputs = existing.filtered(lambda line: line.name == _AUTO_FLIGHT_INPUT_NAME)
            amount = slip._hr_uae_flight_deduction_amount()
            if not amount:
                auto_inputs.unlink()
                continue
            target = existing[:1] or Input.create(
                {
                    "payslip_id": slip.id,
                    "contract_id": slip.contract_id.id,
                    "code": "FLIGHT_DED",
                    "name": _AUTO_FLIGHT_INPUT_NAME,
                }
            )
            target.write(
                {
                    "payslip_id": slip.id,
                    "contract_id": slip.contract_id.id,
                    "code": "FLIGHT_DED",
                    "name": _AUTO_FLIGHT_INPUT_NAME,
                    "amount": amount,
                }
            )
            (existing - target).unlink()

    def _hr_uae_refresh_payroll_inputs(self):
        self._hr_uae_sync_flight_deduction_inputs()

    @api.model
    def _hr_uae_sync_flight_inputs_for_employees(self, employees):
        if not employees:
            return
        slips = self.sudo().search(
            [
                ("employee_id", "in", employees.ids),
                ("state", "in", ("draft", "verify", "on_hold")),
            ]
        )
        slips._hr_uae_sync_flight_deduction_inputs()

    def _hr_uae_refresh_payroll_sources(self):
        self._hr_uae_refresh_worked_days()
        self._hr_uae_refresh_payroll_inputs()

    # ---------- Hold detection ----------

    def _hr_uae_overlapping_hold_leave(self):
        """Return the leave triggering a hold for this payslip, or empty.

        Hold-eligible leaves: types explicitly flagged to hold payroll. In the
        UAE defaults, only Annual Leave has that flag.
        """
        self.ensure_one()
        if not self.employee_id or not self.date_from or not self.date_to:
            return self.env["hr.leave"].browse()
        return self.env["hr.leave"].sudo().search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "=", "validate"),
                ("hr_uae_returned", "=", False),
                ("date_from", "<=", self.date_to),
                ("date_to", ">=", self.date_from),
                ("holiday_status_id.hr_uae_hold_payroll", "=", True),
            ],
            limit=1,
        )

    def _hr_uae_hold_base_amount(self):
        self.ensure_one()
        net = self.line_ids.filtered(lambda line: line.code == "NET")[:1]
        if net:
            return net.total
        contract = self.contract_id
        if not contract:
            return 0.0
        return (
            (contract.wage or 0.0)
            + (contract.housing_allowance or 0.0)
            + (contract.transportation_allowance or 0.0)
            + (contract.other_allowances or 0.0)
        )

    def _hr_uae_compute_hold_amounts(self, leave):
        """Compute payable-now / held amount based on a leave overlap.

        Pro-rates the computed NET by the days worked before the leave starts.
        If the slip is not computed yet, it falls back to contract wage plus
        regular allowances.
        """
        self.ensure_one()
        base_amount = self._hr_uae_hold_base_amount()
        if not base_amount:
            return 0.0, 0.0
        period_days = (self.date_to - self.date_from).days + 1
        if period_days <= 0:
            return 0.0, 0.0
        leave_start = max(
            self.date_from,
            fields.Date.to_date(leave.date_from) if leave.date_from else self.date_from,
        )
        worked_days = max(0, (leave_start - self.date_from).days)
        payable_now = base_amount * worked_days / period_days
        held = base_amount - payable_now
        return round(payable_now, 2), round(held, 2)

    def _hr_uae_apply_or_clear_hold(self):
        """Set or clear vacation/permit hold without running a full sheet compute.

        Called after ``compute_sheet`` and whenever overlapping approved leaves
        change, so HR does not have to manually re-click **Compute Sheet** only
        to refresh hold flags.
        """
        slips = self.filtered(lambda s: s.state in ("draft", "verify", "on_hold"))
        for slip in slips:
            leave = slip._hr_uae_overlapping_hold_leave()
            if leave:
                payable, held = slip._hr_uae_compute_hold_amounts(leave)
                slip.write(
                    {
                        "hr_uae_hold_active": True,
                        "hr_uae_held_leave_id": leave.id,
                        "hr_uae_payable_now": payable,
                        "hr_uae_held_amount": held,
                        "state": "on_hold",
                    }
                )
            else:
                was_hold = slip.hr_uae_hold_active or slip.state == "on_hold"
                clear_vals = {
                    "hr_uae_hold_active": False,
                    "hr_uae_held_leave_id": False,
                    "hr_uae_payable_now": 0.0,
                    "hr_uae_held_amount": 0.0,
                }
                if was_hold:
                    clear_vals["state"] = "verify" if slip.line_ids else "draft"
                slip.write(clear_vals)

    @api.model
    def _hr_uae_sync_hold_for_employees(self, employees):
        """Refresh hold on all editable payslips for the given employees."""
        if not employees:
            return
        slips = self.sudo().search(
            [
                ("employee_id", "in", employees.ids),
                ("state", "in", ("draft", "verify", "on_hold")),
            ]
        )
        slips._hr_uae_apply_or_clear_hold()

    # ---------- Workflow hooks ----------

    def compute_sheet(self):
        self._hr_uae_refresh_payroll_sources()
        result = super().compute_sheet()
        self._hr_uae_apply_or_clear_hold()
        return result

    def write(self, vals):
        emps_before = self.mapped("employee_id")
        res = super().write(vals)
        if {"employee_id", "date_from", "date_to"} & vals.keys():
            self._hr_uae_sync_hold_for_employees(emps_before | self.mapped("employee_id"))
        return res

    def action_hr_uae_release_hold(self):
        """Re-evaluate hold (e.g. after **Returned**) without a full recomputation."""
        self._hr_uae_apply_or_clear_hold()
        return True

    def action_hr_uae_recompute_slips_same_period(self):
        """Run **Compute Sheet** on this slip and other editable slips that share the same overlap window.

        Use after leave changes or **Returned**, when HR wants salary lines refreshed without hunting each slip.
        """
        Payslip = self.env["hr.payslip"].sudo()
        to_compute = Payslip.browse()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue
            found = Payslip.search(
                [
                    ("employee_id", "=", slip.employee_id.id),
                    ("state", "in", ("draft", "verify", "on_hold")),
                    ("date_from", "<=", slip.date_to),
                    ("date_to", ">=", slip.date_from),
                ]
            )
            to_compute |= found
        if not to_compute:
            return _hr_uae_recompute_notify(self.env, 0)
        to_compute.compute_sheet()
        return _hr_uae_recompute_notify(self.env, len(to_compute))

    def action_payslip_done(self):
        held = self.filtered("hr_uae_hold_active")
        if held:
            raise UserError(
                _("Cannot confirm a payslip on hold. Mark the leave as Returned first.")
            )
        return super().action_payslip_done()

    def _hr_uae_audit_employee_id(self):
        return self.employee_id


class HrLeave(models.Model):
    """Auto sync payslip vacation hold when leave data or approval changes."""

    _inherit = "hr.leave"

    def action_hr_uae_recompute_overlapping_payslips(self):
        """Full **Compute Sheet** on payslips that overlap this leave (explicit HR action)."""
        Payslip = self.env["hr.payslip"].sudo()
        to_compute = Payslip.browse()
        for leave in self:
            if not leave.employee_id or not leave.date_from or not leave.date_to:
                continue
            d_from = leave.date_from.date()
            d_to = leave.date_to.date()
            found = Payslip.search(
                [
                    ("employee_id", "=", leave.employee_id.id),
                    ("state", "in", ("draft", "verify", "on_hold")),
                    ("date_from", "<=", d_to),
                    ("date_to", ">=", d_from),
                ]
            )
            to_compute |= found
        if not to_compute:
            return _hr_uae_recompute_notify(self.env, 0)
        to_compute.compute_sheet()
        return _hr_uae_recompute_notify(self.env, len(to_compute))

    def write(self, vals):
        employees_before = self.mapped("employee_id")
        result = super().write(vals)
        if _LEAVE_HOLD_TRACK & vals.keys():
            employees = employees_before | self.mapped("employee_id")
            self.env["hr.payslip"]._hr_uae_sync_hold_for_employees(employees)
        return result

    def unlink(self):
        employees = self.mapped("employee_id")
        res = super().unlink()
        self.env["hr.payslip"]._hr_uae_sync_hold_for_employees(employees)
        return res
