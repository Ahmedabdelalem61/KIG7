from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _hr_uae_apply_defaults(self):
        """Apply UAE-friendly defaults to companies that look like UAE companies.

        Only adjusts companies whose country is UAE; never overrides an explicitly
        chosen value. Safe to call multiple times.
        """
        uae = self.env.ref("base.ae", raise_if_not_found=False)
        aed = self.env.ref("base.AED", raise_if_not_found=False)
        uae_calendar = self.env.ref(
            "hr_uae_base.resource_calendar_uae", raise_if_not_found=False
        )
        if not uae:
            return
        companies = self.sudo().search([]).filtered(
            lambda company: company.partner_id.country_id == uae
        )
        for company in companies:
            vals = {}
            if aed and company.currency_id != aed:
                vals["currency_id"] = aed.id
            if uae_calendar and not company.resource_calendar_id:
                vals["resource_calendar_id"] = uae_calendar.id
            if vals:
                company.write(vals)

    @api.model
    def _hr_uae_enforce_main_company(self):
        """Pin the main company to UAE, then apply UAE defaults."""
        main_company = self.env.ref("base.main_company", raise_if_not_found=False)
        uae = self.env.ref("base.ae", raise_if_not_found=False)
        aed = self.env.ref("base.AED", raise_if_not_found=False)
        uae_calendar = self.env.ref(
            "hr_uae_base.resource_calendar_uae", raise_if_not_found=False
        )
        if main_company and uae:
            vals = {}
            if aed and main_company.currency_id != aed:
                vals["currency_id"] = aed.id
            if uae_calendar and main_company.resource_calendar_id != uae_calendar:
                vals["resource_calendar_id"] = uae_calendar.id
            if main_company.partner_id.country_id != uae:
                main_company.partner_id.sudo().write({"country_id": uae.id})
            if vals:
                main_company.sudo().write(vals)
        self._hr_uae_apply_defaults()
