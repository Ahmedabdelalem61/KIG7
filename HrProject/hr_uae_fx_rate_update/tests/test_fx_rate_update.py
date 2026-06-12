from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase, tagged

from ..models import res_currency as fx_mod  # for patching DEFAULT_FX_URL


@tagged("post_install", "-at_install")
class TestFxRateUpdate(TransactionCase):
    """Tests for hr_uae_fx_rate_update: rate fetching, upsert, and cron."""

    # pylint: disable=protected-access

    @classmethod
    def setUpClass(cls):  # pylint: disable=invalid-name
        """Set up shared test fixtures."""
        super().setUpClass()
        cls.Currency = cls.env["res.currency"]
        cls.Rate = cls.env["res.currency.rate"]
        cls.company = cls.env.company
        cls.foreign = cls.env.ref("base.USD")
        if cls.foreign == cls.company.currency_id:
            cls.foreign = cls.env.ref("base.EUR")
        cls.foreign.active = True
        cls.today = fields.Date.context_today(cls.Currency)

    def _rate_rows(self):
        """Return today's rate rows for the test foreign currency."""
        return self.Rate.search(
            [
                ("currency_id", "=", self.foreign.id),
                ("name", "=", self.today),
                ("company_id", "=", self.company.id),
            ]
        )

    def test_upsert_creates_then_updates(self):
        """Upsert creates a rate row; a second call updates it in place."""
        self._rate_rows().unlink()
        n = self.Currency._hr_uae_upsert_rates(
            self.company, {self.foreign.name: 0.25}
        )
        self.assertGreaterEqual(n, 1)
        rows = self._rate_rows()
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows.rate, 0.25, places=6)
        # second run updates the same row, does not duplicate
        self.Currency._hr_uae_upsert_rates(self.company, {self.foreign.name: 0.30})
        rows = self._rate_rows()
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows.rate, 0.30, places=6)

    def test_upsert_skips_base_and_unknown(self):
        """Upsert ignores the base currency and unknown currency codes."""
        base_code = self.company.currency_id.name
        n = self.Currency._hr_uae_upsert_rates(
            self.company, {base_code: 1.0, "ZZZ": 9.9}
        )
        self.assertEqual(n, 0)  # base excluded, ZZZ not a real active currency

    def test_cron_with_mocked_fetch(self):
        """Cron writes a rate row when fetch returns a valid dict."""
        self._rate_rows().unlink()
        with patch.object(
            type(self.Currency),
            "_hr_uae_fetch_rates",
            return_value={self.foreign.name: 0.25},
        ):
            count = self.Currency._hr_uae_cron_update_rates()
        self.assertGreaterEqual(count, 1)
        self.assertEqual(len(self._rate_rows()), 1)

    def test_fetch_failure_returns_empty(self):
        """Fetch returns {} and never raises when the URL is unreachable."""
        with patch.object(fx_mod, "DEFAULT_FX_URL", "http://127.0.0.1:9/%s"):
            self.assertEqual(
                self.Currency._hr_uae_fetch_rates(self.company.currency_id.name),
                {},
            )
