import logging

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)

PROJECT_FIELD_MODELS = {
    "hr.employee",
    "hr.employee.base",
    "hr.employee.public",
    "hr.contract",
    "hr.contract.history",
    "hr.job",
    "hr.leave",
    "hr.leave.allocation",
    "hr.leave.report",
    "hr.expense.sheet",
    "hr.uae.flight",
    "hr.uae.termination",
    "hr.uae.salary.adjustment",
    "hr.uae.document",
    "hr.uae.movement.tracking",
    "hr.uae.payroll.dashboard",
    "res.users",
    "resource.resource",
    "mail.activity.plan",
}


def _department_code_from_analytic(analytic):
    return (analytic.code or "").strip() or False


def _analytic_name(analytic):
    return analytic.display_name or analytic.name or "Project"


def _find_or_create_project_department(env, analytic, employee=None):
    Department = env["hr.department"].sudo()
    domain = [("project_allocation_id", "=", analytic.id)]
    if employee and employee.company_id:
        domain = ["|", ("company_id", "=", employee.company_id.id), ("company_id", "=", False)] + domain
    department = Department.search(domain, limit=1)
    if department:
        return department

    name = _analytic_name(analytic)
    search_domain = [("name", "=", name)]
    if employee and employee.company_id:
        search_domain = ["|", ("company_id", "=", employee.company_id.id), ("company_id", "=", False)] + search_domain
    department = Department.search(search_domain, limit=1)
    vals = {"project_allocation_id": analytic.id}
    code = _department_code_from_analytic(analytic)
    if code:
        vals["code"] = code
    if employee and employee.company_id:
        vals["company_id"] = employee.company_id.id
    if department:
        write_vals = {}
        if not department.project_allocation_id:
            write_vals["project_allocation_id"] = analytic.id
        if code and not department.code:
            write_vals["code"] = code
        if write_vals:
            department.with_context(hr_uae_project_department_skip_sync=True).write(
                write_vals
            )
        return department

    vals["name"] = name
    return Department.with_context(hr_uae_project_department_skip_sync=True).create(vals)


def apply_project_department_migration(env):
    """Map legacy employee project allocations onto Project/departments."""
    Employee = env["hr.employee"].sudo()
    Department = env["hr.department"].sudo()

    allocated = Employee.search([("project_allocation_id", "!=", False)])

    for department in Department.search([]):
        employees = allocated.filtered(lambda emp, dept=department: emp.department_id == dept)
        allocations = employees.mapped("project_allocation_id")
        if not employees or department.project_allocation_id:
            continue
        if len(allocations) == 1:
            department.with_context(hr_uae_project_department_skip_sync=True).write(
                {"project_allocation_id": allocations.id}
            )
            continue
        _logger.warning(
            "Project-as-Department migration skipped department %s because employees use multiple project allocations: %s",
            department.display_name,
            ", ".join(allocations.mapped("display_name")),
        )

    for employee in allocated.filtered(lambda emp: not emp.department_id):
        department = _find_or_create_project_department(
            env, employee.project_allocation_id, employee=employee
        )
        employee.with_context(hr_uae_project_department_skip_sync=True).write(
            {"department_id": department.id}
        )

    for employee in Employee.search([("department_id", "!=", False)]):
        allocation = employee.department_id.project_allocation_id
        if employee.project_allocation_id != allocation:
            employee.with_context(hr_uae_project_department_skip_sync=True).write(
                {"project_allocation_id": allocation.id or False}
            )


def sync_existing_flight_projects(env):
    Flight = env["hr.uae.flight"].sudo()
    for flight in Flight.search([("employee_id", "!=", False)]):
        vals = {}
        if not flight.department_id and flight.employee_id.department_id:
            vals["department_id"] = flight.employee_id.department_id.id
        if not flight.project_allocation_id and flight.employee_id.project_allocation_id:
            vals["project_allocation_id"] = flight.employee_id.project_allocation_id.id
        if vals:
            flight.with_context(hr_uae_project_department_skip_sync=True).write(vals)


def relabel_department_metadata(env):
    Field = env["ir.model.fields"].sudo()
    Field.search(
        [("name", "=", "department_id"), ("model", "in", list(PROJECT_FIELD_MODELS))]
    ).write({"field_description": "Project"})
    Field.search([("model", "=", "hr.department"), ("name", "=", "name")]).write(
        {"field_description": "Project"}
    )
    Field.search([("model", "=", "hr.department"), ("name", "=", "parent_id")]).write(
        {"field_description": "Parent Project"}
    )
    Field.search([("model", "=", "hr.department"), ("name", "=", "child_ids")]).write(
        {"field_description": "Child Projects"}
    )
    Field.search([("model", "=", "hr.department"), ("name", "=", "code")]).write(
        {"field_description": "Project Code"}
    )

    env["ir.actions.act_window"].sudo().search([("res_model", "=", "hr.department")]).write(
        {"name": "Projects"}
    )


def post_init_hook(env):
    if not isinstance(env, api.Environment):
        env = api.Environment(env, SUPERUSER_ID, {})
    apply_project_department_migration(env)
    sync_existing_flight_projects(env)
    relabel_department_metadata(env)
