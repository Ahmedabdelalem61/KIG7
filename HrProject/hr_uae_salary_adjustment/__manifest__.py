# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Salary Adjustments",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Payroll",
    "summary": "Salary adjustments / allowances / deductions with single-stage "
    "HR Manager approval. Supports one-shot, from/to and recurring modes.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/ir_sequence_data.xml",
        "views/hr_uae_salary_adjustment_views.xml",
        "views/hr_uae_salary_adjustment_menus.xml",
    ],
    "installable": True,
    "application": False,
}
