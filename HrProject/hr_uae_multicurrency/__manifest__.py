# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Multi-currency Contracts",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Denominate contracts in any currency. Payroll converts to the "
    "company currency at the payslip period-end exchange rate (fresh each run); "
    "flight deductions and salary adjustments are converted too. Fails safe when "
    "a rate is missing.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_payroll",
        "hr_uae_salary_adjustment",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/hr_contract_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
