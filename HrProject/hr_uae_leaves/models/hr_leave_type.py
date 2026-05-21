from odoo import api, fields, models


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
    hr_uae_hold_payroll = fields.Boolean(
        string="Hold Payroll Until Return",
        help="Validated leaves of this type put editable payslips on hold "
        "until the employee is marked as returned.",
    )

    @staticmethod
    def _hr_uae_default_leave_types():
        return {
            "leave_type_annual": {
                "names": ["Annual Leave"],
                "vals": {
                    "name": "Annual Leave",
                    "time_type": "leave",
                    "leave_validation_type": "hr",
                    "requires_allocation": "yes",
                    "allocation_validation_type": "hr",
                    "hr_uae_status_code": "vacations",
                    "hr_uae_alert_days": 20,
                    "hr_uae_unpaid": False,
                    "hr_uae_hold_payroll": True,
                    "color": 1,
                },
            },
            "leave_type_special": {
                "names": ["Special Leave"],
                "vals": {
                    "name": "Special Leave",
                    "time_type": "leave",
                    "leave_validation_type": "hr",
                    "requires_allocation": "no",
                    "hr_uae_status_code": "special_permit",
                    "hr_uae_alert_days": 7,
                    "hr_uae_unpaid": False,
                    "hr_uae_hold_payroll": False,
                    "color": 2,
                },
            },
            "leave_type_medical": {
                "names": ["Medical Leave", "Sick Leave"],
                "vals": {
                    "name": "Medical Leave",
                    "time_type": "leave",
                    "leave_validation_type": "hr",
                    "requires_allocation": "no",
                    "hr_uae_status_code": "sick_leave",
                    "hr_uae_alert_days": 0,
                    "hr_uae_unpaid": False,
                    "hr_uae_hold_payroll": False,
                    "color": 3,
                },
            },
            "leave_type_unpaid": {
                "names": ["Unpaid Leave"],
                "vals": {
                    "name": "Unpaid Leave",
                    "time_type": "leave",
                    "leave_validation_type": "hr",
                    "requires_allocation": "no",
                    "hr_uae_status_code": "vacations",
                    "hr_uae_alert_days": 0,
                    "hr_uae_unpaid": True,
                    "hr_uae_hold_payroll": False,
                    "color": 4,
                },
            },
        }

    @api.model
    def _hr_uae_find_or_create_leave_type(self, xml_name, config):
        xmlid = "hr_uae_leaves.%s" % xml_name
        leave_type = self.env.ref(xmlid, raise_if_not_found=False)
        if not leave_type:
            leave_type = self.search([("name", "in", config["names"])], limit=1)
        if not leave_type:
            leave_type = self.create(config["vals"])
        else:
            leave_type.write(
                {
                    "hr_uae_status_code": config["vals"]["hr_uae_status_code"],
                    "hr_uae_alert_days": config["vals"]["hr_uae_alert_days"],
                    "hr_uae_unpaid": config["vals"]["hr_uae_unpaid"],
                    "hr_uae_hold_payroll": config["vals"]["hr_uae_hold_payroll"],
                }
            )
        module, name = xmlid.split(".")
        data = self.env["ir.model.data"].sudo()
        existing = data.search([("module", "=", module), ("name", "=", name)], limit=1)
        if not existing:
            data.create(
                {
                    "module": module,
                    "name": name,
                    "model": self._name,
                    "res_id": leave_type.id,
                    "noupdate": True,
                }
            )
        return leave_type

    @api.model
    def _hr_uae_ensure_default_leave_flags(self):
        for xml_name, config in self._hr_uae_default_leave_types().items():
            self._hr_uae_find_or_create_leave_type(xml_name, config)
        return True
