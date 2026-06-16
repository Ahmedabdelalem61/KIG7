from odoo import fields, models


class HrUaePayrollDashboard(models.Model):
    # pylint: disable=too-few-public-methods
    """Expose the company currency on the payroll dashboard so its (already
    company-currency) amounts can be labelled with the monetary widget."""

    _inherit = "hr.uae.payroll.dashboard"

    company_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_company_currency",
    )

    def _compute_company_currency(self):
        cur = self.env.company.currency_id
        for rec in self:
            rec.company_currency_id = cur
