from odoo.tests.common import TransactionCase


class TestHrUaeBase(TransactionCase):
    def test_uae_calendar_seeded(self):
        calendar = self.env.ref("hr_uae_base.resource_calendar_uae")
        self.assertEqual(calendar.tz, "Asia/Dubai")
        self.assertEqual(calendar.hours_per_day, 8.0)
        self.assertEqual(len(calendar.attendance_ids), 12)

    def test_aed_currency_active(self):
        aed = self.env.ref("base.AED")
        self.assertTrue(aed.active)

    def test_security_groups_present(self):
        for xmlid in (
            "hr_uae_base.group_hr_uae_user",
            "hr_uae_base.group_hr_uae_document_owner",
            "hr_uae_base.group_hr_uae_finance",
            "hr_uae_base.group_hr_uae_manager",
            "hr_uae_base.group_hr_uae_management",
        ):
            self.assertTrue(self.env.ref(xmlid))

    def test_root_menu_present(self):
        menu = self.env.ref("hr_uae_base.menu_hr_uae_root")
        self.assertEqual(menu.name, "HR UAE Admin")
