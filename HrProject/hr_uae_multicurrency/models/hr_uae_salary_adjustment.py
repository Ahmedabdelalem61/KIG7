from odoo import fields, models


class HrUaeSalaryAdjustment(models.Model):
    _inherit = "hr.uae.salary.adjustment"

    def _apply_to_payslips(self):
        """Override: push the adjustment to payslip inputs in the COMPANY
        currency, converting the adjustment amount from its own currency at the
        target payslip's period-end date."""
        Input = self.env["hr.payslip.input"].sudo()
        for rec in self:
            payslips = rec._matching_payslips()
            if not payslips:
                continue
            for slip in payslips:
                amount_company = rec.currency_id._hr_uae_to_company(
                    rec.amount,
                    slip.company_id,
                    slip.date_to or fields.Date.context_today(rec),
                )
                existing = Input.search(
                    [
                        ("payslip_id", "=", slip.id),
                        ("code", "=", rec._input_code()),
                        ("name", "=", rec.name),
                    ],
                    limit=1,
                )
                vals = {
                    "name": rec.name,
                    "code": rec._input_code(),
                    "amount": amount_company,
                    "payslip_id": slip.id,
                    "contract_id": slip.contract_id.id,
                }
                if existing:
                    existing.write(vals)
                else:
                    Input.create(vals)
            rec.last_applied_period = fields.Date.context_today(rec)
            # Range / recurring stay 'approved' for the cron; one-shot completes.
            if rec.mode == "one_shot":
                rec.state = "done"
