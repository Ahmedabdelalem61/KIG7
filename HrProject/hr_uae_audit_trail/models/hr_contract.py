from odoo import models


class HrContract(models.Model):
    _name = "hr.contract"
    _inherit = ["hr.contract", "hr.uae.audit.mixin"]
