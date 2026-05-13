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

    # ---------- Hold detection ----------

    def _hr_uae_overlapping_hold_leave(self):
        """Return the leave triggering a hold for this payslip, or empty.

        Hold-eligible leaves: types whose ``hr_uae_status_code`` is
        ``vacations`` or ``special_permit`` (Annual & Special Leave by default).
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
                (
                    "holiday_status_id.hr_uae_status_code",
                    "in",
                    ("vacations", "special_permit"),
                ),
            ],
            limit=1,
        )

    def _hr_uae_compute_hold_amounts(self, leave):
        """Compute payable-now / held amount based on a leave overlap.

        Pro-rates the contract wage by the days worked before the leave's
        start within the payslip period.
        """
        self.ensure_one()
        wage = self.contract_id.wage if self.contract_id else 0.0
        if not wage:
            return 0.0, 0.0
        period_days = (self.date_to - self.date_from).days + 1
        if period_days <= 0:
            return 0.0, 0.0
        leave_start = max(self.date_from, leave.date_from.date() if leave.date_from else self.date_from)
        worked_days = max(0, (leave_start - self.date_from).days)
        payable_now = wage * worked_days / period_days
        held = wage - payable_now
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
