from odoo import fields, models


class HrUaeTermination(models.Model):
    _inherit = "hr.uae.termination"

    department_id = fields.Many2one(
        "hr.department",
        string="Project",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )


class HrUaeSalaryAdjustment(models.Model):
    _inherit = "hr.uae.salary.adjustment"

    department_id = fields.Many2one(
        "hr.department",
        string="Project",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )


class HrUaeDocument(models.Model):
    _inherit = "hr.uae.document"

    department_id = fields.Many2one(
        "hr.department",
        string="Project",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )


class HrLeave(models.Model):
    _inherit = "hr.leave"

    department_id = fields.Many2one("hr.department", string="Project")


class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    department_id = fields.Many2one("hr.department", string="Project")


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    department_id = fields.Many2one("hr.department", string="Project")
