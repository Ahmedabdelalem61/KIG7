"""Role isolation: mutual exclusivity, exact group membership, no accidental
access through implied or inherited groups."""
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import Kig7AccessCase


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_isolation")
class TestRoleIsolation(Kig7AccessCase):
    """Group wiring assertions independent of any model access."""

    @classmethod
    def setUpClass(cls):
        """Resolve role groups."""
        super().setUpClass()
        cls.role_officer = cls.env.ref("hr_uae_access.group_kig7_hr_officer")
        cls.role_manager = cls.env.ref("hr_uae_access.group_kig7_hr_manager")
        cls.role_payroll = cls.env.ref(
            "hr_uae_access.group_kig7_payroll_manager"
        )
        cls.roles = cls.role_officer | cls.role_manager | cls.role_payroll

    @staticmethod
    def _closure(group):
        """Transitive closure of a group's implied groups (incl. itself)."""
        seen = group
        todo = group.implied_ids
        while todo:
            seen |= todo
            todo = todo.implied_ids - seen
        return seen

    def test_roles_mutually_exclusive(self):
        """Adding a second KIG7 role to a user raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.officer.sudo().write(
                {"groups_id": [(4, self.role_manager.id)]}
            )
        with self.assertRaises(ValidationError):
            self.payroll.sudo().write(
                {"groups_id": [(4, self.role_officer.id)]}
            )

    def test_roles_do_not_imply_each_other(self):
        """The three roles are disjoint in their implication closures."""
        for role in self.roles:
            self.assertFalse(
                (self._closure(role) & self.roles) - role,
                f"{role.name} must not imply another KIG7 role",
            )

    def test_users_hold_exactly_their_role(self):
        """Each predefined user holds exactly one KIG7 role + internal user."""
        internal = self.env.ref("base.group_user")
        portal = self.env.ref("base.group_portal")
        system = self.env.ref("base.group_system")
        expected = (
            (self.officer, self.role_officer),
            (self.manager, self.role_manager),
            (self.payroll, self.role_payroll),
        )
        for user, role in expected:
            held_roles = user.groups_id & self.roles
            self.assertEqual(held_roles, role, user.login)
            self.assertIn(internal, user.groups_id, user.login)
            self.assertNotIn(portal, user.groups_id, user.login)
            self.assertNotIn(system, user.groups_id, user.login)

    def test_officer_gains_nothing_extra(self):
        """Officer's expanded groups contain none of the forbidden grants."""
        for xmlid in (
            "hr_contract.group_hr_contract_manager",
            "hr_uae_base.group_hr_uae_manager",
            "account.group_account_manager",
            "hr_expense.group_hr_expense_manager",
            "payroll.group_payroll_user",
            "payroll.group_payroll_manager",
            "base.group_system",
        ):
            self.assertNotIn(
                self.env.ref(xmlid),
                self.officer.groups_id,
                f"Officer must not inherit {xmlid}",
            )

    def test_manager_gains_no_accounting_or_admin(self):
        """HR Manager's expanded groups exclude accounting admin and system."""
        for xmlid in (
            "account.group_account_manager",
            "hr_expense.group_hr_expense_manager",
            "payroll.group_payroll_manager",
            "base.group_system",
        ):
            self.assertNotIn(
                self.env.ref(xmlid),
                self.manager.groups_id,
                f"HR Manager must not inherit {xmlid}",
            )

    def test_payroll_gains_no_hr_uae_groups(self):
        """Payroll manager's expanded groups contain NO hr_uae_base group —
        the lever that keeps custom dashboards/menus out of reach."""
        hr_uae_groups = self.env["res.groups"].search(
            [
                (
                    "category_id",
                    "=",
                    self.env.ref("hr_uae_base.module_category_hr_uae").id,
                )
            ]
        )
        self.assertTrue(hr_uae_groups)
        self.assertFalse(self.payroll.groups_id & hr_uae_groups)
        self.assertNotIn(
            self.env.ref("base.group_system"), self.payroll.groups_id
        )
