from odoo import api, models


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    @api.model
    def _hr_uae_sync_contract_allowance_rules(self):
        housing_rule = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_housing", raise_if_not_found=False
        )
        transport_rule = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_transport", raise_if_not_found=False
        )
        other_rule = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_other_allowances",
            raise_if_not_found=False,
        )
        structure = self.env.ref(
            "hr_uae_payroll.hr_payroll_structure_uae", raise_if_not_found=False
        )

        if housing_rule:
            housing_rule.write(
                {
                    "amount_select": "code",
                    "amount_python_compute": (
                        "result = contract.housing_allowance or 0.0"
                    ),
                }
            )
        if transport_rule:
            transport_rule.write(
                {
                    "amount_select": "code",
                    "amount_python_compute": (
                        "result = contract.transportation_allowance or 0.0"
                    ),
                }
            )
        if other_rule and structure and other_rule not in structure.rule_ids:
            structure.write({"rule_ids": [(4, other_rule.id)]})
