"""HR Officer: operational HR access, custom dashboards, and denials."""
from odoo.tests.common import tagged

from .common import Kig7AccessCase


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_officer")
class TestHrOfficer(Kig7AccessCase):
    """Positive and negative access checks for the HR Officer role."""

    # ------------------------------------------------------ permitted

    def test_operational_models_readable(self):
        """Officer reads employees, master data, leaves, flights, documents."""
        for model in (
            "hr.employee",
            "hr.uae.rank",
            "hr.uae.position",
            "hr.uae.employee.state",
            "hr.leave",
            "hr.uae.flight",
            "hr.uae.document",
            "hr.uae.salary.adjustment",
        ):
            self.assert_can(self.officer, model, "r")

    def test_flight_create_write(self):
        """Officer creates and updates flight tickets, but cannot delete."""
        self.assert_can(self.officer, "hr.uae.flight", "rwc")
        self.assert_cannot(self.officer, "hr.uae.flight", "u")

    def test_document_create_write(self):
        """Officer creates and updates employee documents, but cannot delete."""
        self.assert_can(self.officer, "hr.uae.document", "rwc")
        self.assert_cannot(self.officer, "hr.uae.document", "u")
        document = self.sudo_model("hr.uae.document").create(
            {
                "name": "Officer probe doc",
                "employee_id": self.probe_employee.id,
                "document_type": "other",
            }
        )
        document.with_user(self.officer).write({"name": "Officer touched"})
        self.assertEqual(document.name, "Officer touched")

    def test_salary_adjustment_create(self):
        """Officer can submit salary adjustments (no unlink)."""
        self.assert_can(self.officer, "hr.uae.salary.adjustment", "rwc")
        self.assert_cannot(self.officer, "hr.uae.salary.adjustment", "u")

    def test_custom_dashboards_readable(self):
        """Officer reads both custom dashboards (HR + payroll)."""
        self.assert_can(self.officer, "hr.uae.dashboard", "r")
        self.assert_can(self.officer, "hr.uae.payroll.dashboard", "r")
        self.assert_action_model_allowed(
            self.officer, "hr_uae_reports.action_hr_uae_dashboard"
        )
        self.assert_action_model_allowed(
            self.officer, "hr_uae_payroll.action_hr_uae_payroll_dashboard"
        )

    def test_root_menu_visible(self):
        """Officer sees the HR UAE Admin application."""
        self.assert_menu(self.officer, "hr_uae_base.menu_hr_uae_root", True)

    # ------------------------------------------------------ prohibited

    def test_contracts_blocked(self):
        """Officer has no access to contracts (wage data)."""
        self.assert_cannot(self.officer, "hr.contract")

    def test_payslips_blocked(self):
        """Officer has no access to payslips or payslip runs."""
        self.assert_cannot(self.officer, "hr.payslip")
        self.assert_cannot(self.officer, "hr.payslip.run")

    def test_accounting_blocked(self):
        """Officer has no access to journal entries."""
        self.assert_cannot(self.officer, "account.move")

    def test_xlsx_templates_blocked(self):
        """Officer cannot use the Excel import/export configuration."""
        self.assert_cannot(self.officer, "hr.uae.xlsx.template")
        self.assert_action_model_blocked(
            self.officer, "hr_uae_xlsx_io.action_hr_uae_xlsx_template"
        )

    def test_config_menus_hidden(self):
        """Configuration and Audit menus are manager-only."""
        self.assert_menu(self.officer, "hr_uae_base.menu_hr_uae_config", False)
        self.assert_menu(self.officer, "hr_uae_base.menu_hr_uae_audit", False)

    def test_master_data_write_blocked(self):
        """Officer reads master data but cannot change it."""
        for model in ("hr.uae.rank", "hr.uae.position", "hr.uae.employee.state"):
            self.assert_cannot(self.officer, model, "wcu")
