# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Flight Ticket Currency",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Per-ticket currency selection on flight tickets with a live "
    "company-currency total snapshotted by rate date (refreshable before "
    "booking); the generated expense is created in the company currency.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_flights",
        "hr_uae_multicurrency",
        "hr_uae_fx_rate_update",
    ],
    "data": [
        "views/hr_uae_flight_views.xml",
    ],
}
