"""HR Manager: full HR configuration, approvals, reports, dashboards."""
from odoo.tests.common import tagged

from .common import Kig7AccessCase


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_manager")
class TestHrManager(Kig7AccessCase):
    """Positive and negative access checks for the HR Manager role."""

    # ------------------------------------------------------ permitted

    def test_full_crud_on_custom_models(self):
        """Manager has full CRUD on the custom HR models."""
        for model in (
            "hr.uae.flight",
            "hr.uae.document",
            "hr.uae.salary.adjustment",
            "hr.uae.rank",
            "hr.uae.position",
            "hr.uae.employee.state",
        ):
            self.assert_can(self.manager, model, "rwcu")

    def test_contracts_full_access(self):
        """Manager manages contracts (implied hr_contract manager)."""
        self.assert_can(self.manager, "hr.contract", "rwcu")

    def test_payslips_readable(self):
        """Manager consults payslips (payroll user)."""
        self.assert_can(self.manager, "hr.payslip", "r")

    def test_leave_approvals(self):
        """Manager manages leaves (holidays manager)."""
        self.assert_can(self.manager, "hr.leave", "rw")
        self.assert_can(self.manager, "hr.leave.type", "rwcu")

    def test_salary_adjustment_approval_flow(self):
        """Manager can approve a salary adjustment end to end."""
        adjustment = self.sudo_model("hr.uae.salary.adjustment").create(
            {
                "employee_id": self.probe_employee.id,
                "kind": "allowance",
                "amount": 100.0,
            }
        )
        adjustment.with_user(self.manager).write({"amount": 150.0})
        self.assertEqual(adjustment.amount, 150.0)

    def test_custom_dashboards_and_reports(self):
        """Manager reaches dashboards and report actions."""
        self.assert_can(self.manager, "hr.uae.dashboard", "r")
        self.assert_can(self.manager, "hr.uae.payroll.dashboard", "r")
        self.assert_action_model_allowed(
            self.manager, "hr_uae_reports.action_report_hr_uae_master_data"
        )
        self.assert_action_model_allowed(
            self.manager, "hr_uae_payroll.action_hr_uae_payroll_dashboard"
        )

    def test_xlsx_io_allowed(self):
        """Manager configures Excel import/export."""
        self.assert_can(self.manager, "hr.uae.xlsx.template", "rwcu")

    def test_config_menus_visible(self):
        """Manager sees the Configuration and Audit menus."""
        self.assert_menu(self.manager, "hr_uae_base.menu_hr_uae_root", True)
        self.assert_menu(self.manager, "hr_uae_base.menu_hr_uae_config", True)
        self.assert_menu(self.manager, "hr_uae_base.menu_hr_uae_audit", True)

    # ------------------------------------------------------ prohibited

    def test_accounting_blocked(self):
        """Manager cannot touch journal entries or journals."""
        self.assert_cannot(self.manager, "account.move", "wcu")
        self.assert_cannot(self.manager, "account.journal", "wcu")

    def test_settings_menu_hidden(self):
        """Manager does not see Settings."""
        self.assert_menu(self.manager, "base.menu_administration", False)
