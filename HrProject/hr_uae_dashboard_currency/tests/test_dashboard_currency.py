"""Custom dashboards display amounts in the company currency: flight (and
adjustment) values converted, currency relabelled."""
# pylint: disable=duplicate-code,protected-access,invalid-name
from datetime import date, timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged

D_OLD = date(2000, 1, 1)
RATE = 4.0  # 4 foreign units per 1 company-currency unit


@tagged("post_install", "-at_install", "hr_uae_dashboard_currency")
class TestDashboardCurrency(TransactionCase):
    """Company-currency display + flight/adjustment conversion on dashboards."""

    @classmethod
    def setUpClass(cls):
        """USD company + a rated foreign currency + booked foreign flights."""
        super().setUpClass()
        cls.company = cls.env.company
        cls.company_cur = cls.company.currency_id
        cls.emp = cls.env["hr.employee"].create({"name": "Dash FX Emp"})

        cls.foreign = cls.env.ref("base.AED")
        if cls.foreign == cls.company_cur:
            cls.foreign = cls.env.ref("base.EUR")
        cls.foreign.active = True
        cls.env["res.currency.rate"].search(
            [("currency_id", "=", cls.foreign.id)]
        ).unlink()
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.foreign.id,
                "name": D_OLD,
                "rate": RATE,
                "company_id": cls.company.id,
            }
        )

        # Two booked tickets of 4000 foreign each -> 1000 company each.
        cls.flights = cls.env["hr.uae.flight"]
        for _i in range(2):
            f = cls.env["hr.uae.flight"].create(
                {
                    "employee_id": cls.emp.id,
                    "ticket_price": 4000.0,
                    "currency_id": cls.foreign.id,
                    "departure_date": fields.Date.context_today(cls.env.user),
                    "booking_state": "booked",
                }
            )
            cls.flights |= f

    # ---------------------------------------------------------- HR dashboard

    def test_hr_dashboard_currency_is_company(self):
        """fetch_dashboard_data labels money in the company currency, not AED."""
        data = self.env["hr.uae.dashboard"].fetch_dashboard_data()
        self.assertEqual(data["currency"]["name"], self.company_cur.name)

    def test_flight_cost_total_converted(self):
        """flight_cost_total is the converted company-currency sum (not raw).

        Isolation-independent: the database may hold other booked flights, so
        we compare against the live company-currency total and prove the figure
        is converted (raw foreign sum is strictly larger)."""
        booked = self.env["hr.uae.flight"].sudo().search(
            [("booking_state", "in", ("booked", "completed"))]
        )
        expected = sum(booked.mapped("total_company"))
        raw = sum(booked.mapped("total"))
        # our 2 foreign tickets alone contribute 2000 company / 8000 raw
        self.assertAlmostEqual(
            sum(self.flights.mapped("total_company")), 2000.0, places=2
        )
        dash = self.env["hr.uae.dashboard"].create({})
        dash._compute_metrics()
        self.assertAlmostEqual(dash.flight_cost_total, expected, places=2)
        self.assertEqual(dash.currency_id, self.company_cur)
        self.assertGreater(raw, expected)  # foreign flights => converted < raw

    def test_flight_per_project_converted(self):
        """flight_per_project values are company-currency sums, not raw."""
        data = self.env["hr.uae.dashboard"].fetch_dashboard_data()
        converted = sum(row["value"] for row in data["flight_per_project"])
        flight = self.env["hr.uae.flight"].sudo()
        group_field = (
            "department_id"
            if "department_id" in flight._fields
            else "project_allocation_id"
        )
        today = fields.Date.context_today(self.env.user)
        domain = [
            ("departure_date", ">=", today - timedelta(days=365)),
            ("booking_state", "in", ("booked", "completed")),
        ]
        raw_groups = flight.read_group(
            domain, ["total:sum"], [group_field], limit=8, orderby="total desc"
        )
        raw = sum(float(g.get("total") or 0.0) for g in raw_groups)
        self.assertGreater(converted, 0.0)
        self.assertLess(converted, raw)  # converted (÷rate) < raw foreign sum

    # ----------------------------------------------------- payroll dashboard

    def test_payroll_dashboard_company_currency_field(self):
        """The payroll dashboard exposes the company currency for labelling."""
        dash_model = self.env["hr.uae.payroll.dashboard"]
        row = dash_model.search([], limit=1)
        if not row:
            self.skipTest("no payroll dashboard rows on this database")
        self.assertEqual(row.company_currency_id, self.company_cur)

    # ------------------------------------------------- live payroll dashboard

    def test_live_dashboard_currency_and_adjustment(self):
        """Live payroll dashboard relabels currency and converts adjustments."""
        adj = self.env["hr.uae.salary.adjustment"].create(
            {
                "employee_id": self.emp.id,
                "kind": "allowance",
                "amount": 4000.0,
                "currency_id": self.foreign.id,
            }
        )
        adj.state = "to_approve"
        data = self.env["hr.uae.payroll.live.dashboard"].fetch_data()
        self.assertEqual(data["currency"]["name"], self.company_cur.name)
        row = next((r for r in data["adjustments"] if r["id"] == adj.id), None)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row["amount"], 1000.0, places=2)  # 4000/4

    # -------------------------------------------------------------- regression

    def test_providers_return_without_error(self):
        """Both data providers still return their full payloads."""
        hr = self.env["hr.uae.dashboard"].fetch_dashboard_data()
        for key in ("kpis", "flight_per_project", "payroll_trend", "currency"):
            self.assertIn(key, hr)
        live = self.env["hr.uae.payroll.live.dashboard"].fetch_data()
        for key in ("kpis", "adjustments", "currency"):
            self.assertIn(key, live)
