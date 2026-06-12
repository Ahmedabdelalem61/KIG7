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

    # ----------------------------------------------- fetch on activation

    def _activate(self, currencies, fetch_return):
        """Activate ``currencies`` with a mocked online fetch; return the mock."""
        with patch.object(
            type(self.Currency),
            "_hr_uae_fetch_rates",
            return_value=fetch_return,
        ) as mock_fetch:
            currencies.with_context(hr_uae_fx_force_autofetch=True).write(
                {"active": True}
            )
        return mock_fetch

    def test_activation_fetches_rate(self):
        """Activating an inactive currency immediately stores today's rate."""
        self._rate_rows().unlink()
        self.foreign.active = False
        mock_fetch = self._activate(self.foreign, {self.foreign.name: 0.27})
        self.assertTrue(self.foreign.active)
        mock_fetch.assert_called_once_with(self.company.currency_id.name)
        rows = self._rate_rows()
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows.rate, 0.27, places=6)

    def test_activation_provider_failure_keeps_active(self):
        """A provider outage must not block activation; no rate row appears."""
        self._rate_rows().unlink()
        self.foreign.active = False
        self._activate(self.foreign, {})
        self.assertTrue(self.foreign.active)
        self.assertFalse(self._rate_rows())

    def test_activation_no_duplicate_rows(self):
        """Activation updates an existing same-date row instead of duplicating."""
        self._rate_rows().unlink()
        self.Currency._hr_uae_upsert_rates(self.company, {self.foreign.name: 0.25})
        self.foreign.active = False
        self._activate(self.foreign, {self.foreign.name: 0.30})
        rows = self._rate_rows()
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows.rate, 0.30, places=6)

    def test_activation_batch(self):
        """Activating several currencies in one write rates them all with a
        single fetch per company."""
        base = self.company.currency_id
        batch = (
            self.env.ref("base.EUR") | self.env.ref("base.GBP")
        ) - base
        batch.with_context(hr_uae_fx_skip_autofetch=True).write({"active": False})
        rates = {c.name: 0.2 for c in batch}
        mock_fetch = self._activate(batch, rates)
        self.assertEqual(mock_fetch.call_count, 1)
        for currency in batch:
            rows = self.Rate.search(
                [
                    ("currency_id", "=", currency.id),
                    ("name", "=", self.today),
                    ("company_id", "=", self.company.id),
                ]
            )
            self.assertEqual(len(rows), 1, currency.name)
            self.assertAlmostEqual(rows.rate, 0.2, places=6)

    def test_activation_company_currency_skipped(self):
        """Activating the company's own currency fetches nothing (1:1)."""
        base = self.company.currency_id
        with patch.object(
            type(self.Currency), "_hr_uae_fetch_rates", return_value={}
        ) as mock_fetch:
            count = base.with_context(
                hr_uae_fx_force_autofetch=True
            )._hr_uae_fetch_rates_on_activation()
        self.assertEqual(count, 0)
        mock_fetch.assert_not_called()
