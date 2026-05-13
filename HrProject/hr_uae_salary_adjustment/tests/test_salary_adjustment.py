from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestHrUaeSalaryAdjustment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Adj = cls.env["hr.uae.salary.adjustment"]
        cls.Employee = cls.env["hr.employee"]
        cls.Payslip = cls.env["hr.payslip"]
        cls.struct = cls.env.ref("hr_uae_payroll.hr_payroll_structure_uae")
        cls.emp = cls.Employee.create({"name": "Adj Test"})
        cls.contract = cls.env["hr.contract"].create(
            {
                "name": "C-Adj",
                "employee_id": cls.emp.id,
                "wage": 5000,
                "date_start": date(2026, 1, 1),
                "state": "open",
                "struct_id": cls.struct.id,
            }
        )
        cls.emp.contract_id = cls.contract
        cls.slip = cls.Payslip.create(
            {
                "employee_id": cls.emp.id,
                "contract_id": cls.contract.id,
                "struct_id": cls.struct.id,
                "date_from": date(2026, 4, 1),
                "date_to": date(2026, 4, 30),
            }
        )
        manager = cls.env.ref("hr_uae_base.group_hr_uae_manager")
        manager.users |= cls.env.user

    def test_create_with_sequence(self):
        adj = self.Adj.create(
            {
                "employee_id": self.emp.id,
                "kind": "allowance",
                "amount": 200,
                "mode": "one_shot",
                "target_payslip_id": self.slip.id,
            }
        )
        self.assertNotEqual(adj.name, "New")

    def test_one_shot_workflow_pushes_input(self):
        adj = self.Adj.create(
            {
                "employee_id": self.emp.id,
                "kind": "allowance",
                "amount": 250,
                "mode": "one_shot",
                "target_payslip_id": self.slip.id,
            }
        )
        adj.action_submit()
        self.assertEqual(adj.state, "to_approve")
        adj.action_approve()
        self.assertEqual(adj.state, "done")
        Input = self.env["hr.payslip.input"].sudo()
        inp = Input.search(
            [
                ("payslip_id", "=", self.slip.id),
                ("code", "=", "ADJ_ALW"),
                ("name", "=", adj.name),
            ],
            limit=1,
        )
        self.assertTrue(inp)
        self.assertEqual(inp.amount, 250)

    def test_one_shot_requires_target(self):
        adj = self.Adj.create(
            {
                "employee_id": self.emp.id,
                "kind": "deduction",
                "amount": 100,
                "mode": "one_shot",
            }
        )
        with self.assertRaises(UserError):
            adj.action_submit()

    def test_range_pushes_to_matching_payslips(self):
        adj = self.Adj.create(
            {
                "employee_id": self.emp.id,
                "kind": "deduction",
                "amount": 50,
                "mode": "range",
                "date_from": date(2026, 4, 1),
                "date_to": date(2026, 4, 30),
            }
        )
        adj.action_submit()
        adj.action_approve()
        Input = self.env["hr.payslip.input"].sudo()
        inp = Input.search(
            [("payslip_id", "=", self.slip.id), ("code", "=", "ADJ_DED")],
            limit=1,
        )
        self.assertTrue(inp)
        self.assertEqual(inp.amount, 50)
