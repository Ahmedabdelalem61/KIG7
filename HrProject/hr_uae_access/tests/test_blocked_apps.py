"""Discuss, Calendar, Website, Settings and technical models are blocked for
every KIG7 role; only base.group_system keeps unrestricted admin access."""
from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Kig7AccessCase

BLOCKED_ROOT_MENUS = (
    "mail.menu_root_discuss",
    "calendar.mail_menu_calendar",
    "website.menu_website_configuration",
    "base.menu_administration",
)

TECH_MODELS = (
    "ir.config_parameter",
    "ir.cron",
    "ir.rule",
    "ir.model.access",
    "res.groups",
)


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_blocked")
class TestBlockedApps(Kig7AccessCase):
    """App- and technical-level denials, identical for all three roles."""

    @classmethod
    def setUpClass(cls):
        """Admin-owned fixture records in the blocked apps."""
        super().setUpClass()
        now = fields.Datetime.now()
        cls.calendar_event = cls.env["calendar.event"].sudo().create(
            {"name": "KIG7 blocked probe", "start": now, "stop": now}
        )
        cls.discuss_channel = cls.env["discuss.channel"].sudo().create(
            {"name": "kig7-blocked-probe", "channel_type": "channel"}
        )
        cls.website_page = (
            cls.env["website.page"].sudo().search([], limit=1)
        )

    def test_calendar_blocked_for_all_roles(self):
        """Calendar events: empty search, record read and create denied."""
        for user in self.role_users:
            model = self.env["calendar.event"].with_user(user)
            self.assertFalse(
                model.search([]), f"{user.login} must see no calendar events"
            )
            self.assert_record_read_blocked(user, self.calendar_event)
            with self.assertRaises(AccessError):
                model.create(
                    {
                        "name": "forbidden",
                        "start": fields.Datetime.now(),
                        "stop": fields.Datetime.now(),
                    }
                )

    def test_discuss_blocked_for_all_roles(self):
        """Discuss channels: empty search and record read denied."""
        for user in self.role_users:
            model = self.env["discuss.channel"].with_user(user)
            self.assertFalse(
                model.search([]), f"{user.login} must see no channels"
            )
            self.assert_record_read_blocked(user, self.discuss_channel)

    def test_website_blocked_for_all_roles(self):
        """Website pages: denied at ACL level (internal users have no access
        to website.page at all) or, failing that, hidden by the record rule."""
        for user in self.role_users:
            model = self.env["website.page"].with_user(user)
            if not model.has_access("read"):
                with self.assertRaises(AccessError):
                    model.check_access("read")
                continue  # ACL-level denial: even stronger than the rule
            self.assertFalse(
                model.search([]), f"{user.login} must see no website pages"
            )
            if self.website_page:
                self.assert_record_read_blocked(user, self.website_page)

    def test_blocked_root_menus_hidden(self):
        """Discuss/Calendar/Website/Settings roots invisible to all roles,
        visible to the administrator."""
        for xmlid in BLOCKED_ROOT_MENUS:
            for user in self.role_users:
                self.assert_menu(user, xmlid, False)

    def test_technical_models_blocked(self):
        """No role can alter technical security/config models."""
        for user in self.role_users:
            for model in TECH_MODELS:
                self.assert_cannot(user, model, "wcu")

    def test_no_role_is_system(self):
        """No role user belongs to base.group_system."""
        system = self.env.ref("base.group_system")
        for user in self.role_users:
            self.assertNotIn(system, user.groups_id)

    def test_admin_keeps_unrestricted_access(self):
        """base.group_system retains everything the roles lost."""
        self.assertIn(self.env.ref("base.group_system"), self.admin.groups_id)
        for model in TECH_MODELS:
            self.assert_can(self.admin, model, "rw")
        self.assertTrue(
            self.calendar_event.with_user(self.admin).read(["name"])
        )
        for xmlid in BLOCKED_ROOT_MENUS:
            # archived menus (e.g. Discuss on this DB) are hidden for
            # everyone by definition — assert only on active ones
            if self.env.ref(xmlid).active:
                self.assert_menu(self.admin, xmlid, True)
