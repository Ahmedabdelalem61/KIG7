from odoo import fields, models


class HrContractHistory(models.Model):
    _inherit = "hr.contract.history"

    department_id = fields.Many2one("hr.department", string="Project")


class HrLeaveReport(models.Model):
    _inherit = "hr.leave.report"

    department_id = fields.Many2one("hr.department", string="Project")


class ResUsers(models.Model):
    _inherit = "res.users"

    department_id = fields.Many2one("hr.department", string="Project")


class ResourceResource(models.Model):
    _inherit = "resource.resource"

    department_id = fields.Many2one("hr.department", string="Project")


class MailActivityPlan(models.Model):
    _inherit = "mail.activity.plan"

    department_id = fields.Many2one("hr.department", string="Project")


class HrEmployeeSkillLog(models.Model):
    _inherit = "hr.employee.skill.log"

    department_id = fields.Many2one("hr.department", string="Project")
