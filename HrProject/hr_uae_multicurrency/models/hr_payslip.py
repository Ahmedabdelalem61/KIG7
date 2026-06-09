from odoo import fields, models


class HrUaeFxContract:
    """Lightweight proxy used during payslip rule evaluation.

    Salary rules read ``contract.wage`` / ``contract.housing_allowance`` … .
    For a foreign-denominated contract this proxy returns those amounts
    converted to the company currency at the payslip's period-end date, while
    delegating every other attribute to the real contract record. Doing the
    conversion here (in code) — rather than by rewriting the salary-rule
    expressions — keeps payroll correct regardless of module load order or
    later upgrades of the payroll module.
    """

    def __init__(self, contract, payslip):
        object.__setattr__(self, "_contract", contract)
        object.__setattr__(self, "_payslip", payslip)
        object.__setattr__(self, "_money_map", contract._hr_uae_money_map())

    def __getattr__(self, name):
        money_map = object.__getattribute__(self, "_money_map")
        contract = object.__getattribute__(self, "_contract")
        if name in money_map:
            payslip = object.__getattribute__(self, "_payslip")
            return payslip._hr_uae_company_amount(
                contract[money_map[name]], contract.contract_currency_id
            )
        return getattr(contract, name)

    def __getitem__(self, key):
        return getattr(self, key)


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _hr_uae_company_amount(self, amount, from_currency):
        """Convert a contract-currency amount to the company currency at this
        payslip's period-end date. Same currency -> identity."""
        self.ensure_one()
        company = self.company_id
        from_currency = from_currency or company.currency_id
        date = self.date_to or self.date_from or fields.Date.context_today(self)
        return from_currency._hr_uae_to_company(amount or 0.0, company, date)

    def _compute_payslip_line(self, rule, localdict, lines_dict):
        """Evaluate each salary rule with a contract proxy that exposes the
        company-currency (period-end converted) wage and allowances."""
        contract = localdict.get("contract")
        if contract is not None and not isinstance(contract, HrUaeFxContract):
            localdict = dict(localdict, contract=HrUaeFxContract(contract, self))
        return super()._compute_payslip_line(rule, localdict, lines_dict)

    def _hr_uae_flight_deduction_amount(self):
        """Override: convert each employee-paid flight ticket total from its own
        currency to the company currency at the deduction date before summing."""
        self.ensure_one()
        if (
            not self.employee_id
            or not self.employee_id.hr_uae_deduct_employee_paid_tickets
            or not self.date_from
            or not self.date_to
        ):
            return 0.0
        flights = self.env["hr.uae.flight"].sudo().search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("payment_mode", "=", "own_account"),
                ("booking_state", "in", ("booked", "completed")),
                ("total", ">", 0.0),
            ]
        )
        company = self.company_id
        amount = 0.0
        for flight in flights:
            deduction_date = self._hr_uae_flight_deduction_date(flight)
            if deduction_date and self.date_from <= deduction_date <= self.date_to:
                amount += flight.currency_id._hr_uae_to_company(
                    flight.total, company, deduction_date
                )
        return amount
