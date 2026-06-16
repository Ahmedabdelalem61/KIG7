from odoo import api, fields, models

# Calls to the project's _hr_uae_* currency helpers on res.currency records.
# pylint: disable=protected-access


class HrUaeFlight(models.Model):  # pylint: disable=too-few-public-methods
    """Add per-ticket currency valuation: a company-currency total snapshotted
    at a rate date, refreshable before booking, and an expense created in the
    company currency."""

    _inherit = "hr.uae.flight"

    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        readonly=True,
    )
    rate_date = fields.Date(
        default=fields.Date.context_today,
        tracking=True,
        help="Exchange-rate date used to value the ticket in the company "
        "currency. Defaults to the creation date; use 'Refresh Rate' to bring "
        "it to today before booking.",
    )
    total_company = fields.Monetary(
        string="Total (Company Currency)",
        currency_field="company_currency_id",
        compute="_compute_total_company",
        store=True,
        help="Ticket total converted to the company currency at the rate date.",
    )

    @api.depends("total", "currency_id", "rate_date", "company_id")
    def _compute_total_company(self):
        """Soft conversion for display: shows 0 when no rate exists yet so data
        entry never errors (booking uses the strict path)."""
        for flight in self:
            company = flight.company_id or self.env.company
            currency = flight.currency_id or company.currency_id
            date = flight.rate_date or fields.Date.context_today(flight)
            flight.total_company = currency._hr_uae_to_company(
                flight.total, company, date, raise_if_missing=False
            )

    def action_refresh_rate(self):
        """Pull the latest online rates and stamp the rate date to today, so
        the company-currency total is up to date before booking. Never raises
        on a provider/network failure."""
        self.env["res.currency"].sudo()._hr_uae_cron_update_rates()
        today = fields.Date.context_today(self)
        self.write({"rate_date": today})
        missing = self.filtered(
            lambda f: f.currency_id
            and f.currency_id != f.company_currency_id
            and not f.currency_id._hr_uae_has_rate(f.company_id, today)
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Exchange rate refreshed"),
                "message": (
                    self.env._(
                        "No rate available yet for: %s. Add it in "
                        "Accounting → Currencies.",
                        ", ".join(missing.mapped("currency_id.name")),
                    )
                    if missing
                    else self.env._("Ticket totals re-valued at today's rate.")
                ),
                "type": "warning" if missing else "success",
                "sticky": False,
            },
        }

    def _prepare_expense_vals(self):
        """Create the expense in the COMPANY currency, valued at the ticket's
        rate date. A foreign ticket with no rate raises a clear UserError at
        booking (strict conversion)."""
        vals = super()._prepare_expense_vals()
        company = self.company_id or self.env.company
        date = self.rate_date or fields.Date.context_today(self)
        vals["currency_id"] = company.currency_id.id
        vals["total_amount_currency"] = self.currency_id._hr_uae_to_company(
            self.total, company, date
        )
        return vals
