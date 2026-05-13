# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE - Documents",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Typed employee documents (passport, visa, medical, photo, "
    "contract) with expiry alerts and per-owner record rules.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "hr_uae_master_data",
        "hr_uae_audit_trail",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_uae_documents_security.xml",
        "data/hr_uae_documents_cron.xml",
        "data/mail_template_data.xml",
        "views/hr_uae_document_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_uae_documents_menus.xml",
    ],
    "installable": True,
    "application": False,
}
