from datetime import date, datetime

from odoo.tests.common import TransactionCase


class TestHrUaePayroll(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.Payslip = cls.env["hr.payslip"]
        cls.Leave = cls.env["hr.leave"]
        cls.struct = cls.env.ref("hr_uae_payroll.hr_payroll_structure_uae")

    def _make_employee_with_contract(self, name, wage=3000):
        emp = self.Employee.create({"name": name})
        contract = self.Contract.create(
            {
                "name": "Contract %s" % name,
                "employee_id": emp.id,
                "wage": wage,
                "date_start": date(2026, 1, 1),
                "state": "open",
                "struct_id": self.struct.id,
            }
        )
        emp.contract_id = contract
        return emp, contract

    def test_uae_structure_seeded(self):
        self.assertTrue(self.struct)
        self.assertEqual(self.struct.code, "UAE")
        self.assertGreater(len(self.struct.rule_ids), 4)

    def test_payslip_state_includes_on_hold(self):
        self.assertIn("on_hold", dict(self.Payslip._fields["state"].selection))

    def test_compute_sheet_no_leave_no_hold(self):
        emp, contract = self._make_employee_with_contract("PR No Hold")
        slip = self.Payslip.create(
            {
                "employee_id": emp.id,
                "contract_id": contract.id,
                "struct_id": self.struct.id,
                "date_from": date(2026, 2, 1),
                "date_to": date(2026, 2, 28),
            }
        )
        slip.compute_sheet()
        self.assertFalse(slip.hr_uae_hold_active)
        self.assertEqual(slip.hr_uae_held_amount, 0.0)

    def test_compute_sheet_with_overlapping_vacation_holds(self):
        emp, contract = self._make_employee_with_contract("PR Hold", wage=2800)
        annual = self.env.ref("hr_uae_leaves.leave_type_annual")
        leave = self.Leave.create(
            {
                "name": "Vac",
                "employee_id": emp.id,
                "holiday_status_id": annual.id,
                "request_date_from": date(2026, 2, 10),
                "request_date_to": date(2026, 2, 28),
                "date_from": datetime(2026, 2, 10, 0, 0),
                "date_to": datetime(2026, 2, 28, 23, 59),
            }
        )
        leave.action_validate()
        slip = self.Payslip.create(
            {
                "employee_id": emp.id,
                "contract_id": contract.id,
                "struct_id": self.struct.id,
                "date_from": date(2026, 2, 1),
                "date_to": date(2026, 2, 28),
            }
        )
        slip.compute_sheet()
        self.assertTrue(slip.hr_uae_hold_active)
        self.assertEqual(slip.state, "on_hold")
        self.assertGreater(slip.hr_uae_held_amount, 0.0)
        self.assertGreater(slip.hr_uae_payable_now, 0.0)

    def test_marking_returned_releases_hold(self):
        emp, contract = self._make_employee_with_contract("PR Return", wage=3000)
        annual = self.env.ref("hr_uae_leaves.leave_type_annual")
        leave = self.Leave.create(
            {
                "name": "Vac2",
                "employee_id": emp.id,
                "holiday_status_id": annual.id,
                "request_date_from": date(2026, 3, 5),
                "request_date_to": date(2026, 3, 25),
                "date_from": datetime(2026, 3, 5, 0, 0),
                "date_to": datetime(2026, 3, 25, 23, 59),
            }
        )
        leave.action_validate()
        slip = self.Payslip.create(
            {
                "employee_id": emp.id,
                "contract_id": contract.id,
                "struct_id": self.struct.id,
                "date_from": date(2026, 3, 1),
                "date_to": date(2026, 3, 31),
            }
        )
        slip.compute_sheet()
        self.assertEqual(slip.state, "on_hold")
        leave.hr_uae_returned = True
        self.assertEqual(slip.state, "verify")
        self.assertEqual(slip.hr_uae_held_amount, 0.0)
