from odoo import api, fields, models


class HrLeave(models.Model):
    _name = "hr.leave"
    _inherit = ["hr.leave", "hr.uae.audit.mixin"]

    hr_uae_returned = fields.Boolean(
        string="Returned",
        copy=False,
        tracking=True,
        help="HR sets this when the employee has physically returned "
        "from a vacation / special permit. Releases payroll holds.",
    )
    hr_uae_alert_sent = fields.Boolean(
        string="Alert Sent",
        copy=False,
    )

    @api.model
    def _cron_leave_alerts(self):
        today = fields.Date.context_today(self)
        Leave = self.env["hr.leave"].sudo()
        candidates = Leave.search(
            [
                ("state", "=", "validate"),
                ("hr_uae_alert_sent", "=", False),
                ("holiday_status_id.hr_uae_alert_days", ">", 0),
                ("date_from", "<=", today),
            ]
        )
        template = self.env.ref(
            "hr_uae_leaves.email_template_leave_alert",
            raise_if_not_found=False,
        )
        if not template:
            return
        manager_group = self.env.ref("hr_uae_base.group_hr_uae_manager")
        recipients = manager_group.users.filtered("partner_id").partner_id
        for leave in candidates:
            elapsed = (today - leave.date_from.date()).days if leave.date_from else 0
            threshold = leave.holiday_status_id.hr_uae_alert_days
            if elapsed >= threshold:
                template.with_context(
                    default_partner_ids=recipients.ids
                ).send_mail(leave.id, force_send=False)
                leave.hr_uae_alert_sent = True

    def _hr_uae_audit_employee_id(self):
        return self.employee_id

    def action_set_returned(self):
        for leave in self:
            leave.hr_uae_returned = True
        return True
