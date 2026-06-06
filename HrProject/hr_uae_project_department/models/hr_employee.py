from odoo import api, fields, models

from .hr_department import SYNC_CONTEXT_KEY


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_id = fields.Many2one("hr.department", string="Project")
    project_allocation_id = fields.Many2one(
        "account.analytic.account",
        string="Project Cost Center",
        readonly=True,
        domain=lambda self: self._project_allocation_domain(),
    )

    @api.model
    def _department_for_project_allocation(self, allocation, employee=None):
        Department = self.env["hr.department"].sudo()
        domain = [("project_allocation_id", "=", allocation.id)]
        if employee and employee.company_id:
            domain = ["|", ("company_id", "=", employee.company_id.id), ("company_id", "=", False)] + domain
        department = Department.search(domain, limit=1)
        if department:
            return department

        name = allocation.display_name or allocation.name or "Project"
        search_domain = [("name", "=", name)]
        if employee and employee.company_id:
            search_domain = ["|", ("company_id", "=", employee.company_id.id), ("company_id", "=", False)] + search_domain
        department = Department.search(search_domain, limit=1)
        vals = {"project_allocation_id": allocation.id}
        if employee and employee.company_id:
            vals["company_id"] = employee.company_id.id
        if department:
            if not department.project_allocation_id:
                department.with_context(**{SYNC_CONTEXT_KEY: True}).write(vals)
            return department

        vals["name"] = name
        return Department.with_context(**{SYNC_CONTEXT_KEY: True}).create(vals)

    def _sync_project_allocation_from_department(self):
        for employee in self:
            allocation = employee.department_id.project_allocation_id
            if employee.project_allocation_id != allocation:
                employee.with_context(**{SYNC_CONTEXT_KEY: True}).write(
                    {"project_allocation_id": allocation.id or False}
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            allocation_id = vals.get("project_allocation_id")
            if allocation_id and not vals.get("department_id"):
                allocation = self.env["account.analytic.account"].browse(allocation_id)
                vals["department_id"] = self._department_for_project_allocation(
                    allocation
                ).id
        employees = super().create(vals_list)
        if not self.env.context.get(SYNC_CONTEXT_KEY):
            for employee, vals in zip(employees, vals_list):
                explicit_allocation = vals.get("project_allocation_id")
                if explicit_allocation and employee.department_id:
                    employee.department_id.write(
                        {"project_allocation_id": explicit_allocation}
                    )
                elif employee.department_id:
                    employee._sync_project_allocation_from_department()
        return employees

    def write(self, vals):
        if self.env.context.get(SYNC_CONTEXT_KEY):
            return super().write(vals)

        allocation_id = vals.get("project_allocation_id")
        if allocation_id and "department_id" not in vals:
            for employee in self.filtered(lambda emp: not emp.department_id):
                allocation = self.env["account.analytic.account"].browse(allocation_id)
                employee.with_context(**{SYNC_CONTEXT_KEY: True}).write(
                    {
                        "department_id": self._department_for_project_allocation(
                            allocation, employee=employee
                        ).id
                    }
                )

        result = super().write(vals)

        if "project_allocation_id" in vals:
            for employee in self.filtered("department_id"):
                employee.department_id.write(
                    {"project_allocation_id": vals["project_allocation_id"] or False}
                )
        elif "department_id" in vals:
            self._sync_project_allocation_from_department()
        return result


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    department_id = fields.Many2one("hr.department", string="Project")


class HrContract(models.Model):
    _inherit = "hr.contract"

    department_id = fields.Many2one("hr.department", string="Project")


class HrJob(models.Model):
    _inherit = "hr.job"

    department_id = fields.Many2one("hr.department", string="Project")
