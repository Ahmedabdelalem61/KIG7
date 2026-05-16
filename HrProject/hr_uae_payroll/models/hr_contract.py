from odoo import api, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    @api.model
    def _hr_uae_assign_default_structure(self):
        """Backfill the UAE structure onto blank contracts for the UAE company."""
        structure = self.env.ref(
            "hr_uae_payroll.hr_payroll_structure_uae", raise_if_not_found=False
        )
        if not structure:
            return
        domain = [
            ("struct_id", "=", False),
            ("company_id", "=", structure.company_id.id),
        ]
        self.sudo().search(domain).write({"struct_id": structure.id})
