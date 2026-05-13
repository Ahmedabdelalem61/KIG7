from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    hr_uae_status_code = fields.Selection(
        selection=[
            ("vacations", "Vacations"),
            ("special_permit", "Special Permit"),
            ("sick_leave", "Sick Leave"),
        ],
        string="UAE Status Mapping",
        help="Used by hr.employee.hr_uae_status to map a current leave to "
        "the employee's UAE status.",
    )
    hr_uae_alert_days = fields.Integer(
        string="Alert After N Days",
        default=0,
        help="If > 0, an alert is raised once a validated leave of this "
        "type reaches the configured number of days. 0 disables alerts.",
    )
    hr_uae_unpaid = fields.Boolean(
        string="Unpaid (Deduct from Payroll)",
        help="Leaves of this type subtract from worked days in payroll.",
    )
