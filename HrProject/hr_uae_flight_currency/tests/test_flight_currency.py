"""Per-ticket currency valuation: company-currency total, rate date, refresh
button, and company-currency expense."""
# pylint: disable=protected-access,invalid-name,duplicate-code
from datetime import date
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

D_OLD = date(2000, 1, 1)
RATE = 4.0  # 4 foreign units per 1 company-currency unit


@tagged("post_install", "-at_install", "hr_uae_flight_currency")
class TestFlightCurrency(TransactionCase):
    """Positive and negative checks for flight-ticket currency conversion."""

    @classmethod
    def setUpClass(cls):
        """Company currency + a foreign currency WITH a rate and one WITHOUT."""
        super().setUpClass()
        cls.Flight = cls.env["hr.uae.flight"]
        cls.Rate = cls.env["res.currency.rate"]
        cls.company = cls.env.company
        cls.company_cur = cls.company.currency_id
        cls.emp = cls.env["hr.employee"].create({"name": "FX Flight Emp"})

        # Foreign currency WITH a rate (4 per 1 company unit).
        cls.foreign = cls.env.ref("base.AED")
        if cls.foreign == cls.company_cur:
            cls.foreign = cls.env.ref("base.EUR")
        cls.foreign.active = True
        cls.Rate.search([("currency_id", "=", cls.foreign.id)]).unlink()
        cls.Rate.create(
            {
                "currency_id": cls.foreign.id,
                "name": D_OLD,
                "rate": RATE,
                "company_id": cls.company.id,
            }
        )

        # Foreign currency WITHOUT any rate (fail-safe path).
        cls.norate = cls.env.ref("base.GBP")
        if cls.norate in (cls.company_cur, cls.foreign):
            cls.norate = cls.env.ref("base.CHF")
        cls.norate.active = True
        cls.Rate.search([("currency_id", "=", cls.norate.id)]).unlink()

    def _flight(self, currency=None, price=4000.0, **kw):
        vals = {
            "employee_id": self.emp.id,
            "ticket_price": price,
            "departure_date": date(2026, 3, 1),
            "currency_id": (currency or self.foreign).id,
        }
        vals.update(kw)
        return self.Flight.create(vals)

    # ------------------------------------------------------------- positive

    def test_rate_date_defaults_today(self):
        """rate_date defaults to the creation date (today)."""
        flight = self._flight()
        self.assertEqual(flight.rate_date, fields.Date.context_today(flight))

    def test_total_company_converted(self):
        """total_company is total converted to company currency at rate_date."""
        flight = self._flight(price=4000.0)  # 4000 foreign / 4 = 1000 company
        self.assertAlmostEqual(flight.total_company, 1000.0, places=2)
        self.assertEqual(flight.company_currency_id, self.company_cur)

    def test_identity_when_company_currency(self):
        """A ticket already in company currency converts 1:1."""
        flight = self._flight(currency=self.company_cur, price=750.0)
        self.assertAlmostEqual(flight.total_company, 750.0, places=2)

    def test_recompute_on_value_change(self):
        """Editing the price re-derives total_company."""
        flight = self._flight(price=4000.0)
        flight.ticket_price = 8000.0
        self.assertAlmostEqual(flight.total_company, 2000.0, places=2)

    def test_recompute_on_rate_date_change(self):
        """A different rate on another date changes total_company."""
        self.Rate.create(
            {
                "currency_id": self.foreign.id,
                "name": date(2026, 6, 1),
                "rate": 5.0,
                "company_id": self.company.id,
            }
        )
        flight = self._flight(price=4000.0, rate_date=date(2026, 6, 10))
        self.assertAlmostEqual(flight.total_company, 800.0, places=2)  # 4000/5

    def test_refresh_rate_button(self):
        """Refresh Rate stamps rate_date to today and re-values (network mocked)."""
        flight = self._flight(price=4000.0, rate_date=D_OLD)
        with patch.object(
            type(self.env["res.currency"]),
            "_hr_uae_cron_update_rates",
            return_value=0,
        ):
            flight.action_refresh_rate()
        self.assertEqual(flight.rate_date, fields.Date.context_today(flight))
        self.assertAlmostEqual(flight.total_company, 1000.0, places=2)

    def test_booking_creates_company_currency_expense(self):
        """Booking builds the expense in company currency with converted amount."""
        flight = self._flight(price=4000.0)
        flight.action_book()
        self.assertEqual(flight.booking_state, "booked")
        self.assertTrue(flight.expense_id)
        self.assertEqual(flight.expense_id.currency_id, self.company_cur)
        self.assertAlmostEqual(
            flight.expense_id.total_amount_currency, 1000.0, places=2
        )

    def test_soft_zero_when_no_rate(self):
        """During entry, a no-rate foreign ticket shows 0 (never errors)."""
        flight = self._flight(currency=self.norate, price=1000.0)
        self.assertEqual(flight.total_company, 0.0)

    # ------------------------------------------------------------- negative

    def test_booking_no_rate_raises(self):
        """Booking a foreign ticket with no rate raises a clear error."""
        flight = self._flight(currency=self.norate, price=1000.0)
        with self.assertRaises(UserError):
            flight.action_book()
