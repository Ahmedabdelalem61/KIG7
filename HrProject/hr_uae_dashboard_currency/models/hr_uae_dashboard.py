from datetime import timedelta

from odoo import api, fields, models

# Small company-currency dict shared in shape with the live dashboard.
# pylint: disable=duplicate-code


class HrUaeDashboard(models.TransientModel):
    # pylint: disable=too-few-public-methods,no-wizard-in-models
    """Show the HR dashboard in the company currency: relabel money and value
    flight cost via the per-ticket company-currency total."""

    _inherit = "hr.uae.dashboard"

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    def _compute_metrics(self):  # pylint: disable=missing-return
        super()._compute_metrics()
        company = self.env.company
        flights = self.env["hr.uae.flight"].sudo().search(
            [("booking_state", "in", ("booked", "completed"))]
        )
        total = sum(flights.mapped("total_company"))
        for rec in self:
            rec.currency_id = company.currency_id
            rec.flight_cost_total = total

    @api.model
    def fetch_dashboard_data(self):
        """Relabel the live data to the company currency and convert the
        flight-per-project totals to company currency."""
        data = super().fetch_dashboard_data()
        data["currency"] = self._hr_uae_company_currency_dict()
        data["flight_per_project"] = self._hr_uae_flight_per_project_company()
        return data

    @api.model
    def _hr_uae_company_currency_dict(self):
        cur = self.env.company.currency_id
        return {
            "id": cur.id,
            "name": cur.name,
            "symbol": cur.symbol or cur.name,
            "position": cur.position or "after",
        }

    @api.model
    def _hr_uae_flight_per_project_company(self):
        """Flight cost per project/department (top 8, last 12 months) summed in
        company currency (total_company) instead of raw ticket currency."""
        today = fields.Date.context_today(self)
        flight = self.env["hr.uae.flight"].sudo()
        group_field = (
            "department_id"
            if "department_id" in flight._fields
            else "project_allocation_id"
        )
        groups = flight.read_group(
            [
                ("departure_date", ">=", today - timedelta(days=365)),
                ("booking_state", "in", ("booked", "completed")),
            ],
            ["total_company:sum"],
            [group_field],
            limit=8,
            orderby="total_company desc",
        )
        result = []
        for grp in groups:
            ref = grp.get(group_field)
            result.append(
                {
                    "project_id": ref[0] if ref else False,
                    "label": ref[1] if ref else "(unassigned)",
                    "value": float(grp.get("total_company") or 0.0),
                }
            )
        return result
