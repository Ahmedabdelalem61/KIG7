from odoo import _, fields, models
from odoo.exceptions import UserError


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _hr_uae_has_rate(self, company, date):
        """True if `self` can be converted to/from the company currency at
        `date` (the company currency itself is always convertible at rate 1)."""
        self.ensure_one()
        if self == company.currency_id:
            return True
        return bool(
            self.env["res.currency.rate"].sudo().search_count(
                [
                    ("currency_id", "=", self.id),
                    ("name", "<=", date),
                    ("company_id", "in", [company.id, False]),
                ]
            )
        )

    def _hr_uae_to_company(self, amount, company, date, raise_if_missing=True):
        """Convert `amount` (expressed in `self`) to the company currency at
        `date`.

        Fails safe: if `self` is not the company currency and no exchange rate
        is defined on or before `date`, raise a clear error so payroll never
        silently pays at a 1:1 rate. Pass ``raise_if_missing=False`` for soft
        display refreshes (returns 0.0 when no rate is available)."""
        self.ensure_one()
        company_currency = company.currency_id
        amount = amount or 0.0
        if not amount or self == company_currency:
            return amount
        if not date:
            date = fields.Date.context_today(self)
        if not self._hr_uae_has_rate(company, date):
            if raise_if_missing:
                raise UserError(
                    _(
                        "No exchange rate is defined for %(cur)s on or before "
                        "%(date)s. Add it in Accounting → Currencies.",
                        cur=self.name,
                        date=date,
                    )
                )
            return 0.0
        return self._convert(amount, company_currency, company, date)

    def _hr_uae_from_company(self, amount, company, date):
        """Convert `amount` (in the company currency) into `self`. Soft: returns
        the amount unchanged when no rate exists (used only to seed an entry
        field on currency change; payroll always uses the strict path)."""
        self.ensure_one()
        company_currency = company.currency_id
        amount = amount or 0.0
        if not amount or self == company_currency:
            return amount
        if not date:
            date = fields.Date.context_today(self)
        if not self._hr_uae_has_rate(company, date):
            return amount
        return company_currency._convert(amount, self, company, date)
