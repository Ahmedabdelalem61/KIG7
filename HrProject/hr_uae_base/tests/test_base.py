from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestHrUaeBase(TransactionCase):
    """hr_uae_base seed data and company-default behaviour."""

    # pylint: disable=protected-access

    def _set_main_company_currency(self, currency):
        """Switch the main company to ``currency``, bypassing the accounting
        journal-items block (the test DB has journal entries)."""
        main = self.env.ref("base.main_company")
        with patch.object(
            type(main), "_existing_accounting", return_value=False
        ):
            main.sudo().write({"currency_id": currency.id})
        return main

    def test_explicit_currency_survives_defaults(self):
        """An explicitly selected company currency is never reset to the
        code-defined default by the UAE helpers outside of installation."""
        aed = self.env.ref("base.AED")
        main = self._set_main_company_currency(aed)
        self.env["res.company"]._hr_uae_apply_defaults()
        self.assertEqual(main.currency_id, aed)
        self.env["res.company"]._hr_uae_enforce_main_company()
        self.assertEqual(main.currency_id, aed)

    def test_install_mode_bootstraps_code_currency(self):
        """During module data loading (install_mode) the code-defined company
        currency (USD) is bootstrapped onto UAE companies."""
        usd = self.env.ref("base.USD")
        aed = self.env.ref("base.AED")
        main = self._set_main_company_currency(aed)
        with patch.object(
            type(main), "_existing_accounting", return_value=False
        ):
            self.env["res.company"].with_context(
                install_mode=True
            )._hr_uae_enforce_main_company()
        self.assertEqual(main.currency_id, usd)

    def test_code_currency_is_usd(self):
        """The project's code-defined company currency is USD."""
        self.assertEqual(
            self.env["res.company"]._hr_uae_company_currency(),
            self.env.ref("base.USD"),
        )

    def test_calendar_default_applies_outside_install(self):
        """Non-currency defaults (working calendar) still apply on every run."""
        calendar = self.env.ref("hr_uae_base.resource_calendar_uae")
        main = self.env.ref("base.main_company")
        main.sudo().resource_calendar_id = False
        self.env["res.company"]._hr_uae_apply_defaults()
        self.assertEqual(main.resource_calendar_id, calendar)

    def test_uae_calendar_seeded(self):
        """The UAE working calendar is seeded with the expected schedule."""
        calendar = self.env.ref("hr_uae_base.resource_calendar_uae")
        self.assertEqual(calendar.tz, "Asia/Dubai")
        self.assertEqual(calendar.hours_per_day, 8.0)
        self.assertEqual(len(calendar.attendance_ids), 12)

    def test_aed_currency_active(self):
        """AED is activated by the module data."""
        aed = self.env.ref("base.AED")
        self.assertTrue(aed.active)

    def test_security_groups_present(self):
        """All UAE security groups exist."""
        for xmlid in (
            "hr_uae_base.group_hr_uae_user",
            "hr_uae_base.group_hr_uae_document_owner",
            "hr_uae_base.group_hr_uae_finance",
            "hr_uae_base.group_hr_uae_manager",
            "hr_uae_base.group_hr_uae_management",
        ):
            self.assertTrue(self.env.ref(xmlid))

    def test_root_menu_present(self):
        """The HR UAE root menu exists."""
        menu = self.env.ref("hr_uae_base.menu_hr_uae_root")
        self.assertEqual(menu.name, "HR UAE Admin")
