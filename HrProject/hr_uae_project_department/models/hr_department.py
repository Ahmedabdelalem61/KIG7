from odoo import api, fields, models


SYNC_CONTEXT_KEY = "hr_uae_project_department_skip_sync"


class HrDepartment(models.Model):
    _inherit = "hr.department"

    name = fields.Char(string="Project")
    parent_id = fields.Many2one("hr.department", string="Parent Project")
    child_ids = fields.One2many(
        "hr.department",
        "parent_id",
        string="Child Projects",
    )
    project_allocation_id = fields.Many2one(
        "account.analytic.account",
        string="Project Cost Center",
        domain=lambda self: self._project_allocation_domain(),
        tracking=True,
    )

    @api.model
    def _project_allocation_domain(self):
        Employee = self.env["hr.employee"]
        if hasattr(Employee, "_project_allocation_domain"):
            return Employee._project_allocation_domain()
        return []

    def write(self, vals):
        result = super().write(vals)
        if (
            "project_allocation_id" in vals
            and not self.env.context.get(SYNC_CONTEXT_KEY)
        ):
            for department in self:
                department.member_ids.with_context(**{SYNC_CONTEXT_KEY: True}).write(
                    {
                        "project_allocation_id": department.project_allocation_id.id
                        or False
                    }
                )
        return result
