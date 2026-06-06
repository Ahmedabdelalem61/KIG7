from odoo import api, fields, models


SYNC_CONTEXT_KEY = "hr_uae_project_department_skip_sync"


class HrDepartment(models.Model):
    _inherit = "hr.department"
    _rec_names_search = ["name", "complete_name", "code"]

    name = fields.Char(string="Project")
    code = fields.Char(string="Project Code", index=True, copy=False, tracking=True)
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

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique(company_id, code)",
            "Project code must be unique per company.",
        ),
    ]

    @api.depends_context("hierarchical_naming")
    @api.depends("code", "name", "complete_name")
    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            if record.code and record.display_name:
                record.display_name = "[%s] %s" % (record.code, record.display_name)

    @api.model
    def _project_allocation_domain(self):
        Employee = self.env["hr.employee"]
        if hasattr(Employee, "_project_allocation_domain"):
            return Employee._project_allocation_domain()
        return []

    @api.model
    def _code_from_allocation(self, allocation):
        if not allocation:
            return False
        return (allocation.code or "").strip() or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("project_allocation_id") and not vals.get("code"):
                allocation = self.env["account.analytic.account"].browse(
                    vals["project_allocation_id"]
                )
                code = self._code_from_allocation(allocation)
                if code:
                    vals["code"] = code
        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)
        if (
            "project_allocation_id" in vals
            and not self.env.context.get(SYNC_CONTEXT_KEY)
        ):
            for department in self:
                if (
                    department.project_allocation_id
                    and not department.code
                ):
                    code = self._code_from_allocation(department.project_allocation_id)
                    if code:
                        department.code = code
                department.member_ids.with_context(**{SYNC_CONTEXT_KEY: True}).write(
                    {
                        "project_allocation_id": department.project_allocation_id.id
                        or False
                    }
                )
        return result
