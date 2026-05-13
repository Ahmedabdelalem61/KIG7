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
        domain = [("country_id", "=", uae.id)]
        for company in self.sudo().search(domain):
            vals = {}
            if aed and company.currency_id != aed:
                vals["currency_id"] = aed.id
            if uae_calendar and not company.resource_calendar_id:
                vals["resource_calendar_id"] = uae_calendar.id
            if vals:
                company.write(vals)
