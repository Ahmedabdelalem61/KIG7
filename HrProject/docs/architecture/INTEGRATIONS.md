> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Integrations

## open.er-api.com

- Endpoint: `https://open.er-api.com/v6/latest/%s`, where `%s` is the company currency code.
- Authentication: none in code.
- Request shape: HTTP GET with base currency in the path.
- Response shape used by code: JSON object with `rates` mapping currency code to numeric rate; `result == "error"` is treated as provider error.
- Timeout: 20 seconds via `urllib.request.urlopen(url, timeout=20)`.
- Retry: no in-method retry; daily cron/manual action can retry later.
- Failure handling: catches all exceptions, logs warning, returns `{}`; cron does not raise.
- URL location: code constant `DEFAULT_FX_URL`, not `ir.config_parameter`.

Source: [../../hr_uae_fx_rate_update/models/res_currency.py](../../hr_uae_fx_rate_update/models/res_currency.py).

## Schedules And Triggers

| Trigger | Code | Frequency/guard |
|---|---|---|
| Daily FX cron | `_hr_uae_cron_update_rates()` | Every 1 day, active |
| Manual server action | `action_hr_uae_update_rates_now()` | User-triggered server action |
| Fetch on activation | `_hr_uae_fetch_rates_on_activation()` | Skips install mode; skips normal test threads unless forced |
| Currency activation data | `_hr_uae_activate_currencies()` | XML `<function>` activates USD/AED/EUR/GBP |

## Operational Risks

- Free provider accuracy/availability is outside KIG7 control.
- No retry/backoff inside the request method.
- Provider schema changes can silently produce empty rates and later payroll missing-rate errors.
- Rate semantics are critical: rates are units of target currency per 1 company-currency unit.

## Security Risks

No API key is used, so no API secret is stored. Network egress still reveals currency base requests. Keep deployment proxy/firewall rules outside this repository documented separately.
