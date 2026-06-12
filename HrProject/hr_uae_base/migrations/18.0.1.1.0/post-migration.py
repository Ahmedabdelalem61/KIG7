"""Switch existing databases to the code-defined company currency (USD).

The currency is defined in code (hr_uae_base.models.res_company
HR_UAE_COMPANY_CURRENCY_XMLID) so staging and production stay aligned without
depending on database state. This migration converges an already-installed
database to that policy:

1. Delete the journal entries that block a company-currency change (Odoo's
   account module forbids the switch while any journal item exists).
2. Switch every company still on another currency to USD.
3. Purge USD rate rows — the company currency must have no rates (stale rows
   from the AED era would corrupt every conversion).

Rates for AED/EUR/GBP against the new USD base are refreshed by
hr_uae_fx_rate_update (manual action or daily cron) after the upgrade.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Converge the database to the code-defined USD company currency."""
    if not version:
        return  # fresh install: the install-time bootstrap handles it
    env = api.Environment(cr, SUPERUSER_ID, {})
    usd = env.ref("base.USD", raise_if_not_found=False)
    if not usd:
        return
    usd.active = True
    for company in env["res.company"].sudo().search([]):
        if company.currency_id == usd:
            continue
        if "account.move" in env:
            moves = env["account.move"].sudo().search(
                [("company_id", "=", company.id)]
            )
            if moves:
                _logger.warning(
                    "hr_uae_base: deleting %s journal entries of company %s "
                    "to allow the USD currency switch",
                    len(moves),
                    company.name,
                )
                moves.filtered(lambda m: m.state == "posted").button_draft()
                moves.with_context(force_delete=True).unlink()
        company.write({"currency_id": usd.id})
        _logger.info(
            "hr_uae_base: company %s switched to USD (code-defined currency)",
            company.name,
        )
    # The company currency must have no rate rows: stale ones (written while
    # AED was the base) would corrupt every conversion.
    stale = env["res.currency.rate"].sudo().search([("currency_id", "=", usd.id)])
    if stale:
        _logger.info("hr_uae_base: purging %s stale USD rate rows", len(stale))
        stale.unlink()
