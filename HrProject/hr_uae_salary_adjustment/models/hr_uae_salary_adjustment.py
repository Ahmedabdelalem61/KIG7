from odoo import _, api, fields, models
from odoo.exceptions import UserError


KIND_TO_INPUT_CODE = {
    "adjustment": "ADJ_ADJ",
    "allowance": "ADJ_ALW",
    "deduction": "ADJ_DED",
}


class HrUaeSalaryAdjustment(models.Model):
    _name = "hr.uae.salary.adjustment"
    _description = "Salary Adjustment / Allowance / Deduction"
    _inherit = ["mail.thread", "mail.activity.mixin", "hr.uae.audit.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        tracking=True,
    )
    kind = fields.Selection(
        [
            ("adjustment", "Adjustment"),
            ("allowance", "Allowance"),
            ("deduction", "Deduction"),
        ],
        required=True,
        default="adjustment",
        tracking=True,
    )
    amount = fields.Monetary(
        currency_field="currency_id",
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.AED"),
        required=True,
    )

    mode = fields.Selection(
        [
            ("one_shot", "One-shot (specific period)"),
            ("range", "From / To range"),
            ("recurring", "Recurring"),
        ],
        required=True,
        default="one_shot",
        tracking=True,
    )
    target_payslip_id = fields.Many2one(
        "hr.payslip",
        string="Target Payslip",
        domain="[('employee_id','=',employee_id),('state','in',('draft','verify','on_hold'))]",
    )
    date_from = fields.Date(tracking=True)
    date_to = fields.Date(tracking=True)
    recurring_interval = fields.Selection(
        [("month", "Every Month"), ("year", "Every Year")],
        default="month",
    )
    recurring_until = fields.Date()
    last_applied_period = fields.Date(
        readonly=True,
        copy=False,
        help="Last payslip period this adjustment was applied to.",
    )

    notes = fields.Text(tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("refused", "Refused"),
        ],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )

    approver_id = fields.Many2one(
        "res.users",
        string="Approved By",
        readonly=True,
        copy=False,
    )
    approved_on = fields.Datetime(readonly=True, copy=False)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    # ---------- Defaults ----------

    @api.model_create_multi
    def create(self, vals_list):
        Sequence = self.env["ir.sequence"].sudo()
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("New"):
                vals["name"] = (
                    Sequence.next_by_code("hr.uae.salary.adjustment") or _("New")
                )
        return super().create(vals_list)

    def _hr_uae_audit_employee_id(self):
        return self.employee_id

    # ---------- Workflow ----------

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                continue
            if rec.mode == "one_shot" and not rec.target_payslip_id:
                raise UserError(
                    _("Pick a target payslip before submitting a one-shot adjustment.")
                )
            if rec.mode == "range" and not (rec.date_from and rec.date_to):
                raise UserError(_("Set both 'From' and 'To' dates for a range adjustment."))
            if rec.mode == "recurring" and not rec.date_from:
                raise UserError(_("Set 'From' date to start the recurring adjustment."))
            rec.state = "to_approve"

    def action_approve(self):
        manager_group = self.env.ref("hr_uae_base.group_hr_uae_manager")
        if self.env.user not in manager_group.users and not self.env.user.has_group(
            "hr_uae_base.group_hr_uae_manager"
        ):
            raise UserError(_("Only HR Managers (UAE) can approve salary adjustments."))
        for rec in self:
            if rec.state != "to_approve":
                raise UserError(_("Only 'To Approve' records can be approved."))
            rec.write(
                {
                    "state": "approved",
                    "approver_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )
            rec._apply_to_payslips()

    def action_refuse(self):
        for rec in self:
            rec.state = "refused"

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = "draft"

    # ---------- Application ----------

    def _input_code(self):
        return KIND_TO_INPUT_CODE[self.kind]

    def _matching_payslips(self):
        """Find payslips this adjustment should be pushed to."""
        self.ensure_one()
        Payslip = self.env["hr.payslip"].sudo()
        if self.mode == "one_shot":
            return self.target_payslip_id
        domain = [
            ("employee_id", "=", self.employee_id.id),
            ("state", "in", ("draft", "verify", "on_hold")),
        ]
        if self.mode == "range":
            domain += [
                ("date_from", ">=", self.date_from),
                ("date_to", "<=", self.date_to),
            ]
        else:
            domain += [("date_from", ">=", self.date_from)]
            if self.recurring_until:
                domain += [("date_to", "<=", self.recurring_until)]
        return Payslip.search(domain)

    def _apply_to_payslips(self):
        Input = self.env["hr.payslip.input"].sudo()
        for rec in self:
            payslips = rec._matching_payslips()
            if not payslips:
                continue
            for slip in payslips:
                existing = Input.search(
                    [
                        ("payslip_id", "=", slip.id),
                        ("code", "=", rec._input_code()),
                        ("name", "=", rec.name),
                    ],
                    limit=1,
                )
                vals = {
                    "name": rec.name,
                    "code": rec._input_code(),
                    "amount": rec.amount,
                    "payslip_id": slip.id,
                    "contract_id": slip.contract_id.id,
                }
                if existing:
                    existing.write(vals)
                else:
                    Input.create(vals)
            rec.last_applied_period = fields.Date.context_today(rec)
            # Range / recurring stay at 'approved' so the cron re-applies them
            # in future periods. One-shot adjustments are completed.
            if rec.mode == "one_shot":
                rec.state = "done"

    @api.model
    def _cron_apply_recurring(self):
        recs = self.search(
            [
                ("state", "=", "approved"),
                ("mode", "in", ("range", "recurring")),
            ]
        )
        recs._apply_to_payslips()
