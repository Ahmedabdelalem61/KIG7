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
        cls.Allocation = cls.env["hr.leave.allocation"]
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

    def _allocate(self, emp, leave_type, days=30):
        allocation = self.Allocation.create(
            {
                "name": "Allocation %s" % emp.name,
                "employee_id": emp.id,
                "holiday_status_id": leave_type.id,
                "number_of_days": days,
                "date_from": date(2026, 1, 1),
                "date_to": date(2026, 12, 31),
                "state": "confirm",
            }
        )
        allocation.action_validate()
        return allocation

    def test_uae_structure_seeded(self):
        self.assertTrue(self.struct)
        self.assertEqual(self.struct.code, "UAE")
        self.assertGreater(len(self.struct.rule_ids), 4)

    def test_payslip_state_includes_on_hold(self):
        self.assertIn("on_hold", dict(self.Payslip._fields["state"].selection))

    def test_payslip_basic_net_from_lines(self):
        emp, contract = self._make_employee_with_contract("PR Basic Net", wage=3000)
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
        basic = slip.line_ids.filtered(lambda line: line.code == "BASIC")[:1]
        net = slip.line_ids.filtered(lambda line: line.code == "NET")[:1]
        self.assertEqual(slip.hr_uae_basic, basic.total)
        self.assertEqual(slip.hr_uae_net, net.total)

    def test_payslip_net_uses_payable_when_on_hold(self):
        emp, contract = self._make_employee_with_contract("PR Net Hold", wage=2800)
        annual = self.env.ref("hr_uae_leaves.leave_type_annual")
        self._allocate(emp, annual)
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
        self.assertEqual(slip.hr_uae_net, slip.hr_uae_payable_now)

    def test_contract_allowances_flow_into_monthly_payslip(self):
        emp, contract = self._make_employee_with_contract("PR Allowances", wage=3000)
        contract.write(
            {
                "housing_allowance": 1500,
                "transportation_allowance": 300,
                "other_allowances": 200,
            }
        )
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
        housing = slip.line_ids.filtered(lambda record: record.code == "HOUSING")
        transport = slip.line_ids.filtered(lambda record: record.code == "TRANSPORT")
        other = slip.line_ids.filtered(lambda record: record.code == "OTHER_ALW")
        net = slip.line_ids.filtered(lambda record: record.code == "NET")
        self.assertEqual(housing.total, 1500)
        self.assertEqual(transport.total, 300)
        self.assertEqual(other.total, 200)
        self.assertEqual(net.total, 5000)

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
        self._allocate(emp, annual)
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

    def test_special_and_unpaid_leave_do_not_hold_payroll(self):
        emp, contract = self._make_employee_with_contract("PR Annual Only", wage=3000)
        for leave_type, day in (
            (self.env.ref("hr_uae_leaves.leave_type_special"), 10),
            (self.env.ref("hr_uae_leaves.leave_type_unpaid"), 15),
        ):
            leave = self.Leave.create(
                {
                    "name": "No Hold",
                    "employee_id": emp.id,
                    "holiday_status_id": leave_type.id,
                    "request_date_from": date(2026, 2, day),
                    "request_date_to": date(2026, 2, day + 1),
                    "date_from": datetime(2026, 2, day, 0, 0),
                    "date_to": datetime(2026, 2, day + 1, 23, 59),
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
        self.assertFalse(slip.hr_uae_hold_active)
        self.assertNotEqual(slip.state, "on_hold")

    def test_unpaid_leave_creates_standalone_deduction(self):
        emp, contract = self._make_employee_with_contract("PR Unpaid", wage=3000)
        unpaid = self.env.ref("hr_uae_leaves.leave_type_unpaid")
        leave = self.Leave.create(
            {
                "name": "Unpaid",
                "employee_id": emp.id,
                "holiday_status_id": unpaid.id,
                "request_date_from": date(2026, 2, 10),
                "request_date_to": date(2026, 2, 11),
                "date_from": datetime(2026, 2, 10, 0, 0),
                "date_to": datetime(2026, 2, 11, 23, 59),
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
        unpaid_worked_days = slip.worked_days_line_ids.filtered(
            lambda line: line.code == "UNPAID"
        )
        unpaid_line = slip.line_ids.filtered(lambda line: line.code == "UNPAID")
        net = slip.line_ids.filtered(lambda line: line.code == "NET")
        self.assertFalse(slip.hr_uae_hold_active)
        self.assertEqual(unpaid_worked_days.number_of_days, 2.0)
        self.assertAlmostEqual(unpaid_line.total, -200.0)
        self.assertAlmostEqual(net.total, 2800.0)

    def test_employee_paid_flights_deduct_only_when_employee_flag_enabled(self):
        emp, contract = self._make_employee_with_contract("PR Flight Ded", wage=3000)
        Flight = self.env["hr.uae.flight"]
        flight = Flight.create(
            {
                "employee_id": emp.id,
                "payment_mode": "own_account",
                "ticket_price": 500,
                "extra_charges": 50,
                "departure_date": date(2026, 3, 10),
            }
        )
        company_paid = Flight.create(
            {
                "employee_id": emp.id,
                "payment_mode": "company_account",
                "ticket_price": 900,
                "departure_date": date(2026, 3, 12),
            }
        )
        flight.action_book()
        company_paid.action_book()
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
        self.assertFalse(slip.line_ids.filtered(lambda line: line.code == "FLIGHT_DED"))
        self.assertEqual(slip.line_ids.filtered(lambda line: line.code == "NET").total, 3000)

        emp.hr_uae_deduct_employee_paid_tickets = True
        slip.compute_sheet()
        flight_line = slip.line_ids.filtered(lambda line: line.code == "FLIGHT_DED")
        net = slip.line_ids.filtered(lambda line: line.code == "NET")
        self.assertAlmostEqual(flight_line.total, -550.0)
        self.assertAlmostEqual(net.total, 2450.0)

    def test_marking_returned_releases_hold(self):
        emp, contract = self._make_employee_with_contract("PR Return", wage=3000)
        annual = self.env.ref("hr_uae_leaves.leave_type_annual")
        self._allocate(emp, annual)
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
