from datetime import timedelta

from odoo import api, fields, models


class HrUaeAuditLog(models.Model):
    _name = "hr.uae.audit.log"
    _description = "HR UAE Audit Log Entry"
    _order = "change_date desc, id desc"
    _rec_name = "field_label"

    model = fields.Char(required=True, index=True, readonly=True)
    res_id = fields.Integer(required=True, index=True, readonly=True)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        index=True,
        ondelete="set null",
        readonly=True,
    )
    field_name = fields.Char(readonly=True)
    field_label = fields.Char(string="Field", readonly=True)
    old_display = fields.Char(string="Old Value", readonly=True)
    new_display = fields.Char(string="New Value", readonly=True)
    change_type = fields.Selection(
        [
            ("create", "Created"),
            ("write", "Updated"),
            ("unlink", "Deleted"),
        ],
        required=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Changed By",
        default=lambda self: self.env.user,
        readonly=True,
        index=True,
    )
    change_date = fields.Datetime(
        string="Changed At",
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        index=True,
    )

    @api.depends("field_label", "model", "old_display", "new_display")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s: %s -> %s" % (
                rec.field_label or rec.model,
                rec.old_display or "",
                rec.new_display or "",
            )

    @api.model
    def _gc_old_logs(self, retention_days=730):
        """Garbage-collect logs older than `retention_days`. Default = 2 years."""
        cutoff = fields.Datetime.now() - timedelta(days=retention_days)
        self.search([("change_date", "<", cutoff)]).unlink()
