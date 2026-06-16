# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Dashboards in Company Currency",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Display all custom HR/payroll dashboards in the company currency: "
    "relabel money to the company currency and convert flight (and salary "
    "adjustment) amounts instead of summing raw foreign-currency values.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_flight_currency",
        "hr_uae_xlsx_io",
        "hr_uae_multicurrency",
    ],
    "data": [
        "views/hr_uae_payroll_dashboard_views.xml",
    ],
}
