from datetime import date

from odoo.tests.common import TransactionCase


class TestHrUaeFlights(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Flight = cls.env["hr.uae.flight"]
        cls.Employee = cls.env["hr.employee"]
        cls.emp = cls.Employee.create({"name": "Flight Test"})

    def test_create_with_sequence(self):
        f = self.Flight.create(
            {
                "employee_id": self.emp.id,
                "ticket_price": 1000,
                "extra_charges": 50,
                "departure_date": date(2026, 1, 10),
            }
        )
        self.assertNotEqual(f.name, "New")
        self.assertEqual(f.total, 1050)
        self.assertEqual(f.month, "January")

    def test_currency_default_aed(self):
        f = self.Flight.create({"employee_id": self.emp.id})
        self.assertEqual(f.currency_id, self.env.ref("base.AED"))

    def test_book_creates_expense(self):
        f = self.Flight.create(
            {
                "employee_id": self.emp.id,
                "ticket_price": 500,
                "departure_date": date(2026, 3, 1),
            }
        )
        f.action_book()
        self.assertEqual(f.booking_state, "booked")
        self.assertTrue(f.expense_id)
        self.assertEqual(f.expense_id.employee_id, self.emp)

    def test_cancel_clears_draft_expense(self):
        f = self.Flight.create(
            {
                "employee_id": self.emp.id,
                "ticket_price": 700,
                "departure_date": date(2026, 5, 1),
            }
        )
        f.action_book()
        f.action_cancel()
        self.assertEqual(f.booking_state, "cancelled")

    def test_employee_change_syncs_project(self):
        analytic = self.env["account.analytic.account"].create(
            {
                "name": "Project A",
                "plan_id": self.env.ref(
                    "hr_uae_master_data.account_analytic_plan_project_allocation"
                ).id,
            }
        )
        self.emp.project_allocation_id = analytic
        f = self.Flight.new({"employee_id": self.emp.id})
        f._onchange_employee()
        self.assertEqual(f.project_allocation_id, analytic)
