from odoo import api, fields, models


class HrUaePayrollDashboard(models.Model):
    """Add Basic / Net columns to the payroll dashboard for display and export.

    These are non-stored computed fields so the underlying SQL view (defined in
    hr_uae_payroll and extended in hr_uae_project_department) is left untouched.
    The payslip-line read is sudo'd: it is a read-only derived figure for a row
    the user can already see, and avoids regressing access for plain HR users.
    """

    _inherit = "hr.uae.payroll.dashboard"

    basic_amount = fields.Float(
        string="Basic",
        compute="_compute_basic_amount",
        help="Basic salary from the payslip line with salary rule code 'BASIC'.",
    )
    net_amount = fields.Float(
        string="Net",
        compute="_compute_net_amount",
        help="Net payable for the period (mirrors Total to Pay).",
    )

    @api.depends("total_to_pay")
    def _compute_net_amount(self):
        for row in self:
            row.net_amount = row.total_to_pay

    @api.depends("payslip_id")
    def _compute_basic_amount(self):
        slips = self.mapped("payslip_id")
        totals = {}
        if slips:
            groups = self.env["hr.payslip.line"].sudo().read_group(
                [("slip_id", "in", slips.ids), ("code", "=", "BASIC")],
                ["total:sum"],
                ["slip_id"],
            )
            totals = {g["slip_id"][0]: g["total"] for g in groups if g["slip_id"]}
        for row in self:
            row.basic_amount = totals.get(row.payslip_id.id, 0.0)
