from datetime import timedelta

from odoo import api, fields, models


DOCUMENT_TYPES = [
    ("passport", "Passport"),
    ("visa", "Visa"),
    ("medical", "Medical Examination"),
    ("photo", "Photograph"),
    ("contract", "Contract"),
    ("other", "Other"),
]


class HrUaeDocument(models.Model):
    _name = "hr.uae.document"
    _description = "Employee Document"
    _inherit = ["mail.thread", "hr.uae.audit.mixin"]
    _order = "expiry_date asc, id desc"

    name = fields.Char(required=True, tracking=True)
    document_type = fields.Selection(
        DOCUMENT_TYPES,
        required=True,
        default="other",
        tracking=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    issue_date = fields.Date(tracking=True)
    expiry_date = fields.Date(tracking=True)
    days_to_expiry = fields.Integer(
        string="Days to Expiry",
        compute="_compute_days_to_expiry",
        store=True,
    )
    expiry_state = fields.Selection(
        [
            ("none", "No Expiry"),
            ("expired", "Expired"),
            ("expires_30", "Expires < 30 days"),
            ("expires_60", "Expires < 60 days"),
            ("expires_90", "Expires < 90 days"),
            ("ok", "OK"),
        ],
        compute="_compute_days_to_expiry",
        store=True,
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Files",
    )
    note = fields.Text()
    user_id = fields.Many2one(
        related="employee_id.user_id",
        store=True,
        string="Owner User",
    )
    company_id = fields.Many2one(
        related="employee_id.company_id",
        store=True,
    )
    active = fields.Boolean(default=True)

    @api.depends("expiry_date")
    def _compute_days_to_expiry(self):
        today = fields.Date.context_today(self)
        for doc in self:
            if not doc.expiry_date:
                doc.days_to_expiry = 0
                doc.expiry_state = "none"
                continue
            delta = (doc.expiry_date - today).days
            doc.days_to_expiry = delta
            if delta < 0:
                doc.expiry_state = "expired"
            elif delta <= 30:
                doc.expiry_state = "expires_30"
            elif delta <= 60:
                doc.expiry_state = "expires_60"
            elif delta <= 90:
                doc.expiry_state = "expires_90"
            else:
                doc.expiry_state = "ok"

    @api.model
    def _cron_expiry_alert(self):
        """Daily cron: notify HR Manager group for documents expiring within 90 days."""
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=90)
        docs = self.search(
            [
                ("expiry_date", "!=", False),
                ("expiry_date", "<=", horizon),
                ("active", "=", True),
            ]
        )
        if not docs:
            return
        template = self.env.ref(
            "hr_uae_documents.email_template_document_expiry",
            raise_if_not_found=False,
        )
        if not template:
            return
        manager_group = self.env.ref("hr_uae_base.group_hr_uae_manager")
        recipients = manager_group.users.filtered("partner_id")
        for doc in docs:
            ctx = {
                "default_partner_ids": recipients.partner_id.ids,
            }
            template.with_context(**ctx).send_mail(doc.id, force_send=False)

    def _hr_uae_audit_employee_id(self):
        return self.employee_id
