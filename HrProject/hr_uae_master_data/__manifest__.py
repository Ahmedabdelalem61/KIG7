# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Master Data",
    "version": "18.0.1.0.1",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Single source of truth for UAE employee master data: rank, "
    "passport, roster, position, project allocation, cost center, status, visa.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_base",
        "hr_contract",
        "hr_holidays",
        "analytic",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_analytic_plan_data.xml",
        "data/account_analytic_account_data.xml",
        "data/hr_uae_rank_data.xml",
        "data/hr_uae_position_data.xml",
        "data/ir_cron_data.xml",
        "views/hr_uae_rank_views.xml",
        "views/hr_uae_position_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_uae_analytic_menus.xml",
        "views/hr_uae_master_data_menus.xml",
    ],
    "installable": True,
    "application": False,
}
