# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "KIG7 Access Rights",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Hidden",
    "summary": "KIG7 role-based access: HR Officer, HR Manager and Payroll & "
    "Accounting Manager roles under one 'KIG7 Access Rights' category, with "
    "predefined users, mutual exclusivity, and blocking of Discuss / Calendar "
    "/ Website / Settings for non-administrators.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_xlsx_io",
        "calendar",
        "website",
    ],
    "data": [
        "security/hr_uae_access_security.xml",
        "security/ir.model.access.csv",
        "data/menu_restrictions.xml",
        "data/res_users_data.xml",
    ],
}
