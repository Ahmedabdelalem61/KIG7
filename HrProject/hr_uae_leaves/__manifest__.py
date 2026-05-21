# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Leaves & Movements",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "UAE leave types (Annual / Special / Medical / Unpaid) with "
    "auto-deduction rule for Unpaid, Movement Tracking report, and "
    "vacation/permit alerts.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_master_data",
        "hr_uae_audit_trail",
        "hr_holidays",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_leave_type_data.xml",
        "data/hr_leave_type_defaults_data.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        "views/hr_leave_type_views.xml",
        "views/hr_leave_views.xml",
        "views/hr_uae_movement_tracking_views.xml",
        "views/hr_uae_leaves_menus.xml",
    ],
    "installable": True,
    "application": False,
}
