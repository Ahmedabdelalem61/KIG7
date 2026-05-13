from odoo import api, fields, models


class HrUaeAuditReportWizard(models.TransientModel):
    _name = "hr.uae.audit.report.wizard"
    _description = "Audit Report Wizard"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
    )
    date_from = fields.Date()
    date_to = fields.Date()

    def action_print(self):
        self.ensure_one()
        return self.env.ref(
            "hr_uae_audit_trail.action_report_employee_audit_trail"
        ).report_action(self)

    def _get_logs(self):
        self.ensure_one()
        domain = [("employee_id", "=", self.employee_id.id)]
        if self.date_from:
            domain.append(("change_date", ">=", self.date_from))
        if self.date_to:
            domain.append(("change_date", "<=", self.date_to))
        return self.env["hr.uae.audit.log"].sudo().search(domain, order="change_date asc, id asc")
