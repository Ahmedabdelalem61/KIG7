"""Payroll & Accounting Manager: accounting/payroll/expenses in, custom HR out."""
# pylint: disable=duplicate-code
from odoo.tests.common import tagged

from .common import Kig7AccessCase


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_payroll")
class TestPayrollManager(Kig7AccessCase):
    """Positive and negative access checks for Payroll & Accounting Manager."""

    # ------------------------------------------------------ permitted

    def test_accounting_full_access(self):
        """Payroll manager administers accounting."""
        self.assert_can(self.payroll, "account.move", "rwcu")
        self.assert_can(self.payroll, "account.journal", "rwcu")

    def test_payroll_full_access(self):
        """Payroll manager runs payroll (payslips and batches)."""
        self.assert_can(self.payroll, "hr.payslip", "rwcu")
        self.assert_can(self.payroll, "hr.payslip.run", "rwcu")
        self.assert_can(self.payroll, "hr.salary.rule", "r")

    def test_expenses_full_access(self):
        """Payroll manager manages expenses."""
        self.assert_can(self.payroll, "hr.expense", "rwcu")
        self.assert_can(self.payroll, "hr.expense.sheet", "rwcu")

    def test_employee_contract_data(self):
        """Payroll manager reads employees and manages contracts (wages)."""
        self.assert_can(self.payroll, "hr.employee", "r")
        self.assert_can(self.payroll, "hr.contract", "rwcu")

    # ------------------------------------------------------ prohibited

    def test_custom_dashboards_blocked(self):
        """The custom HR/payroll dashboards are NOT accessible — neither the
        models nor the actions behind the menus."""
        self.assert_cannot(self.payroll, "hr.uae.dashboard")
        self.assert_cannot(self.payroll, "hr.uae.payroll.dashboard")
        self.assert_action_model_blocked(
            self.payroll, "hr_uae_payroll.action_hr_uae_payroll_dashboard"
        )
        self.assert_action_model_blocked(
            self.payroll, "hr_uae_reports.action_hr_uae_dashboard"
        )

    def test_custom_hr_models_blocked(self):
        """Custom HR operational/config models are NOT accessible."""
        for model in (
            "hr.uae.flight",
            "hr.uae.document",
            "hr.uae.salary.adjustment",
            "hr.uae.rank",
            "hr.uae.position",
            "hr.uae.employee.state",
            "hr.uae.xlsx.template",
        ):
            self.assert_cannot(self.payroll, model)

    def test_hr_uae_menus_hidden(self):
        """The whole HR UAE Admin application is invisible."""
        self.assert_menu(self.payroll, "hr_uae_base.menu_hr_uae_root", False)
        self.assert_menu(self.payroll, "hr_uae_base.menu_hr_uae_config", False)

    def test_settings_menu_hidden(self):
        """Payroll manager does not see Settings."""
        self.assert_menu(self.payroll, "base.menu_administration", False)

    def test_standard_dashboards_still_standard(self):
        """Standard app dashboards stay governed by standard groups: the
        accounting move model is readable through the account action while
        custom dashboards are not (asserted above)."""
        self.assert_action_model_allowed(
            self.payroll, "account.action_move_journal_line"
        )
