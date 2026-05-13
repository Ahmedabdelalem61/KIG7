# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Contract Termination",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Contract termination workflow: archives the employee, ends "
    "the contract, cancels future payslips, and renders the Termination report.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/hr_uae_termination_views.xml",
        "views/hr_uae_termination_menus.xml",
        "report/hr_uae_termination_report.xml",
        "report/hr_uae_termination_report_template.xml",
    ],
    "installable": True,
    "application": False,
}
