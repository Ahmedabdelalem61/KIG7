from odoo import fields, models

# Small company-currency dict shared in shape with the HR dashboard.
# pylint: disable=duplicate-code


class HrUaePayrollLiveDashboard(models.AbstractModel):
    # pylint: disable=too-few-public-methods,protected-access
    """Relabel the live payroll dashboard to the company currency and convert
    the (foreign-currency) salary-adjustment amounts. Net/held figures are
    already company currency (payroll computes there)."""

    _inherit = "hr.uae.payroll.live.dashboard"

    def fetch_data(self, options=None):
        """Relabel currency to company and convert adjustment amounts."""
        data = super().fetch_data(options=options)
        company = self.env.company
        cur = company.currency_id
        data["currency"] = {
            "id": cur.id,
            "name": cur.name,
            "symbol": cur.symbol or cur.name,
            "position": cur.position or "after",
        }
        today = fields.Date.context_today(self)
        adj_model = self.env["hr.uae.salary.adjustment"].sudo()
        converted = {
            a.id: a.currency_id._hr_uae_to_company(
                a.amount, company, today, raise_if_missing=False
            )
            for a in adj_model.search([("state", "=", "to_approve")])
        }
        for row in data.get("adjustments", []):
            if row.get("id") in converted:
                row["amount"] = float(converted[row["id"]])
        return data
