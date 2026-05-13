from datetime import timedelta

from odoo import api, fields, models


class HrUaeDashboard(models.TransientModel):
    """In-memory dashboard model whose computed fields drive the tile view."""

    _name = "hr.uae.dashboard"
    _description = "HR UAE Dashboard"

    name = fields.Char(default="Dashboard")
    employees_total = fields.Integer(compute="_compute_metrics")
    employees_active = fields.Integer(compute="_compute_metrics")
    employees_on_vacation = fields.Integer(compute="_compute_metrics")
    employees_on_special_permit = fields.Integer(compute="_compute_metrics")
    employees_sick = fields.Integer(compute="_compute_metrics")
    employees_resigned = fields.Integer(compute="_compute_metrics")
    employees_terminated = fields.Integer(compute="_compute_metrics")
    visas_expiring_30 = fields.Integer(compute="_compute_metrics")
    visas_expiring_60 = fields.Integer(compute="_compute_metrics")
    visas_expiring_90 = fields.Integer(compute="_compute_metrics")
    held_payslips = fields.Integer(compute="_compute_metrics")
    pending_adjustments = fields.Integer(compute="_compute_metrics")
    flights_open = fields.Integer(compute="_compute_metrics")
    flight_cost_total = fields.Monetary(
        compute="_compute_metrics", currency_field="currency_id"
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.ref("base.AED")
    )

    def _compute_metrics(self):
        Employee = self.env["hr.employee"].sudo()
        today = fields.Date.context_today(self)
        for rec in self:
            rec.employees_total = Employee.search_count([("active", "=", True)])
            rec.employees_active = Employee.search_count(
                [("active", "=", True), ("hr_uae_status", "=", "active")]
            )
            rec.employees_on_vacation = Employee.search_count(
                [("active", "=", True), ("hr_uae_status", "=", "vacations")]
            )
            rec.employees_on_special_permit = Employee.search_count(
                [("active", "=", True), ("hr_uae_status", "=", "special_permit")]
            )
            rec.employees_sick = Employee.search_count(
                [("active", "=", True), ("hr_uae_status", "=", "sick_leave")]
            )
            rec.employees_resigned = Employee.search_count(
                [("active", "=", True), ("hr_uae_status", "=", "resignation")]
            )
            rec.employees_terminated = Employee.search_count(
                [("active", "=", False), ("hr_uae_status", "=", "terminated")]
            )
            for days, fname in ((30, "visas_expiring_30"), (60, "visas_expiring_60"), (90, "visas_expiring_90")):
                rec[fname] = Employee.search_count(
                    [
                        ("active", "=", True),
                        ("visa_expire", ">=", today),
                        ("visa_expire", "<=", today + timedelta(days=days)),
                    ]
                )
            rec.held_payslips = self.env["hr.payslip"].sudo().search_count(
                [("hr_uae_hold_active", "=", True)]
            )
            rec.pending_adjustments = self.env["hr.uae.salary.adjustment"].sudo().search_count(
                [("state", "=", "to_approve")]
            )
            rec.flights_open = self.env["hr.uae.flight"].sudo().search_count(
                [("booking_state", "in", ("draft", "booked"))]
            )
            flights = self.env["hr.uae.flight"].sudo().search(
                [("booking_state", "in", ("booked", "completed"))]
            )
            rec.flight_cost_total = sum(flights.mapped("total"))

    @api.model
    def action_open_dashboard(self):
        rec = self.create({})
        return {
            "type": "ir.actions.act_window",
            "name": "HR UAE Dashboard",
            "res_model": "hr.uae.dashboard",
            "res_id": rec.id,
            "view_mode": "form",
            "target": "current",
        }

    # ---------- Live (Owl) dashboard data ----------

    @api.model
    def fetch_dashboard_data(self):
        """Aggregate everything the live JS dashboard needs in one round-trip."""
        Employee = self.env["hr.employee"].sudo()
        Payslip = self.env["hr.payslip"].sudo()
        Flight = self.env["hr.uae.flight"].sudo()
        Term = self.env["hr.uae.termination"].sudo()
        Doc = self.env["hr.uae.document"].sudo()
        Adj = self.env["hr.uae.salary.adjustment"].sudo()
        today = fields.Date.context_today(self)

        # KPI tiles
        kpis = {
            "employees_total": Employee.search_count([("active", "=", True)]),
            "employees_active": Employee.search_count(
                [("active", "=", True), ("hr_uae_status", "=", "active")]
            ),
            "employees_on_leave": Employee.search_count(
                [
                    ("active", "=", True),
                    (
                        "hr_uae_status",
                        "in",
                        ("vacations", "special_permit", "sick_leave"),
                    ),
                ]
            ),
            "employees_terminated": Employee.search_count(
                [("active", "=", False), ("hr_uae_status", "=", "terminated")]
            ),
            "visas_expiring_30": Employee.search_count(
                [
                    ("active", "=", True),
                    ("visa_expire", ">=", today),
                    ("visa_expire", "<=", today + timedelta(days=30)),
                ]
            ),
            "held_payslips": Payslip.search_count([("hr_uae_hold_active", "=", True)]),
            "pending_adjustments": Adj.search_count([("state", "=", "to_approve")]),
            "flights_open": Flight.search_count(
                [("booking_state", "in", ("draft", "booked"))]
            ),
            "documents_alerts": Doc.search_count(
                [("expiry_state", "in", ("warning", "expired"))]
            ),
        }

        # Status pie
        status_breakdown = []
        status_labels = {
            "active": "Active",
            "vacations": "Vacations",
            "special_permit": "Special Permit",
            "sick_leave": "Sick Leave",
            "resignation": "Resignation",
            "cancellation": "Cancellation",
            "terminated": "Terminated",
        }
        for code, label in status_labels.items():
            count = Employee.search_count(
                [
                    ("hr_uae_status", "=", code),
                    ("active", "in", (True, False)),
                ]
            )
            if count:
                status_breakdown.append({"label": label, "value": count})

        # Headcount per project allocation (top 8)
        self.env.cr.execute(
            """
            SELECT a.id, a.name, COUNT(e.id) AS n
              FROM hr_employee e
              JOIN account_analytic_account a
                ON a.id = e.project_allocation_id
             WHERE e.active IS TRUE
          GROUP BY a.id, a.name
          ORDER BY n DESC
             LIMIT 8
            """
        )
        per_project = [
            {"label": name, "value": n} for (_id, name, n) in self.env.cr.fetchall()
        ]

        # Flight cost per project (top 8) over the last 12 months
        self.env.cr.execute(
            """
            SELECT a.name, COALESCE(SUM(f.total), 0)
              FROM hr_uae_flight f
              LEFT JOIN account_analytic_account a
                ON a.id = f.project_allocation_id
             WHERE f.departure_date >= %s
               AND f.booking_state IN ('booked', 'completed')
          GROUP BY a.name
          ORDER BY 2 DESC
             LIMIT 8
            """,
            (today - timedelta(days=365),),
        )
        flight_per_project = [
            {"label": name or "(unassigned)", "value": float(amount)}
            for (name, amount) in self.env.cr.fetchall()
        ]

        # Recent payroll totals per month (last 6 months)
        self.env.cr.execute(
            """
            SELECT to_char(p.date_from, 'YYYY-MM') AS mo,
                   COUNT(p.id)             AS slips,
                   COALESCE(SUM(
                     CASE WHEN p.hr_uae_hold_active
                          THEN COALESCE(p.hr_uae_payable_now, 0)
                          ELSE COALESCE(c.wage, 0)
                     END
                   ), 0)                   AS total
              FROM hr_payslip p
              LEFT JOIN hr_contract c ON c.id = p.contract_id
             WHERE p.date_from >= %s
          GROUP BY mo
          ORDER BY mo
            """,
            (today - timedelta(days=210),),
        )
        payroll_trend = [
            {"label": mo, "slips": slips, "value": float(total)}
            for (mo, slips, total) in self.env.cr.fetchall()
        ]

        # Upcoming visa expiries (next 60 days, top 10)
        upcoming_visas = Employee.search_read(
            [
                ("active", "=", True),
                ("visa_expire", ">=", today),
                ("visa_expire", "<=", today + timedelta(days=60)),
            ],
            ["id", "name", "passport_id", "visa_expire", "project_allocation_id"],
            order="visa_expire asc",
            limit=10,
        )

        # Upcoming returns from leave (top 10)
        upcoming_returns = self.env["hr.leave"].sudo().search_read(
            [
                ("state", "=", "validate"),
                ("hr_uae_returned", "=", False),
                ("date_to", ">=", today),
            ],
            ["id", "employee_id", "holiday_status_id", "date_from", "date_to"],
            order="date_to asc",
            limit=10,
        )

        # Recent terminations (last 10)
        recent_terminations = Term.search_read(
            [],
            ["id", "name", "employee_id", "departure_date", "reason", "state"],
            order="departure_date desc",
            limit=10,
        )

        currency = self.env.ref("base.AED").sudo()
        return {
            "kpis": kpis,
            "status_breakdown": status_breakdown,
            "per_project": per_project,
            "flight_per_project": flight_per_project,
            "payroll_trend": payroll_trend,
            "upcoming_visas": upcoming_visas,
            "upcoming_returns": upcoming_returns,
            "recent_terminations": recent_terminations,
            "currency": {
                "id": currency.id,
                "name": currency.name,
                "symbol": currency.symbol or "AED",
                "position": currency.position or "after",
            },
            "today": fields.Date.to_string(today),
        }

    @api.model
    def action_open_live_dashboard(self):
        return {
            "type": "ir.actions.client",
            "tag": "hr_uae_live_dashboard",
            "name": "HR UAE Live Dashboard",
            "target": "current",
        }
