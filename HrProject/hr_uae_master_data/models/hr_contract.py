from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    housing_allowance = fields.Monetary(
        string="Housing Allowance",
        currency_field="currency_id",
        tracking=True,
        help="Monthly housing allowance defined on the contract.",
    )
    transportation_allowance = fields.Monetary(
        string="Transportation Allowance",
        currency_field="currency_id",
        tracking=True,
        help="Monthly transportation allowance defined on the contract.",
    )
    other_allowances = fields.Monetary(
        string="Other Allowances",
        currency_field="currency_id",
        tracking=True,
        help="Other monthly allowances defined on the contract.",
    )
    annual_ticket_amount = fields.Monetary(
        string="Annual Ticket Amount",
        currency_field="currency_id",
        tracking=True,
        help="Annual flight-ticket benefit amount defined on the contract.",
    )
