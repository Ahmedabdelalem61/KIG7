from datetime import timedelta

from lxml import etree

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.hr_uae_project_department.hooks import (
    apply_project_department_migration,
)


@tagged("post_install", "-at_install")
class TestHrUaeProjectDepartment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Department = cls.env["hr.department"]
        cls.Analytic = cls.env["account.analytic.account"]
        cls.plan = cls.env.ref(
            "hr_uae_master_data.account_analytic_plan_project_allocation"
        )

    def _analytic(self, name):
        return self.Analytic.create({"name": name, "plan_id": self.plan.id})

    def _legacy_employee_allocation(self, employee, analytic):
        self.env.cr.execute(
            "UPDATE hr_employee SET project_allocation_id = %s WHERE id = %s",
            (analytic.id, employee.id),
        )
        self.env.invalidate_all()

    def test_migration_maps_employee_allocation_to_empty_department(self):
        analytic = self._analytic("PD Legacy Allocation")
        department = self.Department.create({"name": "PD Legacy Project"})
        employee = self.Employee.create(
            {"name": "PD Legacy Employee", "department_id": department.id}
        )
        self._legacy_employee_allocation(employee, analytic)

        apply_project_department_migration(self.env)

        self.assertEqual(department.project_allocation_id, analytic)
        self.assertEqual(employee.project_allocation_id, analytic)

    def test_migration_creates_project_for_allocated_employee_without_department(self):
        analytic = self._analytic("PD No Department Allocation")
        employee = self.Employee.create({"name": "PD No Department Employee"})
        self._legacy_employee_allocation(employee, analytic)

        apply_project_department_migration(self.env)

        self.assertTrue(employee.department_id)
        self.assertEqual(employee.department_id.project_allocation_id, analytic)
        self.assertEqual(employee.project_allocation_id, analytic)

    def test_migration_does_not_overwrite_existing_project_cost_center(self):
        existing = self._analytic("PD Existing Cost Center")
        legacy = self._analytic("PD Legacy Should Not Overwrite")
        department = self.Department.create(
            {"name": "PD Protected Project", "project_allocation_id": existing.id}
        )
        employee = self.Employee.create(
            {"name": "PD Protected Employee", "department_id": department.id}
        )
        self._legacy_employee_allocation(employee, legacy)

        apply_project_department_migration(self.env)

        self.assertEqual(department.project_allocation_id, existing)
        self.assertEqual(employee.project_allocation_id, existing)

    def test_employee_allocation_follows_employee_project(self):
        allocation_a = self._analytic("PD Runtime A")
        allocation_b = self._analytic("PD Runtime B")
        project_a = self.Department.create(
            {"name": "PD Runtime Project A", "project_allocation_id": allocation_a.id}
        )
        project_b = self.Department.create(
            {"name": "PD Runtime Project B", "project_allocation_id": allocation_b.id}
        )
        employee = self.Employee.create(
            {"name": "PD Runtime Employee", "department_id": project_a.id}
        )

        self.assertEqual(employee.project_allocation_id, allocation_a)

        employee.write({"department_id": project_b.id})
        self.assertEqual(employee.project_allocation_id, allocation_b)

        employee.write({"project_allocation_id": allocation_a.id})
        self.assertEqual(project_b.project_allocation_id, allocation_a)
        self.assertEqual(employee.project_allocation_id, allocation_a)

    def test_flight_keeps_analytic_cost_center_for_expenses(self):
        analytic = self._analytic("PD Flight Cost Center")
        project = self.Department.create(
            {"name": "PD Flight Project", "project_allocation_id": analytic.id}
        )
        employee = self.Employee.create(
            {"name": "PD Flight Employee", "department_id": project.id}
        )
        flight = self.env["hr.uae.flight"].create(
            {
                "employee_id": employee.id,
                "ticket_price": 500,
                "departure_date": fields.Date.context_today(self.env["hr.uae.flight"]),
            }
        )

        self.assertEqual(flight.department_id, project)
        self.assertEqual(flight.project_allocation_id, analytic)

        flight.action_book()

        self.assertEqual(
            flight.expense_id.analytic_distribution,
            {str(analytic.id): 100.0},
        )

    def test_key_search_views_group_by_project_department(self):
        expected_views = [
            "hr.view_employee_filter",
            "hr_uae_flights.view_hr_uae_flight_search",
            "hr_uae_documents.view_hr_uae_document_search",
            "hr_uae_salary_adjustment.view_hr_uae_salary_adjustment_search",
            "hr_uae_leaves.view_hr_uae_movement_tracking_search",
            "hr_uae_payroll.view_hr_uae_payroll_dashboard_search",
            "hr_uae_project_department.view_hr_uae_termination_search_project",
        ]
        for xmlid in expected_views:
            arch = self.env.ref(xmlid).get_combined_arch()
            self.assertIn("department_id", arch, xmlid)

        self.assertIn(
            "'group_by': 'department_id'",
            self.env.ref("hr_uae_flights.view_hr_uae_flight_search").get_combined_arch(),
        )
        self.assertIn(
            "'group_by': 'department_id'",
            self.env.ref(
                "hr_uae_payroll.view_hr_uae_payroll_dashboard_search"
            ).get_combined_arch(),
        )

    def test_projects_menu_is_after_employee_menu(self):
        employee_menu = self.env.ref("hr_uae_base.menu_hr_uae_employees")
        project_menu = self.env.ref("hr_uae_project_department.menu_hr_uae_projects")

        self.assertEqual(project_menu.parent_id, employee_menu.parent_id)
        self.assertEqual(project_menu.sequence, employee_menu.sequence + 5)
        self.assertEqual(project_menu.action.res_model, "hr.department")

    def test_employee_project_field_is_in_master_data_tab(self):
        arch = self.env.ref("hr.view_employee_form").get_combined_arch()
        root = etree.fromstring(arch.encode())

        master_project_fields = root.xpath(
            "//page[@name='hr_uae_master_data']//field[@name='department_id']"
        )
        top_project_fields = root.xpath("//sheet/group/group/field[@name='department_id']")

        self.assertTrue(master_project_fields)
        self.assertEqual(master_project_fields[0].get("string"), "Project")
        self.assertTrue(top_project_fields)
        self.assertEqual(top_project_fields[0].get("invisible"), "1")

    def test_hr_live_dashboard_groups_headcount_by_project(self):
        project = self.Department.create({"name": "PD Dashboard Project"})
        for idx in range(9):
            self.Employee.create(
                {"name": "PD Dashboard Employee %s" % idx, "department_id": project.id}
            )

        data = self.env["hr.uae.dashboard"].fetch_dashboard_data()

        self.assertIn(
            "PD Dashboard Project",
            [row["label"] for row in data["per_project"]],
        )

    def test_payroll_live_dashboard_uses_department_domain_ids(self):
        analytic = self._analytic("PD Payroll Cost Center")
        project = self.Department.create(
            {"name": "PD Payroll Project", "project_allocation_id": analytic.id}
        )
        employee = self.Employee.create(
            {"name": "PD Payroll Employee", "department_id": project.id}
        )
        today = fields.Date.context_today(self.env["hr.payslip"])
        date_from = today.replace(day=1)
        contract = self.env["hr.contract"].create(
            {
                "name": "PD Payroll Contract",
                "employee_id": employee.id,
                "wage": 99999,
                "date_start": date_from - timedelta(days=30),
                "state": "open",
                "struct_id": self.env.ref(
                    "hr_uae_payroll.hr_payroll_structure_uae"
                ).id,
            }
        )
        employee.contract_id = contract
        self.env["hr.payslip"].create(
            {
                "employee_id": employee.id,
                "contract_id": contract.id,
                "struct_id": contract.struct_id.id,
                "date_from": date_from,
                "date_to": date_from + timedelta(days=27),
            }
        )

        data = self.env["hr.uae.payroll.live.dashboard"].fetch_data(
            {"months_back": 36}
        )
        project_rows = [
            row for row in data["net_by_project"] if row["project_id"] == project.id
        ]

        self.assertTrue(project_rows)
        self.assertEqual(project_rows[0]["label"], "PD Payroll Project")
