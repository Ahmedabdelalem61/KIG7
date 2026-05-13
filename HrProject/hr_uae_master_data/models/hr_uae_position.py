from odoo import fields, models


class HrUaePosition(models.Model):
    _name = "hr.uae.position"
    _description = "Employee Position (HR UAE)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "Position name must be unique.",
        ),
    ]
