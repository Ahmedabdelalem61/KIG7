from odoo import fields, models


class HrUaeEmployeeState(models.Model):
    _name = "hr.uae.employee.state"
    _description = "Employee Lifecycle State (HR UAE)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    color = fields.Integer(string="Color Index", default=0)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "code_unique",
            "unique(code)",
            "Employee state code must be unique.",
        ),
    ]
