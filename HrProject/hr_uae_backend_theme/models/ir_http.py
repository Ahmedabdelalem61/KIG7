# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        session = super().session_info()
        if session.get("uid"):
            session["hr_uae_backend_theme"] = self.env.user._get_hr_theme_payload()
        return session
