from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def write(self, vals):
        result = super().write(vals)
        if "hr_uae_deduct_employee_paid_tickets" in vals:
            self.env["hr.payslip"]._hr_uae_sync_flight_inputs_for_employees(self)
        return result
