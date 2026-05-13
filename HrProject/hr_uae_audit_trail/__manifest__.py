# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Audit Trail",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Field-level audit trail for HR UAE records "
    "(old vs new value, who, when) with employee tab and PDF report.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_master_data",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_uae_audit_security.xml",
        "wizard/hr_uae_audit_report_wizard_views.xml",
        "views/hr_uae_audit_log_views.xml",
        "views/hr_employee_views.xml",
        "report/hr_uae_audit_report.xml",
        "report/hr_uae_audit_report_template.xml",
        "views/hr_uae_audit_menus.xml",
    ],
    "installable": True,
    "application": False,
}
