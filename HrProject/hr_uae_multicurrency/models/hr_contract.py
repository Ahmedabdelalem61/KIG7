from odoo import api, fields, models

_FOREIGN_SUFFIX = "_foreign"
_OPTIONAL_MONEY_FIELDS = (
    "housing_allowance",
    "transportation_allowance",
    "other_allowances",
    "annual_ticket_amount",
)


class HrContract(models.Model):
    _inherit = "hr.contract"

    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    contract_currency_id = fields.Many2one(
        "res.currency",
        string="Contract Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
        help="Currency the contract is denominated in. Payroll converts the "
        "amounts to the company currency at each payslip's period-end rate.",
    )
    wage_foreign = fields.Monetary(
        string="Wage (Contract Currency)",
        currency_field="contract_currency_id",
        help="Monthly wage in the contract currency. This is the value payroll "
        "converts at the payslip period-end rate.",
    )
    housing_allowance_foreign = fields.Monetary(
        string="Housing Allowance (Contract Currency)",
        currency_field="contract_currency_id",
    )
    transportation_allowance_foreign = fields.Monetary(
        string="Transportation Allowance (Contract Currency)",
        currency_field="contract_currency_id",
    )
    other_allowances_foreign = fields.Monetary(
        string="Other Allowances (Contract Currency)",
        currency_field="contract_currency_id",
    )
    annual_ticket_amount_foreign = fields.Monetary(
        string="Annual Ticket Amount (Contract Currency)",
        currency_field="contract_currency_id",
    )

    # ------------------------------------------------------------------ helpers

    @api.model
    def _hr_uae_money_map(self):
        """company-currency field -> contract-currency (foreign) field."""
        mapping = {"wage": "wage" + _FOREIGN_SUFFIX}
        for fname in _OPTIONAL_MONEY_FIELDS:
            if fname in self._fields:
                mapping[fname] = fname + _FOREIGN_SUFFIX
        return mapping

    def _hr_uae_currency_of(self, vals):
        cur_id = vals.get("contract_currency_id")
        if cur_id:
            return self.env["res.currency"].browse(cur_id)
        if self:
            return self.contract_currency_id or self.company_id.currency_id
        return self.env.company.currency_id

    def _hr_uae_company_of(self, vals):
        comp_id = vals.get("company_id")
        if comp_id:
            return self.env["res.company"].browse(comp_id)
        if self:
            return self.company_id or self.env.company
        return self.env.company

    def _hr_uae_apply_currency(self, vals):
        """Augment `vals` so the company-currency money fields and the foreign
        money fields stay consistent.

        - Company mode (contract currency == company currency): the AED fields
          are authoritative; foreign mirrors them (so payroll, which reads the
          foreign fields, sees the same number).
        - Foreign mode: the foreign fields are authoritative; the AED fields are
          derived at today's rate (display/reporting only — payroll reconverts
          at the payslip date). On a currency *change* without a new foreign
          amount, the foreign field is seeded from the prior AED value so the
          real worth is preserved (prevents accidental over/under-pay).
        """
        vals = dict(vals)
        company = self._hr_uae_company_of(vals)
        company_cur = company.currency_id
        ccur = self._hr_uae_currency_of(vals)
        today = fields.Date.context_today(self)
        money_map = self._hr_uae_money_map()
        foreign_mode = bool(ccur) and ccur != company_cur
        currency_changed = "contract_currency_id" in vals and (
            not self or vals["contract_currency_id"] != self.contract_currency_id.id
        )
        for cf, ff in money_map.items():
            if foreign_mode:
                if currency_changed and ff not in vals and self:
                    vals[ff] = ccur._hr_uae_from_company(self[cf], company, today)
                foreign_val = vals.get(ff, self[ff] if self else 0.0)
                vals[cf] = ccur._hr_uae_to_company(
                    foreign_val, company, today, raise_if_missing=False
                )
            else:
                company_val = vals.get(cf, self[cf] if self else 0.0)
                vals[ff] = company_val
        return vals

    # ------------------------------------------------------------------ ORM

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [
            self._hr_uae_apply_currency(vals) for vals in vals_list
        ]
        return super().create(vals_list)

    def write(self, vals):
        money_map = self._hr_uae_money_map()
        triggers = (
            {"contract_currency_id", "company_id"}
            | set(money_map)
            | set(money_map.values())
        )
        if not (set(vals) & triggers):
            return super().write(vals)
        for rec in self:
            super(HrContract, rec).write(rec._hr_uae_apply_currency(vals))
        return True

    # ------------------------------------------------------------------ onchange

    @api.onchange("contract_currency_id")
    def _onchange_hr_uae_currency(self):
        """Switching currency seeds the entry fields, preserving real worth:
        to a foreign currency, foreign := (AED value converted to it); back to
        company currency, foreign mirrors the AED value."""
        company = self.company_id or self.env.company
        company_cur = company.currency_id
        ccur = self.contract_currency_id
        today = fields.Date.context_today(self)
        if ccur and ccur != company_cur:
            for cf, ff in self._hr_uae_money_map().items():
                self[ff] = ccur._hr_uae_from_company(self[cf], company, today)
        else:
            for cf, ff in self._hr_uae_money_map().items():
                self[ff] = self[cf]

    @api.onchange(
        "wage",
        "housing_allowance",
        "transportation_allowance",
        "other_allowances",
        "annual_ticket_amount",
        "wage_foreign",
        "housing_allowance_foreign",
        "transportation_allowance_foreign",
        "other_allowances_foreign",
        "annual_ticket_amount_foreign",
    )
    def _onchange_hr_uae_money(self):
        """Keep AED and foreign in sync as amounts are edited. Foreign mode:
        AED := convert(foreign). Company mode: foreign mirrors AED."""
        company = self.company_id or self.env.company
        company_cur = company.currency_id
        ccur = self.contract_currency_id
        today = fields.Date.context_today(self)
        if ccur and ccur != company_cur:
            for cf, ff in self._hr_uae_money_map().items():
                self[cf] = ccur._hr_uae_to_company(
                    self[ff], company, today, raise_if_missing=False
                )
        else:
            for cf, ff in self._hr_uae_money_map().items():
                self[ff] = self[cf]

    # ------------------------------------------------------------------ cron

    @api.model
    def _hr_uae_cron_refresh_currency(self):
        """Daily refresh of the displayed company-currency amounts for foreign
        contracts at the current rate (payroll itself always reconverts at the
        payslip date). Skips contracts whose rate is not yet defined."""
        contracts = self.search([])
        today = fields.Date.context_today(self)
        refreshed = 0
        for contract in contracts:
            company = contract.company_id
            ccur = contract.contract_currency_id
            if not ccur or ccur == company.currency_id:
                continue
            if not ccur._hr_uae_has_rate(company, today):
                continue
            vals = {}
            for cf, ff in contract._hr_uae_money_map().items():
                vals[cf] = ccur._hr_uae_to_company(
                    contract[ff], company, today, raise_if_missing=False
                )
            contract.with_context(hr_uae_skip_audit=True).write(vals)
            refreshed += 1
        return refreshed
