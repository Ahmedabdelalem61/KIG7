# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Excel Import / Export",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Dynamic, configurable XLSX import/export for HR UAE data with a "
    "normal-ORM validation layer (no SQL bypass). Predefined templates for "
    "employees, contracts, flights, documents, salary adjustments, "
    "terminations and an export-only payroll template.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        # Pulls in payroll, flights, documents, salary_adjustment, termination,
        # master_data, base and adds the Project (department_id) columns.
        "hr_uae_project_department",
    ],
    "external_dependencies": {
        "python": ["openpyxl"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/xlsx_template_views.xml",
        "views/xlsx_io_wizard_views.xml",
        "views/hr_uae_payroll_dashboard_views.xml",
        "views/xlsx_io_menus.xml",
        "data/xlsx_predefined_templates.xml",
    ],
    "installable": True,
    "application": False,
}
