from odoo import fields, models


class HrUaeRank(models.Model):
    _name = "hr.uae.rank"
    _description = "Employee Rank (HR UAE)"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(help="Short code used in reports.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "Rank name must be unique.",
        ),
    ]
