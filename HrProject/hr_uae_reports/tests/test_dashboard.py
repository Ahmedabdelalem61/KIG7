from odoo.tests.common import TransactionCase


class TestHrUaeDashboard(TransactionCase):
    def test_dashboard_record_creation_and_metrics(self):
        # A few extra employees to exercise the metrics.
        Employee = self.env["hr.employee"]
        Employee.create({"name": "Dashboard E1"})
        Employee.create({"name": "Dashboard E2"})
        dashboard = self.env["hr.uae.dashboard"].create({})
        self.assertGreaterEqual(dashboard.employees_total, 2)
        self.assertGreaterEqual(dashboard.employees_active, 0)
        self.assertGreaterEqual(dashboard.held_payslips, 0)
        self.assertEqual(dashboard.currency_id, self.env.ref("base.AED"))

    def test_dashboard_action_returns_act_window(self):
        action = self.env["hr.uae.dashboard"].action_open_dashboard()
        self.assertEqual(action["res_model"], "hr.uae.dashboard")
        self.assertEqual(action["view_mode"], "form")
