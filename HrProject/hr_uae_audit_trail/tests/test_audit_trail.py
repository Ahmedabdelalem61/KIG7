from odoo.tests.common import TransactionCase


class TestHrUaeAuditTrail(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Log = cls.env["hr.uae.audit.log"]
        cls.Employee = cls.env["hr.employee"]

    def test_create_logs_create_entry(self):
        before = self.Log.search_count([])
        emp = self.Employee.create({"name": "AuditCreate"})
        after = self.Log.search_count([("model", "=", "hr.employee"), ("res_id", "=", emp.id)])
        self.assertGreaterEqual(after, 1)
        self.assertGreater(after + before, before)

    def test_write_logs_changes_with_old_and_new(self):
        emp = self.Employee.create({"name": "AuditWrite"})
        emp.write({"passport_id": "P12345"})
        log = self.Log.search(
            [
                ("model", "=", "hr.employee"),
                ("res_id", "=", emp.id),
                ("field_name", "=", "passport_id"),
                ("change_type", "=", "write"),
            ],
            limit=1,
        )
        self.assertTrue(log)
        self.assertEqual(log.new_display, "P12345")

    def test_skip_audit_context(self):
        emp = self.Employee.with_context(hr_uae_skip_audit=True).create(
            {"name": "AuditSkipped"}
        )
        emp.with_context(hr_uae_skip_audit=True).write({"passport_id": "X"})
        logs = self.Log.search(
            [("model", "=", "hr.employee"), ("res_id", "=", emp.id)]
        )
        self.assertFalse(logs)

    def test_format_many2one_uses_display_name(self):
        rank = self.env.ref("hr_uae_master_data.rank_civilian")
        emp = self.Employee.create({"name": "AuditM2O"})
        emp.write({"rank_id": rank.id})
        log = self.Log.search(
            [
                ("model", "=", "hr.employee"),
                ("res_id", "=", emp.id),
                ("field_name", "=", "rank_id"),
            ],
            limit=1,
        )
        self.assertTrue(log)
        self.assertEqual(log.new_display, rank.display_name)

    def test_employee_audit_log_count(self):
        emp = self.Employee.create({"name": "AuditCount"})
        emp.write({"passport_id": "C1"})
        emp.write({"passport_id": "C2"})
        emp.invalidate_recordset(["audit_log_count"])
        self.assertGreaterEqual(emp.audit_log_count, 2)
