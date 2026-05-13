from datetime import date, timedelta

from odoo.tests.common import TransactionCase


class TestHrUaeDocuments(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.Doc = cls.env["hr.uae.document"]
        cls.emp = cls.Employee.create({"name": "Doc Test"})

    def test_create_document(self):
        doc = self.Doc.create(
            {
                "employee_id": self.emp.id,
                "document_type": "passport",
                "name": "P-123",
                "expiry_date": date.today() + timedelta(days=200),
            }
        )
        self.assertEqual(doc.expiry_state, "ok")
        self.assertGreater(doc.days_to_expiry, 90)

    def test_expiry_states(self):
        today = date.today()
        cases = [
            (today - timedelta(days=10), "expired"),
            (today + timedelta(days=20), "expires_30"),
            (today + timedelta(days=50), "expires_60"),
            (today + timedelta(days=80), "expires_90"),
            (today + timedelta(days=200), "ok"),
        ]
        for expiry, expected in cases:
            doc = self.Doc.create(
                {
                    "employee_id": self.emp.id,
                    "document_type": "visa",
                    "name": "V-%s" % expiry.isoformat(),
                    "expiry_date": expiry,
                }
            )
            self.assertEqual(
                doc.expiry_state,
                expected,
                "expiry %s should be %s, got %s" % (expiry, expected, doc.expiry_state),
            )

    def test_employee_document_count(self):
        self.Doc.create(
            {
                "employee_id": self.emp.id,
                "document_type": "passport",
                "name": "P1",
                "expiry_date": date.today() + timedelta(days=10),
            }
        )
        self.Doc.create(
            {
                "employee_id": self.emp.id,
                "document_type": "medical",
                "name": "M1",
            }
        )
        self.emp.invalidate_recordset(["document_count", "document_alert_count"])
        self.assertGreaterEqual(self.emp.document_count, 2)
        self.assertGreaterEqual(self.emp.document_alert_count, 1)
