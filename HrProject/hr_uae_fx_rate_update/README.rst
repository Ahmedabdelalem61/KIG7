==============================
HR UAE - Online Exchange Rates
==============================

Keeps ``res.currency`` exchange rates up to date automatically, so the
multi-currency payroll conversion (``hr_uae_multicurrency``) stays close to the
real rate.

What it does
============

* A **daily scheduled action** fetches rates from a free, no-key online source
  and writes a ``res.currency.rate`` row (dated today) for every **active**
  currency, relative to each company's currency.
* A **manual “Update Exchange Rates (online)”** action is available from the
  Currencies list (Settings → Technical → Currencies → ⚙ Action).
* The source URL is an **ir.config_parameter** (``hr_uae_fx_rate_update.url``,
  default ``https://open.er-api.com/v6/latest/%s``) — change it to use another
  provider. The provider must return rates as *units of each currency per 1 unit
  of the base*, which is Odoo's rate convention.

Notes
=====

* Only **active** currencies get rates — activate the currencies you use first.
* It never raises on a network/provider error (it logs a warning and skips), so
  the scheduler is safe.
* Accuracy depends on the chosen provider. For production payroll, point it at an
  authoritative feed your finance team approves.
