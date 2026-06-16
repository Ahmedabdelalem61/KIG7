# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Initial Data (KIG7)",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Data-driven initialization of the KIG7 master configuration that "
    "was originally created by hand (company name, provision/pension salary "
    "rules, departments). Installing it on a fresh database reproduces the "
    "current master setup. Transactional/per-employee data is never seeded.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    # Depend on the COMPLETE project so one `-i hr_uae_init_data` installs
    # every module the client runs (hr_uae_app does NOT pull access/currency/
    # xlsx/dashboards) plus this module's master-data seeds.
    "depends": [
        "hr_uae_app",
        "hr_uae_access",
        "hr_uae_multicurrency",
        "hr_uae_fx_rate_update",
        "hr_uae_project_department",
        "hr_uae_xlsx_io",
        "hr_uae_flight_currency",
        "hr_uae_dashboard_currency",
    ],
    "data": [
        "data/res_company_data.xml",
        "data/hr_department_data.xml",
        "data/hr_salary_rule_data.xml",
    ],
}
