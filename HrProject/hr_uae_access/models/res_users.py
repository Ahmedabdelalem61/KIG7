from odoo import api, models
from odoo.exceptions import ValidationError

# The three KIG7 roles are mutually exclusive: a user holds at most one.
KIG7_ROLE_XMLIDS = (
    "hr_uae_access.group_kig7_hr_officer",
    "hr_uae_access.group_kig7_hr_manager",
    "hr_uae_access.group_kig7_payroll_manager",
)


class ResUsers(models.Model):  # pylint: disable=too-few-public-methods
    """Enforce that KIG7 roles are mutually exclusive."""

    _inherit = "res.users"

    def _kig7_role_groups(self):
        """The KIG7 role groups present in this database."""
        groups = self.env["res.groups"]
        for xmlid in KIG7_ROLE_XMLIDS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                groups |= group
        return groups

    @api.constrains("groups_id")
    def _check_kig7_single_role(self):
        roles = self._kig7_role_groups()
        if not roles:
            return
        for user in self:
            held = user.groups_id & roles
            if len(held) > 1:
                raise ValidationError(
                    self.env._(
                        "KIG7 roles are mutually exclusive: %(user)s cannot hold "
                        "%(roles)s at the same time. Pick exactly one role.",
                        user=user.name,
                        roles=", ".join(held.mapped("name")),
                    )
                )
