import json
import logging
import urllib.request

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

# Free, no-key source. Returns rates as "units of <code> per 1 <base>", which is
# exactly Odoo's res.currency.rate.rate convention when <base> is the company
# currency. The URL is stored in ir.config_parameter so it can be swapped.
DEFAULT_FX_URL = "https://open.er-api.com/v6/latest/%s"
_PARAM_KEY = "hr_uae_fx_rate_update.url"


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _hr_uae_fx_url(self, base_code):
        param = self.env["ir.config_parameter"].sudo().get_param(
            _PARAM_KEY, DEFAULT_FX_URL
        )
        return param % base_code if "%s" in param else param + base_code

    @api.model
    def _hr_uae_fetch_rates(self, base_code):
        """Fetch {currency_code: rate_per_1_base} for ``base_code``.

        Returns an empty dict on any failure (network, bad payload) and logs a
        warning — never raises, so the cron can't crash the scheduler."""
        url = self._hr_uae_fx_url(base_code)
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = json.load(response)
        except Exception as exc:  # noqa: BLE001 - network/parse must not crash cron
            _logger.warning("hr_uae_fx: fetch failed for %s: %s", base_code, exc)
            return {}
        if data.get("result") == "error":
            _logger.warning(
                "hr_uae_fx: provider error for %s: %s",
                base_code,
                data.get("error-type") or data,
            )
            return {}
        return data.get("rates") or {}

    @api.model
    def _hr_uae_upsert_rates(self, company, rates, date=None):
        """Create/update today's ``res.currency.rate`` for each ACTIVE currency
        present in ``rates`` (relative to the company currency). Returns the
        number of currencies written."""
        if not rates:
            return 0
        date = date or fields.Date.context_today(self)
        base = company.currency_id
        Rate = self.env["res.currency.rate"].sudo()
        count = 0
        for currency in self.search([("id", "!=", base.id)]):
            value = rates.get(currency.name)
            if not value or value <= 0:
                continue
            existing = Rate.search(
                [
                    ("currency_id", "=", currency.id),
                    ("name", "=", date),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            if existing:
                existing.rate = value
            else:
                Rate.create(
                    {
                        "currency_id": currency.id,
                        "name": date,
                        "rate": value,
                        "company_id": company.id,
                    }
                )
            count += 1
        return count

    @api.model
    def _hr_uae_cron_update_rates(self):
        """Daily entrypoint: refresh active-currency rates for every company."""
        total = 0
        for company in self.env["res.company"].sudo().search([]):
            base = company.currency_id
            if not base:
                continue
            rates = self._hr_uae_fetch_rates(base.name)
            total += self._hr_uae_upsert_rates(company, rates)
        _logger.info("hr_uae_fx: updated %s currency rate(s)", total)
        return total

    @api.model
    def action_hr_uae_update_rates_now(self):
        """Manual trigger (server action / button). Shows a toast."""
        count = self._hr_uae_cron_update_rates()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Exchange rates updated"),
                "message": _("%s currency rate(s) refreshed for today.") % count,
                "type": "success" if count else "warning",
                "sticky": False,
            },
        }
