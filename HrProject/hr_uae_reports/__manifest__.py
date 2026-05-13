# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Reports & Dashboard",
    "version": "18.0.1.0.2",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Consolidated PDF reports and a modern dashboard for the HR "
    "UAE Admin platform: Master Data, Payroll, Tickets, Vacations, "
    "Movement Tracking, Termination and Audit Trail.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_master_data",
        "hr_uae_audit_trail",
        "hr_uae_documents",
        "hr_uae_leaves",
        "hr_uae_flights",
        "hr_uae_payroll",
        "hr_uae_salary_adjustment",
        "hr_uae_termination",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/hr_uae_master_data_report.xml",
        "report/hr_uae_master_data_report_template.xml",
        "report/hr_uae_movement_tracking_report.xml",
        "report/hr_uae_movement_tracking_report_template.xml",
        "views/hr_uae_dashboard_views.xml",
        "views/hr_uae_live_dashboard_actions.xml",
        "views/hr_uae_reports_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_uae_reports/static/src/live_dashboard/live_dashboard.js",
            "hr_uae_reports/static/src/live_dashboard/live_dashboard.xml",
            "hr_uae_reports/static/src/live_dashboard/live_dashboard.scss",
        ],
    },
    "installable": True,
    "application": False,
}
