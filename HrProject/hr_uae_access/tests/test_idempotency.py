"""Install/upgrade idempotency: no duplicated users, groups or categories."""
from odoo.tests.common import tagged

from .common import Kig7AccessCase

LOGINS = ("kig7.hr.officer", "kig7.hr.manager", "kig7.payroll.manager")


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_idempotency")
class TestIdempotency(Kig7AccessCase):
    """These run after install AND after every upgrade: counts must hold."""

    def test_single_category(self):
        """Exactly one 'KIG7 Access Rights' module category exists."""
        self.assertEqual(
            self.env["ir.module.category"].search_count(
                [("name", "=", "KIG7 Access Rights")]
            ),
            1,
        )

    def test_exactly_three_roles(self):
        """Exactly the three roles live under the category."""
        category = self.env.ref("hr_uae_access.module_category_kig7_access")
        groups = self.env["res.groups"].search(
            [("category_id", "=", category.id)]
        )
        self.assertEqual(len(groups), 3)
        self.assertEqual(
            sorted(groups.mapped("name")),
            ["HR Manager", "HR Officer", "Payroll & Accounting Manager"],
        )

    def test_users_not_duplicated(self):
        """Each predefined login exists exactly once (even archived)."""
        users = self.env["res.users"].with_context(active_test=False)
        for login in LOGINS:
            self.assertEqual(
                users.search_count([("login", "=", login)]),
                1,
                f"login {login} must exist exactly once",
            )

    def test_officer_access_lines_not_duplicated(self):
        """The module's extra ACL lines exist exactly once."""
        officer = self.env.ref("hr_uae_access.group_kig7_hr_officer")
        flights = self.env["ir.model.access"].search(
            [
                ("group_id", "=", officer.id),
                ("model_id.model", "=", "hr.uae.flight"),
            ]
        )
        self.assertEqual(len(flights), 1)
