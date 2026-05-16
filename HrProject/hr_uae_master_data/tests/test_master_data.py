from datetime import date

from odoo.tests.common import TransactionCase


class TestHrUaeMasterData(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Contract = cls.env["hr.contract"]
        cls.cost_center_plan = cls.env.ref(
            "hr_uae_master_data.account_analytic_plan_cost_center"
        )
        cls.project_plan = cls.env.ref(
            "hr_uae_master_data.account_analytic_plan_project_allocation"
        )

    def test_analytic_plans_seeded(self):
        self.assertTrue(self.cost_center_plan)
        self.assertTrue(self.project_plan)
        self.assertNotEqual(self.cost_center_plan.id, self.project_plan.id)

    def test_employee_create_auto_cost_center(self):
        emp = self.Employee.create({"name": "Test UAE Employee"})
        self.assertTrue(emp.cost_center_id)
        self.assertEqual(emp.cost_center_id.name, "Test UAE Employee")
        self.assertEqual(emp.cost_center_id.plan_id, self.cost_center_plan)

    def test_employee_rename_syncs_cost_center(self):
        emp = self.Employee.create({"name": "Original"})
        cc = emp.cost_center_id
        emp.name = "Renamed"
        self.assertEqual(cc.name, "Renamed")

    def test_employee_archive_archives_cost_center(self):
        emp = self.Employee.create({"name": "ToArchive"})
        cc = emp.cost_center_id
        emp.active = False
        self.assertFalse(cc.active)

    def test_age_compute(self):
        emp = self.Employee.create(
            {"name": "Aged", "birthday": date(1990, 1, 1)}
        )
        self.assertGreaterEqual(emp.age, 30)

    def test_visa_status_compute(self):
        emp = self.Employee.create(
            {"name": "VisaActive", "visa_expire": date(2099, 1, 1)}
        )
        self.assertEqual(emp.visa_status, "active")
        emp.write({"visa_expire": False})
        emp._compute_visa_status()
        self.assertEqual(emp.visa_status, "none")

    def test_default_status_active(self):
        emp = self.Employee.create({"name": "Active"})
        self.assertEqual(emp.hr_uae_status, "active")

    def test_status_terminated_when_archived(self):
        emp = self.Employee.create({"name": "ToTerminate"})
        emp.active = False
        emp.invalidate_recordset(["hr_uae_status"])
        emp._compute_hr_uae_status()
        self.assertEqual(emp.hr_uae_status, "terminated")

    def test_seed_ranks_and_positions(self):
        self.assertTrue(self.env.ref("hr_uae_master_data.rank_civilian"))
        self.assertTrue(self.env.ref("hr_uae_master_data.position_driver"))

    def test_contract_benefit_fields_are_stored(self):
        emp = self.Employee.create({"name": "Contract Benefit"})
        contract = self.Contract.create(
            {
                "name": "Benefit Contract",
                "employee_id": emp.id,
                "wage": 3500,
                "housing_allowance": 1500,
                "transportation_allowance": 300,
                "other_allowances": 200,
                "annual_ticket_amount": 1200,
            }
        )
        emp.contract_id = contract
        contract.flush_recordset(
            [
                "housing_allowance",
                "transportation_allowance",
                "other_allowances",
                "annual_ticket_amount",
            ]
        )
        contract.invalidate_recordset(
            [
                "housing_allowance",
                "transportation_allowance",
                "other_allowances",
                "annual_ticket_amount",
            ]
        )
        emp.invalidate_recordset(
            [
                "housing_allowance",
                "transportation_allowance",
                "other_allowances",
                "annual_ticket_amount",
            ]
        )
        self.assertEqual(contract.housing_allowance, 1500)
        self.assertEqual(contract.transportation_allowance, 300)
        self.assertEqual(contract.other_allowances, 200)
        self.assertEqual(contract.annual_ticket_amount, 1200)
        self.assertEqual(emp.housing_allowance, 1500)
        self.assertEqual(emp.transportation_allowance, 300)
        self.assertEqual(emp.other_allowances, 200)
        self.assertEqual(emp.annual_ticket_amount, 1200)
