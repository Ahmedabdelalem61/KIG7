from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    document_ids = fields.One2many(
        "hr.uae.document",
        "employee_id",
        string="Documents",
    )
    document_count = fields.Integer(
        compute="_compute_document_count",
    )
    document_alert_count = fields.Integer(
        compute="_compute_document_count",
        help="Number of documents that are expired or about to expire (<= 90 days).",
    )

    def _compute_document_count(self):
        Doc = self.env["hr.uae.document"].sudo()
        for emp in self:
            domain = [("employee_id", "=", emp.id), ("active", "=", True)]
            emp.document_count = Doc.search_count(domain)
            emp.document_alert_count = Doc.search_count(
                domain + [("expiry_state", "in", ("expired", "expires_30", "expires_60", "expires_90"))]
            )

    def action_open_documents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Documents - %s" % self.name,
            "res_model": "hr.uae.document",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        }
