from odoo import api, models


class HrUaeFlight(models.Model):
    _inherit = "hr.uae.flight"

    def _hr_uae_sync_payroll_inputs(self):
        employees = self.mapped("employee_id")
        if employees:
            self.env["hr.payslip"]._hr_uae_sync_flight_inputs_for_employees(employees)

    @api.model_create_multi
    def create(self, vals_list):
        flights = super().create(vals_list)
        flights._hr_uae_sync_payroll_inputs()
        return flights

    def write(self, vals):
        employees_before = self.mapped("employee_id")
        result = super().write(vals)
        employees = employees_before | self.mapped("employee_id")
        if employees:
            self.env["hr.payslip"]._hr_uae_sync_flight_inputs_for_employees(employees)
        return result

    def action_book(self):
        result = super().action_book()
        self._hr_uae_sync_payroll_inputs()
        return result

    def action_complete(self):
        result = super().action_complete()
        self._hr_uae_sync_payroll_inputs()
        return result

    def action_cancel(self):
        result = super().action_cancel()
        self._hr_uae_sync_payroll_inputs()
        return result

    def action_reschedule(self):
        result = super().action_reschedule()
        self._hr_uae_sync_payroll_inputs()
        return result

    def action_reset_to_draft(self):
        result = super().action_reset_to_draft()
        self._hr_uae_sync_payroll_inputs()
        return result
