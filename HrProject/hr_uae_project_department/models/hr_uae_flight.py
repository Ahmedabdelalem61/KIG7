from odoo import api, fields, models


class HrUaeFlight(models.Model):
    _inherit = "hr.uae.flight"

    department_id = fields.Many2one(
        "hr.department",
        string="Project",
        tracking=True,
        ondelete="restrict",
    )

    @api.onchange("employee_id")
    def _onchange_employee(self):
        result = super()._onchange_employee()
        if self.employee_id:
            self.department_id = self.employee_id.department_id
        return result

    @api.model_create_multi
    def create(self, vals_list):
        Employee = self.env["hr.employee"].sudo()
        for vals in vals_list:
            employee_id = vals.get("employee_id")
            if not employee_id:
                continue
            employee = Employee.browse(employee_id)
            vals.setdefault("department_id", employee.department_id.id or False)
            vals.setdefault(
                "project_allocation_id", employee.project_allocation_id.id or False
            )
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("employee_id"):
            employee = self.env["hr.employee"].sudo().browse(vals["employee_id"])
            vals = dict(vals)
            vals.setdefault("department_id", employee.department_id.id or False)
            vals.setdefault(
                "project_allocation_id", employee.project_allocation_id.id or False
            )
        return super().write(vals)
