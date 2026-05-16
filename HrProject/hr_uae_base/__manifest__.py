# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Base",
    "version": "18.0.1.0.1",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Foundation module for UAE HR Admin platform "
    "(country, currency, working calendar, security groups, root menu).",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr",
        "hr_contract",
        "resource",
    ],
    "data": [
        "security/hr_uae_security.xml",
        "security/ir.model.access.csv",
        "data/res_currency_data.xml",
        "data/resource_calendar_data.xml",
        "data/res_company_data.xml",
        "data/hr_uae_public_holidays_data.xml",
        "data/res_users_admin_groups.xml",
        "views/hr_uae_menus.xml",
    ],
    "installable": True,
    "application": False,
}
