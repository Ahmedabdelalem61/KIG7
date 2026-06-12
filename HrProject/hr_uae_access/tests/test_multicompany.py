"""Multi-company record rules: company-scoped users see only their company."""
from odoo.tests.common import tagged

from .common import Kig7AccessCase


@tagged("post_install", "-at_install", "hr_uae_access", "kig7_multicompany")
class TestMultiCompany(Kig7AccessCase):
    """Documents are company-scoped for managers (existing ir.rule)."""

    @classmethod
    def setUpClass(cls):
        """Try to create a second company; flag if this DB forbids it."""
        super().setUpClass()
        cls.company_b = None
        try:
            with cls.env.cr.savepoint():
                cls.company_b = cls.env["res.company"].create(
                    {"name": "KIG7 MultiCo Probe"}
                )
        except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            cls.company_b = None  # pragma: no cover

    def _require_company_b(self):
        if not self.company_b:
            self.skipTest(
                "second company cannot be created on this database "
                "(accounting chart-template constraint)"
            )

    def test_manager_sees_only_own_company_documents(self):
        """HR Manager (company A) cannot read a company-B document."""
        self._require_company_b()
        employee_b = (
            self.env["hr.employee"]
            .sudo()
            .create(
                {"name": "MultiCo Employee", "company_id": self.company_b.id}
            )
        )
        document_b = (
            self.env["hr.uae.document"]
            .sudo()
            .create(
                {
                    "name": "MultiCo doc",
                    "employee_id": employee_b.id,
                    "document_type": "other",
                }
            )
        )
        visible = (
            self.env["hr.uae.document"].with_user(self.manager).search([])
        )
        self.assertNotIn(document_b, visible)
        self.assert_record_read_blocked(self.manager, document_b)

    def test_manager_sees_own_company_documents(self):
        """HR Manager still sees company-A documents (positive control)."""
        document_a = (
            self.env["hr.uae.document"]
            .sudo()
            .create(
                {
                    "name": "Own-company doc",
                    "employee_id": self.probe_employee.id,
                    "document_type": "other",
                }
            )
        )
        visible = (
            self.env["hr.uae.document"].with_user(self.manager).search([])
        )
        self.assertIn(document_a, visible)
