from datetime import date

from odoo.tests.common import TransactionCase


class TestHrUaeTermination(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Term = cls.env["hr.uae.termination"]
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["hr.payslip"]
        cls.struct = cls.env.ref("hr_uae_payroll.hr_payroll_structure_uae")
        cls.emp = cls.Employee.create({"name": "Term Test"})
        cls.contract = cls.Contract.create(
            {
                "name": "Contract Term",
                "employee_id": cls.emp.id,
                "wage": 4000,
                "date_start": date(2026, 1, 1),
                "state": "open",
                "struct_id": cls.struct.id,
            }
        )
        cls.emp.contract_id = cls.contract

    def test_create_with_sequence(self):
        t = self.Term.create(
            {
                "employee_id": self.emp.id,
                "contract_id": self.contract.id,
                "departure_date": date(2026, 6, 1),
            }
        )
        self.assertNotEqual(t.name, "New")

    def test_activate_archives_and_cancels_payslips(self):
        slip = self.Payslip.create(
            {
                "employee_id": self.emp.id,
                "contract_id": self.contract.id,
                "struct_id": self.struct.id,
                "date_from": date(2026, 6, 1),
                "date_to": date(2026, 6, 30),
            }
        )
        t = self.Term.create(
            {
                "employee_id": self.emp.id,
                "contract_id": self.contract.id,
                "departure_date": date(2026, 6, 5),
                "reason": "resignation",
            }
        )
        t.action_activate()
        self.assertEqual(t.state, "active")
        self.contract.invalidate_recordset(["state"])
        self.assertEqual(self.contract.state, "close")
        slip.invalidate_recordset(["state"])
        self.assertEqual(slip.state, "cancel")
        self.emp.invalidate_recordset(["active", "hr_uae_status"])
        self.assertFalse(self.emp.active)
        self.assertEqual(self.emp.hr_uae_status, "terminated")

    def test_close_after_active(self):
        t = self.Term.create(
            {"employee_id": self.emp.id, "contract_id": self.contract.id}
        )
        t.action_activate()
        t.action_close()
        self.assertEqual(t.state, "closed")
