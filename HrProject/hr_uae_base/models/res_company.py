from odoo import api, models

# Project policy: the operating currency of the company, defined in CODE so a
# fresh install (e.g. production) gets the same currency as staging without
# relying on anything stored in the database. AED stays active as the local
# (contract) currency; payroll converts via hr_uae_multicurrency.
HR_UAE_COMPANY_CURRENCY_XMLID = "base.USD"


class ResCompany(models.Model):  # pylint: disable=too-few-public-methods
    """UAE bootstrap defaults for companies (country, currency, calendar)."""

    _inherit = "res.company"

    def _hr_uae_company_currency(self):
        """The code-defined company currency (see module-level constant)."""
        return self.env.ref(
            HR_UAE_COMPANY_CURRENCY_XMLID, raise_if_not_found=False
        )

    def _hr_uae_may_force_currency(self):
        """Currency is only bootstrapped while module data loads at install
        time (``install_mode``). Outside of that, an explicitly selected
        company currency is respected — silently flipping a live company's
        currency re-denominates every stored monetary amount and is never
        safe."""
        return bool(self.env.context.get("install_mode"))

    @api.model
    def _hr_uae_apply_defaults(self):
        """Apply UAE-friendly defaults to companies that look like UAE companies.

        Only adjusts companies whose country is UAE. The company-currency
        default (USD, see ``HR_UAE_COMPANY_CURRENCY_XMLID``) is applied at
        module install only; an explicitly chosen currency is never
        overridden afterwards. Safe to call multiple times.
        """
        uae = self.env.ref("base.ae", raise_if_not_found=False)
        currency = self._hr_uae_company_currency()
        uae_calendar = self.env.ref(
            "hr_uae_base.resource_calendar_uae", raise_if_not_found=False
        )
        if not uae:
            return
        force_currency = self._hr_uae_may_force_currency()
        companies = self.sudo().search([]).filtered(  # pylint: disable=no-search-all
            lambda company: company.partner_id.country_id == uae
        )
        for company in companies:
            vals = {}
            if force_currency and currency and company.currency_id != currency:
                vals["currency_id"] = currency.id
            if uae_calendar and not company.resource_calendar_id:
                vals["resource_calendar_id"] = uae_calendar.id
            if vals:
                company.write(vals)

    @api.model
    def _hr_uae_enforce_main_company(self):
        """Pin the main company to UAE, then apply UAE defaults.

        Like ``_hr_uae_apply_defaults``, the company currency is only set
        during install — an explicit currency choice survives upgrades and
        manual re-runs of this method."""
        main_company = self.env.ref("base.main_company", raise_if_not_found=False)
        uae = self.env.ref("base.ae", raise_if_not_found=False)
        currency = self._hr_uae_company_currency()
        uae_calendar = self.env.ref(
            "hr_uae_base.resource_calendar_uae", raise_if_not_found=False
        )
        if main_company and uae:
            vals = {}
            if (
                self._hr_uae_may_force_currency()
                and currency
                and main_company.currency_id != currency
            ):
                vals["currency_id"] = currency.id
            if uae_calendar and main_company.resource_calendar_id != uae_calendar:
                vals["resource_calendar_id"] = uae_calendar.id
            if main_company.partner_id.country_id != uae:
                main_company.partner_id.sudo().write({"country_id": uae.id})
            if vals:
                main_company.sudo().write(vals)
        self._hr_uae_apply_defaults()
