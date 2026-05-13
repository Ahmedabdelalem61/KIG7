# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Flight Tickets",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Flight ticket management built on top of hr.expense; "
    "creates expenses for tickets and pushes employee-paid tickets to payroll.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_master_data",
        "hr_uae_audit_trail",
        "hr_expense",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_product_data.xml",
        "data/ir_sequence_data.xml",
        "views/hr_uae_flight_views.xml",
        "views/hr_uae_flights_menus.xml",
        "report/hr_uae_flights_report.xml",
        "report/hr_uae_flights_report_template.xml",
    ],
    "installable": True,
    "application": False,
}
