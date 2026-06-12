"""Shared base class and assertion helpers for the KIG7 access test suite."""
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

_OPS = {"r": "read", "w": "write", "c": "create", "u": "unlink"}


class Kig7AccessCase(TransactionCase):
    """Resolves the predefined users and provides access assertions."""

    # pylint: disable=protected-access

    @classmethod
    def setUpClass(cls):  # pylint: disable=invalid-name
        """Resolve predefined users and a probe employee."""
        super().setUpClass()
        cls.officer = cls.env.ref("hr_uae_access.user_kig7_hr_officer")
        cls.manager = cls.env.ref("hr_uae_access.user_kig7_hr_manager")
        cls.payroll = cls.env.ref("hr_uae_access.user_kig7_payroll_manager")
        cls.admin = cls.env.ref("base.user_admin")
        cls.role_users = cls.officer | cls.manager | cls.payroll
        cls.probe_employee = cls.env["hr.employee"].create(
            {"name": "KIG7 ACL Probe Employee"}
        )

    # ------------------------------------------------------------- helpers

    def sudo_model(self, model):
        """Model as superuser (fixture creation)."""
        return self.env[model].sudo()

    def assert_can(self, user, model, ops="r"):
        """ACL grants ``ops`` (subset of 'rwcu') on ``model`` for ``user``."""
        records = self.env[model].with_user(user)
        for op, operation in _OPS.items():
            if op in ops:
                self.assertTrue(
                    records.has_access(operation),
                    f"{user.login} should be allowed to {operation} {model}",
                )

    def assert_cannot(self, user, model, ops="rwcu"):
        """ACL denies ``ops`` on ``model`` for ``user`` (raises AccessError)."""
        records = self.env[model].with_user(user)
        for op, operation in _OPS.items():
            if op in ops:
                self.assertFalse(
                    records.has_access(operation),
                    f"{user.login} should NOT be allowed to {operation} {model}",
                )
                with self.assertRaises(
                    AccessError,
                    msg=f"{user.login}: {operation} on {model} "
                    "must raise AccessError",
                ):
                    records.check_access(operation)

    def assert_menu(self, user, menu_xmlid, visible):
        """Menu is (in)visible to ``user``."""
        menu = self.env.ref(menu_xmlid)
        visible_ids = self.env["ir.ui.menu"].with_user(user)._visible_menu_ids()
        if visible:
            self.assertIn(
                menu.id, visible_ids,
                f"{user.login} should see menu {menu_xmlid}",
            )
        else:
            self.assertNotIn(
                menu.id, visible_ids,
                f"{user.login} should NOT see menu {menu_xmlid}",
            )

    @staticmethod
    def _action_model(action):
        """Target model of a window, server or report action."""
        return (
            getattr(action, "res_model", False)
            or getattr(action, "model_name", False)
            or getattr(action, "model", False)
        )

    def assert_action_model_blocked(self, user, action_xmlid):
        """Direct access through the action's model raises AccessError —
        forbidden actions stay blocked even when called by URL/id."""
        model = self._action_model(self.env.ref(action_xmlid))
        with self.assertRaises(
            AccessError,
            msg=f"{user.login}: model {model} behind action "
            f"{action_xmlid} must be blocked",
        ):
            self.env[model].with_user(user).check_access("read")

    def assert_action_model_allowed(self, user, action_xmlid):
        """The action's model is readable — the action genuinely works."""
        model = self._action_model(self.env.ref(action_xmlid))
        self.assertTrue(
            self.env[model].with_user(user).has_access("read"),
            f"{user.login} should reach action {action_xmlid} "
            f"(model {model})",
        )

    def assert_record_read_blocked(self, user, record):
        """Reading a specific record raises AccessError (record-rule deny)."""
        with self.assertRaises(AccessError):
            record.with_user(user).read(["id"])
