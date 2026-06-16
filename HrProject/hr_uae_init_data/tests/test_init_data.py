"""Install-time correctness: the data-driven master config is created."""
# pylint: disable=duplicate-code
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "hr_uae_init_data")
class TestInitData(TransactionCase):
    """Assert the manually-created master data is reproduced from code."""

    def test_company_name(self):
        """The main company is named Kig7."""
        self.assertEqual(self.env.ref("base.main_company").name, "Kig7")

    def test_departments_present(self):
        """The implementor's departments exist with the exact names."""
        self.assertEqual(
            self.env.ref("hr.dep_administration").name, "ABC Project"
        )
        self.assertEqual(
            self.env.ref("hr_uae_init_data.dep_finance").name, "Finance"
        )
        self.assertEqual(
            self.env.ref("hr_uae_init_data.dep_prj_a").name, "[PRJ-A] Project"
        )
        self.assertEqual(
            self.env.ref("hr_uae_init_data.dep_prj_b").name, "[PRJ-B] Project"
        )

    def test_company_category(self):
        """The custom 'Company' rule category exists."""
        cat = self.env.ref("hr_uae_init_data.hr_salary_rule_category_company")
        self.assertEqual(cat.name, "Company")

    def test_provision_rules(self):
        """The 4 provision/pension rules exist, categorised, and attached to
        the UAE structure."""
        rules = {
            "TICPR": "hr_uae_init_data.hr_salary_rule_ticket_provision",
            "EOSPRo": "hr_uae_init_data.hr_salary_rule_eos_provision",
            "PEN_EE": "hr_uae_init_data.hr_salary_rule_pension_employee",
            "PEN_ER": "hr_uae_init_data.hr_salary_rule_pension_employer",
        }
        structure = self.env.ref("hr_uae_payroll.hr_payroll_structure_uae")
        company_cat = self.env.ref(
            "hr_uae_init_data.hr_salary_rule_category_company"
        )
        ded_cat = self.env.ref("hr_uae_payroll.hr_salary_rule_category_ded")
        for code, xmlid in rules.items():
            rule = self.env.ref(xmlid)
            self.assertEqual(rule.code, code)
            self.assertIn(
                rule, structure.rule_ids, f"{code} not on UAE structure"
            )
            self.assertEqual(rule.amount_select, "code")
        # category split: PEN_EE is a deduction, the other 3 are "Company"
        self.assertEqual(
            self.env.ref(rules["PEN_EE"]).category_id, ded_cat
        )
        for code in ("TICPR", "EOSPRo", "PEN_ER"):
            self.assertEqual(
                self.env.ref(rules[code]).category_id, company_cat
            )

    def test_ticket_provision_formula(self):
        """Ticket provision = annual ticket / 12 (formula preserved)."""
        rule = self.env.ref("hr_uae_init_data.hr_salary_rule_ticket_provision")
        self.assertIn("annual_ticket_amount/12", rule.amount_python_compute)
