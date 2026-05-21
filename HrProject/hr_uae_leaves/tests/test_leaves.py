from odoo.tests.common import TransactionCase


class TestHrUaeLeaves(TransactionCase):
    def test_leave_types_seeded(self):
        for xmlid in (
            "hr_uae_leaves.leave_type_annual",
            "hr_uae_leaves.leave_type_special",
            "hr_uae_leaves.leave_type_medical",
            "hr_uae_leaves.leave_type_unpaid",
        ):
            lt = self.env.ref(xmlid)
            self.assertTrue(lt)
            self.assertTrue(lt.active)

    def test_unpaid_flag(self):
        unpaid = self.env.ref("hr_uae_leaves.leave_type_unpaid")
        self.assertTrue(unpaid.hr_uae_unpaid)
        annual = self.env.ref("hr_uae_leaves.leave_type_annual")
        self.assertFalse(annual.hr_uae_unpaid)

    def test_only_annual_holds_payroll(self):
        annual = self.env.ref("hr_uae_leaves.leave_type_annual")
        special = self.env.ref("hr_uae_leaves.leave_type_special")
        medical = self.env.ref("hr_uae_leaves.leave_type_medical")
        unpaid = self.env.ref("hr_uae_leaves.leave_type_unpaid")
        self.assertTrue(annual.hr_uae_hold_payroll)
        self.assertFalse(special.hr_uae_hold_payroll)
        self.assertFalse(medical.hr_uae_hold_payroll)
        self.assertFalse(unpaid.hr_uae_hold_payroll)

    def test_status_codes(self):
        self.assertEqual(
            self.env.ref("hr_uae_leaves.leave_type_annual").hr_uae_status_code,
            "vacations",
        )
        self.assertEqual(
            self.env.ref("hr_uae_leaves.leave_type_special").hr_uae_status_code,
            "special_permit",
        )
        self.assertEqual(
            self.env.ref("hr_uae_leaves.leave_type_medical").hr_uae_status_code,
            "sick_leave",
        )

    def test_alert_days(self):
        self.assertEqual(
            self.env.ref("hr_uae_leaves.leave_type_annual").hr_uae_alert_days, 20
        )
        self.assertEqual(
            self.env.ref("hr_uae_leaves.leave_type_special").hr_uae_alert_days, 7
        )

    def test_movement_tracking_view_exists(self):
        # Just verify the view is queryable (returns 0 rows is fine).
        self.assertGreaterEqual(
            self.env["hr.uae.movement.tracking"].search_count([]),
            0,
        )
