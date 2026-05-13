# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Payroll",
    "version": "18.0.1.0.4",
    "license": "LGPL-3",
    "category": "Payroll",
    "summary": "UAE salary structure, hold-during-vacation logic with on_hold "
    "state and return flag, and the Payroll Dashboard table.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_master_data",
        "hr_uae_audit_trail",
        "hr_uae_leaves",
        "hr_uae_flights",
        "payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_payroll_structure_data.xml",
        "data/hr_salary_rule_data.xml",
        "views/hr_payslip_views.xml",
        "views/hr_leave_payroll_buttons.xml",
        "views/hr_uae_payroll_dashboard_views.xml",
        "views/hr_uae_payroll_live_dashboard_actions.xml",
        "views/hr_uae_payroll_menus.xml",
        "report/hr_uae_payroll_report.xml",
        "report/hr_uae_payroll_report_template.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_uae_payroll/static/src/live_dashboard/payroll_live_dashboard.js",
            "hr_uae_payroll/static/src/live_dashboard/payroll_live_dashboard.xml",
            "hr_uae_payroll/static/src/live_dashboard/payroll_live_dashboard.scss",
        ],
    },
    "installable": True,
    "application": False,
}
