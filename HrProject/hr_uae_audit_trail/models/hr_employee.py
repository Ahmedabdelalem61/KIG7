from odoo import fields, models


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee", "hr.uae.audit.mixin"]

    audit_log_ids = fields.One2many(
        "hr.uae.audit.log",
        "employee_id",
        string="Audit Trail",
        readonly=True,
    )
    audit_log_count = fields.Integer(
        string="Audit Entries",
        compute="_compute_audit_log_count",
    )

    def _compute_audit_log_count(self):
        Log = self.env["hr.uae.audit.log"].sudo()
        for emp in self:
            emp.audit_log_count = Log.search_count(
                [("employee_id", "=", emp.id)]
            )

    def action_open_audit_log(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Audit Trail - %s" % self.name,
            "res_model": "hr.uae.audit.log",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
