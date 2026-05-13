from odoo import _, api, fields, models
from odoo.exceptions import UserError


REASON_SELECTION = [
    ("resignation", "Resignation"),
    ("vacation_no_return", "Vacation - Did Not Return"),
    ("special_permit_no_return", "Special Permit - Did Not Return"),
    ("medical", "Medical"),
    ("end_of_contract", "End of Contract"),
    ("dismissal", "Dismissal"),
    ("other", "Other"),
]


class HrUaeTermination(models.Model):
    _name = "hr.uae.termination"
    _description = "Contract Termination"
    _inherit = ["mail.thread", "mail.activity.mixin", "hr.uae.audit.mixin"]
    _order = "departure_date desc, id desc"

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
        ondelete="restrict",
    )
    contract_id = fields.Many2one(
        "hr.contract",
        string="Contract",
        domain="[('employee_id','=',employee_id)]",
        tracking=True,
    )

    roster = fields.Char(related="employee_id.roster", store=True, readonly=True)
    project_allocation_id = fields.Many2one(
        related="employee_id.project_allocation_id",
        store=True,
        readonly=True,
    )
    passport_no = fields.Char(related="employee_id.passport_id", store=True, readonly=True)
    date_of_birth = fields.Date(related="employee_id.birthday", store=True, readonly=True)
    date_of_joining = fields.Date(
        related="employee_id.first_contract_date",
        store=True,
        readonly=True,
    )

    departure_date = fields.Date(tracking=True)
    arrival_date = fields.Date(tracking=True)
    time_of_service = fields.Char(related="employee_id.time_of_service")

    reason = fields.Selection(REASON_SELECTION, default="resignation", tracking=True)
    note = fields.Char(tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
        ],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        Sequence = self.env["ir.sequence"].sudo()
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("New"):
                vals["name"] = Sequence.next_by_code("hr.uae.termination") or _("New")
        return super().create(vals_list)

    def _hr_uae_audit_employee_id(self):
        return self.employee_id

    # ---------- Workflow ----------

    def action_activate(self):
        for rec in self:
            if not rec.employee_id:
                raise UserError(_("Pick an employee before activating the termination."))
            rec.state = "active"
            rec._apply_termination_effects()

    def action_close(self):
        for rec in self:
            rec.state = "closed"

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state == "active":
                raise UserError(
                    _("Cannot reset to draft once active. Use 'Close' instead.")
                )
            rec.state = "draft"

    def _apply_termination_effects(self):
        Payslip = self.env["hr.payslip"].sudo()
        for rec in self:
            emp = rec.employee_id.sudo()
            if rec.contract_id:
                rec.contract_id.with_context(hr_uae_skip_audit=False).write(
                    {
                        "state": "close",
                        "date_end": rec.departure_date or fields.Date.context_today(rec),
                    }
                )
            for contract in emp.contract_ids.filtered(lambda c: c.state in ("draft", "open")):
                contract.write(
                    {
                        "state": "close",
                        "date_end": rec.departure_date or fields.Date.context_today(rec),
                    }
                )
            future_slips = Payslip.search(
                [
                    ("employee_id", "=", emp.id),
                    ("state", "in", ("draft", "verify", "on_hold")),
                ]
            )
            for slip in future_slips:
                if slip.state in ("draft", "verify", "on_hold"):
                    slip.write({"state": "cancel"})
            emp.write(
                {
                    "active": False,
                    "hr_uae_status": "terminated",
                    "hr_uae_status_manual": True,
                }
            )
