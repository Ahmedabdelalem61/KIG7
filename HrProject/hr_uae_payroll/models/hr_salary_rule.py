from odoo import api, models


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    @api.model
    def _hr_uae_ensure_rule(self, xml_name, vals):
        xmlid = "hr_uae_payroll.%s" % xml_name
        rule = self.env.ref(xmlid, raise_if_not_found=False)
        if rule:
            rule.write(vals)
            return rule
        rule = self.create(vals)
        module, name = xmlid.split(".")
        self.env["ir.model.data"].sudo().create(
            {
                "module": module,
                "name": name,
                "model": self._name,
                "res_id": rule.id,
                "noupdate": True,
            }
        )
        return rule

    @api.model
    def _hr_uae_sync_contract_allowance_rules(self):
        basic = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_category_basic", raise_if_not_found=False
        )
        allowance = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_category_alw", raise_if_not_found=False
        )
        deduction = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_category_ded", raise_if_not_found=False
        )
        net = self.env.ref(
            "hr_uae_payroll.hr_salary_rule_category_net", raise_if_not_found=False
        )
        structure = self.env.ref(
            "hr_uae_payroll.hr_payroll_structure_uae", raise_if_not_found=False
        )

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
        if other_rule:
            other_rule.write(
                {
                    "category_id": allowance.id if allowance else other_rule.category_id.id,
                    "condition_select": "none",
                    "amount_select": "code",
                    "amount_python_compute": (
                        "result = contract.other_allowances or 0.0"
                    ),
                }
            )

        synced_rules = self.browse()
        for rule in (housing_rule, transport_rule, other_rule):
            if rule:
                synced_rules |= rule
        if basic:
            synced_rules |= self._hr_uae_ensure_rule(
                "hr_salary_rule_basic",
                {
                    "name": "Basic",
                    "code": "BASIC",
                    "sequence": 1,
                    "category_id": basic.id,
                    "condition_select": "none",
                    "amount_select": "code",
                    "amount_python_compute": "result = contract.wage",
                },
            )
        if deduction:
            synced_rules |= self._hr_uae_ensure_rule(
                "hr_salary_rule_unpaid_leave",
                {
                    "name": "Unpaid Leave Deduction",
                    "code": "UNPAID",
                    "sequence": 50,
                    "category_id": deduction.id,
                    "condition_select": "python",
                    "condition_python": "result = bool(worked_days.UNPAID)",
                    "amount_select": "code",
                    "amount_python_compute": (
                        "unpaid = worked_days.UNPAID\n"
                        "days = abs(unpaid.number_of_days or 0.0) if unpaid else 0.0\n"
                        "result = -((contract.wage / 30.0) * days) if days else 0.0"
                    ),
                },
            )
            synced_rules |= self._hr_uae_ensure_rule(
                "hr_salary_rule_flight_ded",
                {
                    "name": "Flight Ticket Deduction",
                    "code": "FLIGHT_DED",
                    "sequence": 55,
                    "category_id": deduction.id,
                    "condition_select": "python",
                    "condition_python": "result = bool(inputs.FLIGHT_DED)",
                    "amount_select": "code",
                    "amount_python_compute": (
                        "flight = inputs.FLIGHT_DED\n"
                        "result = -(flight.amount if flight else 0.0)"
                    ),
                },
            )
            synced_rules |= self._hr_uae_ensure_rule(
                "hr_salary_rule_adjustment_deductions",
                {
                    "name": "Salary Adjustment Deduction",
                    "code": "ADJ_DED_LINE",
                    "sequence": 61,
                    "category_id": deduction.id,
                    "condition_select": "python",
                    "condition_python": "result = bool(inputs.ADJ_DED)",
                    "amount_select": "code",
                    "amount_python_compute": (
                        "adj_ded = inputs.ADJ_DED\n"
                        "result = -(adj_ded.amount if adj_ded else 0.0)"
                    ),
                },
            )
        if allowance:
            synced_rules |= self._hr_uae_ensure_rule(
                "hr_salary_rule_adjustments",
                {
                    "name": "Adjustments / Allowances",
                    "code": "ADJUSTMENTS",
                    "sequence": 60,
                    "category_id": allowance.id,
                    "condition_select": "python",
                    "condition_python": "result = bool(inputs.ADJ_ALW or inputs.ADJ_ADJ)",
                    "amount_select": "code",
                    "amount_python_compute": (
                        "adj_alw = inputs.ADJ_ALW\n"
                        "adj_adj = inputs.ADJ_ADJ\n"
                        "allowances = adj_alw.amount if adj_alw else 0.0\n"
                        "adjustments = adj_adj.amount if adj_adj else 0.0\n"
                        "result = allowances + adjustments"
                    ),
                },
            )
        if net:
            synced_rules |= self._hr_uae_ensure_rule(
                "hr_salary_rule_net",
                {
                    "name": "Net Salary",
                    "code": "NET",
                    "sequence": 200,
                    "category_id": net.id,
                    "condition_select": "none",
                    "amount_select": "code",
                    "amount_python_compute": (
                        "result = categories.BASIC + categories.ALW + categories.DED"
                    ),
                },
            )
        if structure and synced_rules:
            for rule in synced_rules:
                if rule not in structure.rule_ids:
                    structure.write({"rule_ids": [(4, rule.id)]})
        return True
