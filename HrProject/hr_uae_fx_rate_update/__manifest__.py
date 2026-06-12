# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Online Exchange Rates",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Daily automatic update of currency exchange rates from a free "
    "online source (no API key), plus a manual 'Update now' action. Keeps "
    "res.currency rates current so the multi-currency payroll conversion stays "
    "close to the real rate.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "base",
    ],
    "data": [
        "data/res_currency_activate.xml",
        "data/ir_cron.xml",
        "data/server_action.xml",
    ],
}
