import json
import logging
import threading
import urllib.request

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Free, no-key source. Returns rates as "units of <code> per 1 <base>", which is
# exactly Odoo's res.currency.rate.rate convention when <base> is the company
# currency.
DEFAULT_FX_URL = "https://open.er-api.com/v6/latest/%s"

# Currencies the project keeps active (code-defined; reapplied on every module
# upgrade so staging and production never drift apart).
HR_UAE_ACTIVE_CURRENCY_CODES = ("USD", "AED", "EUR", "GBP")


class ResCurrency(models.Model):  # pylint: disable=too-few-public-methods
    """Extend res.currency with UAE-project online FX rate fetching."""

    _inherit = "res.currency"

    @api.model
    def _hr_uae_activate_currencies(self):
        """Activate the project currencies (called from a data file on every
        install/upgrade — base currency records are noupdate, so a plain
        ``<record>`` override would be skipped on upgrade)."""
        currencies = self.with_context(active_test=False).search(
            [("name", "in", list(HR_UAE_ACTIVE_CURRENCY_CODES))]
        )
        to_activate = currencies.filtered(lambda c: not c.active)
        if to_activate:
            to_activate.write({"active": True})
        return len(to_activate)

    def write(self, vals):
        """On activation (active: False -> True), immediately fetch today's
        online rate for the newly activated currencies instead of waiting for
        the daily cron."""
        activating = self.browse()
        if vals.get("active"):
            activating = self.filtered(lambda c: not c.active)
        result = super().write(vals)
        if activating:
            activating._hr_uae_fetch_rates_on_activation()  # pylint: disable=protected-access
        return result

    def _hr_uae_fetch_rates_on_activation(self):
        """Fetch and store today's rate for ``self`` (newly activated
        currencies) against every company currency.

        Never raises: a provider failure only logs a warning, so the
        activation itself always succeeds (the daily cron retries later).
        Skipped during XML data loading (install/upgrade) and in test mode
        unless forced via the ``hr_uae_fx_force_autofetch`` context key, so
        installs and unrelated test suites never hit the network."""
        if self.env.context.get("hr_uae_fx_skip_autofetch"):
            return 0
        if self.env.context.get("install_mode"):
            return 0
        if getattr(
            threading.current_thread(), "testing", False
        ) and not self.env.context.get("hr_uae_fx_force_autofetch"):
            return 0
        total = 0
        companies = self.env["res.company"].sudo().search([])  # pylint: disable=no-search-all
        for company in companies:
            base = company.currency_id
            if not base:
                continue
            # The company's own currency converts 1:1 — nothing to fetch.
            targets = self - base
            if not targets:
                continue
            rates = self._hr_uae_fetch_rates(base.name)
            wanted = {c.name: rates[c.name] for c in targets if rates.get(c.name)}
            missing = [c.name for c in targets if not rates.get(c.name)]
            if missing:
                _logger.warning(
                    "hr_uae_fx: no online rate at activation for %s "
                    "(company %s); the daily cron will retry",
                    ", ".join(missing),
                    company.name,
                )
            if wanted:
                total += self.with_context(  # pylint: disable=protected-access
                    hr_uae_fx_skip_autofetch=True
                )._hr_uae_upsert_rates(company, wanted)
        return total

    @api.model
    def _hr_uae_fetch_rates(self, base_code):
        """Fetch {currency_code: rate_per_1_base} for ``base_code``.

        Returns an empty dict on any failure (network, bad payload) and logs a
        warning — never raises, so the cron can't crash the scheduler."""
        url = DEFAULT_FX_URL % base_code
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = json.load(response)
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
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
        rate_model = self.env["res.currency.rate"].sudo()
        count = 0
        for currency in self.search([("id", "!=", base.id)]):
            value = rates.get(currency.name)
            if not value or value <= 0:
                continue
            existing = rate_model.search(
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
                rate_model.create(
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
        companies = self.env["res.company"].sudo().search([])  # pylint: disable=no-search-all
        for company in companies:
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
                "title": self.env._("Exchange rates updated"),
                "message": self.env._("%s currency rate(s) refreshed for today.", count),
                "type": "success" if count else "warning",
                "sticky": False,
            },
        }
