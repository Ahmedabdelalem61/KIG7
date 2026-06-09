from datetime import date, datetime

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

# Fixed dates / rates so payroll-time conversion is deterministic.
D_BASE = date(2000, 1, 1)
D_MAY = date(2026, 5, 1)
D_JUN = date(2026, 6, 1)
RATE_X4 = 0.25  # 1 company-unit = 0.25 foreign  -> 1 foreign = 4 company
RATE_X5 = 0.20  # 1 foreign = 5 company


@tagged("post_install", "-at_install")
class TestMultiCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Contract = cls.env["hr.contract"]
        cls.Employee = cls.env["hr.employee"]
        cls.Payslip = cls.env["hr.payslip"]
        cls.Rate = cls.env["res.currency.rate"]
        cls.struct = cls.env.ref("hr_uae_payroll.hr_payroll_structure_uae")
        cls.company = cls.env.company
        cls.company_cur = cls.company.currency_id

        # Foreign currency WITH rates (x4 from May, x5 from June).
        cls.usd = cls.env.ref("base.USD")
        if cls.usd == cls.company_cur:
            cls.usd = cls.env.ref("base.EUR")
        cls.usd.active = True
        cls.Rate.search([("currency_id", "=", cls.usd.id)]).unlink()
        for name, rate in ((D_BASE, RATE_X4), (D_MAY, RATE_X4), (D_JUN, RATE_X5)):
            cls.Rate.create(
                {
                    "currency_id": cls.usd.id,
                    "name": name,
                    "rate": rate,
                    "company_id": cls.company.id,
                }
            )

        # Foreign currency WITHOUT any rate (for the fail-safe tests).
        cls.norate = cls.env.ref("base.GBP")
        if cls.norate in (cls.company_cur, cls.usd):
            cls.norate = cls.env.ref("base.CHF")
        cls.norate.active = True
        cls.Rate.search([("currency_id", "=", cls.norate.id)]).unlink()

        manager = cls.env.ref("hr_uae_base.group_hr_uae_manager")
        manager.users |= cls.env.user

    # ------------------------------------------------------------------ helpers

    def _make_contract(self, currency=None, wage=1000, housing=0,
                       transport=0, other=0, ticket=0, name="MC"):
        emp = self.Employee.create({"name": "Emp %s" % name})
        vals = {
            "name": "Contract %s" % name,
            "employee_id": emp.id,
            "date_start": date(2026, 1, 1),
            "state": "open",
            "struct_id": self.struct.id,
        }
        if currency and currency != self.company_cur:
            vals.update(
                {
                    "contract_currency_id": currency.id,
                    "wage_foreign": wage,
                    "housing_allowance_foreign": housing,
                    "transportation_allowance_foreign": transport,
                    "other_allowances_foreign": other,
                    "annual_ticket_amount_foreign": ticket,
                }
            )
        else:
            vals.update(
                {
                    "wage": wage,
                    "housing_allowance": housing,
                    "transportation_allowance": transport,
                    "other_allowances": other,
                    "annual_ticket_amount": ticket,
                }
            )
        contract = self.Contract.create(vals)
        emp.contract_id = contract
        return emp, contract

    def _slip(self, emp, contract, dfrom, dto):
        slip = self.Payslip.create(
            {
                "employee_id": emp.id,
                "contract_id": contract.id,
                "struct_id": self.struct.id,
                "date_from": dfrom,
                "date_to": dto,
            }
        )
        slip.compute_sheet()
        return slip

    def _line(self, slip, code):
        line = slip.line_ids.filtered(lambda r: r.code == code)[:1]
        return line.total if line else 0.0

    # =============================================== conversion helper / safety

    def test_01_convert_identity_same_currency(self):
        self.assertEqual(
            self.company_cur._hr_uae_to_company(123.0, self.company, D_MAY), 123.0
        )

    def test_02_convert_value_and_date(self):
        self.assertAlmostEqual(
            self.usd._hr_uae_to_company(1000.0, self.company, date(2026, 5, 31)),
            4000.0, places=2,
        )
        self.assertAlmostEqual(
            self.usd._hr_uae_to_company(1000.0, self.company, date(2026, 6, 30)),
            5000.0, places=2,
        )

    def test_03_convert_missing_rate_raises(self):
        with self.assertRaises(UserError):
            self.norate._hr_uae_to_company(1000.0, self.company, D_MAY)
        # soft mode never raises
        self.assertEqual(
            self.norate._hr_uae_to_company(1000.0, self.company, D_MAY,
                                           raise_if_missing=False),
            0.0,
        )

    # =============================================================== contract

    def test_04_company_currency_identity(self):
        _emp, c = self._make_contract(wage=7000, housing=1000)
        self.assertEqual(c.contract_currency_id, self.company_cur)
        self.assertEqual(c.wage, 7000)
        self.assertEqual(c.wage_foreign, 7000)          # mirror
        self.assertEqual(c.housing_allowance_foreign, 1000)

    def test_05_foreign_sets_company_amounts(self):
        _emp, c = self._make_contract(
            currency=self.usd, wage=1000, housing=200, transport=100,
            other=50, ticket=600,
        )
        today = date.today()
        rate_today = self.usd._hr_uae_to_company(1.0, self.company, today)
        self.assertAlmostEqual(c.wage, 1000 * rate_today, places=2)
        self.assertAlmostEqual(c.housing_allowance, 200 * rate_today, places=2)
        self.assertAlmostEqual(c.transportation_allowance, 100 * rate_today, places=2)
        self.assertAlmostEqual(c.other_allowances, 50 * rate_today, places=2)
        self.assertAlmostEqual(c.annual_ticket_amount, 600 * rate_today, places=2)

    def test_06_write_path_updates_company(self):
        _emp, c = self._make_contract(currency=self.usd, wage=1000)
        c.write({"wage_foreign": 2000})
        today = date.today()
        self.assertAlmostEqual(
            c.wage, self.usd._hr_uae_to_company(2000.0, self.company, today),
            places=2,
        )

    def test_07_employee_contract_wage_related(self):
        emp, c = self._make_contract(currency=self.usd, wage=1000)
        self.assertAlmostEqual(emp.contract_wage, c.wage, places=2)

    def test_08_cron_refresh_follows_rate(self):
        _emp, c = self._make_contract(currency=self.usd, wage=1000)
        # bump today's rate via a fresh row dated today
        self.Rate.create(
            {
                "currency_id": self.usd.id,
                "name": date.today(),
                "rate": 0.10,  # 1 foreign = 10 company
                "company_id": self.company.id,
            }
        )
        self.Contract._hr_uae_cron_refresh_currency()
        self.assertAlmostEqual(c.wage, 1000 * 10, places=2)

    def test_09_switch_back_to_company(self):
        _emp, c = self._make_contract(currency=self.usd, wage=1000)
        c.write({"contract_currency_id": self.company_cur.id})
        self.assertEqual(c.contract_currency_id, self.company_cur)
        self.assertEqual(c.wage_foreign, c.wage)  # mirrors again

    # ============================================ payroll-time conversion (core)

    def test_10_payslip_converts_at_period_end(self):
        emp, c = self._make_contract(
            currency=self.usd, wage=1000, housing=200, transport=100, other=50,
        )
        slip = self._slip(emp, c, D_MAY, date(2026, 5, 31))  # x4
        self.assertAlmostEqual(self._line(slip, "BASIC"), 4000.0, places=2)
        self.assertAlmostEqual(self._line(slip, "HOUSING"), 800.0, places=2)
        self.assertAlmostEqual(self._line(slip, "TRANSPORT"), 400.0, places=2)
        self.assertAlmostEqual(self._line(slip, "OTHER_ALW"), 200.0, places=2)
        # NET = BASIC + ALW
        self.assertAlmostEqual(self._line(slip, "NET"), 5400.0, places=2)

    def test_11_two_periods_different_rates(self):
        emp, c = self._make_contract(currency=self.usd, wage=1000)
        may = self._slip(emp, c, D_MAY, date(2026, 5, 31))   # x4
        jun = self._slip(emp, c, D_JUN, date(2026, 6, 30))   # x5
        self.assertAlmostEqual(self._line(may, "BASIC"), 4000.0, places=2)
        self.assertAlmostEqual(self._line(jun, "BASIC"), 5000.0, places=2)
        self.assertNotAlmostEqual(
            self._line(may, "BASIC"), self._line(jun, "BASIC"), places=2
        )

    def test_12_company_currency_payslip_unchanged(self):
        emp, c = self._make_contract(wage=5000, housing=1500, transport=300, other=200)
        slip = self._slip(emp, c, D_MAY, date(2026, 5, 31))
        self.assertEqual(self._line(slip, "BASIC"), 5000)
        self.assertEqual(self._line(slip, "HOUSING"), 1500)
        self.assertEqual(self._line(slip, "TRANSPORT"), 300)
        self.assertEqual(self._line(slip, "OTHER_ALW"), 200)
        self.assertEqual(self._line(slip, "NET"), 7000)

    def test_13_unpaid_uses_converted_wage(self):
        # 1000 USD x4 = 4000 AED monthly; a 2-day unpaid leave must deduct
        # using the CONVERTED wage: -(4000/30)*2.
        emp, c = self._make_contract(currency=self.usd, wage=1000)
        unpaid = self.env.ref("hr_uae_leaves.leave_type_unpaid")
        leave = self.env["hr.leave"].create(
            {
                "name": "Unpaid",
                "employee_id": emp.id,
                "holiday_status_id": unpaid.id,
                "request_date_from": date(2026, 5, 10),
                "request_date_to": date(2026, 5, 11),
                "date_from": datetime(2026, 5, 10, 0, 0),
                "date_to": datetime(2026, 5, 11, 23, 59),
            }
        )
        leave.action_validate()
        slip = self._slip(emp, c, D_MAY, date(2026, 5, 31))
        self.assertAlmostEqual(
            self._line(slip, "UNPAID"), -(4000.0 / 30.0) * 2, places=2
        )

    def test_14_missing_rate_blocks_payroll(self):
        emp, c = self._make_contract(currency=self.norate, wage=1000)
        self.assertEqual(c.wage, 0.0)  # soft on save, no rate
        with self.assertRaises(UserError):
            self._slip(emp, c, D_MAY, date(2026, 5, 31))

    # ================================================ flight & adjustment

    def test_15_flight_deduction_converted(self):
        emp, c = self._make_contract(wage=5000)
        emp.hr_uae_deduct_employee_paid_tickets = True
        self.env["hr.uae.flight"].create(
            {
                "employee_id": emp.id,
                "currency_id": self.usd.id,
                "ticket_price": 1000,  # USD
                "payment_mode": "own_account",
                "booking_state": "booked",
                "departure_date": date(2026, 5, 15),
            }
        )
        slip = self.Payslip.new(
            {"employee_id": emp.id, "contract_id": c.id,
             "company_id": self.company.id,
             "date_from": D_MAY, "date_to": date(2026, 5, 31)}
        )
        # 1000 USD x4 = 4000 AED
        self.assertAlmostEqual(slip._hr_uae_flight_deduction_amount(), 4000.0, places=2)

    def test_16_adjustment_converted_to_company(self):
        emp, c = self._make_contract(wage=5000)
        slip = self._slip(emp, c, D_MAY, date(2026, 5, 31))
        adj = self.env["hr.uae.salary.adjustment"].create(
            {
                "employee_id": emp.id,
                "kind": "allowance",
                "amount": 1000,
                "currency_id": self.usd.id,
                "mode": "one_shot",
                "target_payslip_id": slip.id,
            }
        )
        adj.action_submit()
        adj.action_approve()
        inp = self.env["hr.payslip.input"].sudo().search(
            [("payslip_id", "=", slip.id), ("code", "=", "ADJ_ALW"),
             ("name", "=", adj.name)], limit=1,
        )
        self.assertTrue(inp)
        self.assertAlmostEqual(inp.amount, 4000.0, places=2)  # 1000 USD x4

    # ===================================================== regression

    def test_17_all_company_currency_regression(self):
        emp, c = self._make_contract(wage=3000)
        slip = self._slip(emp, c, D_MAY, date(2026, 5, 31))
        self.assertEqual(self._line(slip, "BASIC"), 3000)
        self.assertEqual(self._line(slip, "NET"), 3000)
        self.assertEqual(c.wage_foreign, 3000)
