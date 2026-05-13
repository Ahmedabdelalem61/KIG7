from datetime import timedelta

from odoo import api, fields, models


class HrUaePayrollLiveDashboard(models.AbstractModel):
    """Server-side data provider for the modern Owl Payroll dashboard."""

    _name = "hr.uae.payroll.live.dashboard"
    _description = "HR UAE Payroll Live Dashboard"

    @api.model
    def fetch_data(self, options=None):
        options = options or {}
        today = fields.Date.context_today(self)
        # Default window: last 6 months
        months_back = int(options.get("months_back") or 6)
        date_from = (today.replace(day=1)) - timedelta(days=months_back * 31)

        Payslip = self.env["hr.payslip"].sudo()
        Adj = self.env["hr.uae.salary.adjustment"].sudo()

        # ---- Headline KPIs ----
        held_slips = Payslip.search([("hr_uae_hold_active", "=", True)])
        kpis = {
            "slips_total": Payslip.search_count([("date_from", ">=", date_from)]),
            "slips_done": Payslip.search_count(
                [("date_from", ">=", date_from), ("state", "=", "done")]
            ),
            "slips_draft": Payslip.search_count(
                [("date_from", ">=", date_from), ("state", "in", ("draft", "verify"))]
            ),
            "slips_on_hold": len(held_slips),
            "held_amount": sum(held_slips.mapped("hr_uae_held_amount") or [0.0]),
            "pending_adjustments": Adj.search_count([("state", "=", "to_approve")]),
            "active_employees": self.env["hr.employee"].sudo().search_count(
                [("active", "=", True)]
            ),
        }

        # ---- Monthly trend (12 months) from the dashboard SQL view ----
        self.env.cr.execute(
            """
            SELECT to_char(date_from, 'YYYY-MM') AS mo,
                   COUNT(*)                      AS slips,
                   COALESCE(SUM(total_to_pay),0) AS net,
                   COALESCE(SUM(deduction),0)    AS deductions,
                   COALESCE(SUM(extra_payment),0)AS extras,
                   COALESCE(SUM(held_amount),0)  AS held
              FROM hr_uae_payroll_dashboard
             WHERE date_from >= %s
          GROUP BY mo
          ORDER BY mo
            """,
            (today - timedelta(days=370),),
        )
        monthly_trend = [
            {
                "label": mo,
                "slips": int(slips),
                "net": float(net),
                "deductions": float(deductions),
                "extras": float(extras),
                "held": float(held),
            }
            for (mo, slips, net, deductions, extras, held) in self.env.cr.fetchall()
        ]

        # ---- Net pay by project (last 6 months, top 8) ----
        self.env.cr.execute(
            """
            SELECT a.id                              AS project_id,
                   COALESCE(a.name->>'en_US', '(unassigned)') AS proj,
                   COALESCE(SUM(d.total_to_pay),0)  AS net,
                   COUNT(*)                          AS slips
              FROM hr_uae_payroll_dashboard d
              LEFT JOIN account_analytic_account a
                ON a.id = d.project_allocation_id
             WHERE d.date_from >= %s
          GROUP BY a.id, proj
          ORDER BY net DESC
             LIMIT 8
            """,
            (date_from,),
        )
        net_by_project = [
            {
                "label": proj,
                "value": float(net),
                "slips": int(slips),
                "project_id": project_id,
            }
            for (project_id, proj, net, slips) in self.env.cr.fetchall()
        ]

        # ---- Salary rule breakdown for last completed month ----
        self.env.cr.execute(
            """
            SELECT to_char(p.date_from, 'YYYY-MM')
              FROM hr_payslip p
             WHERE p.state = 'done'
          ORDER BY p.date_from DESC
             LIMIT 1
            """
        )
        row = self.env.cr.fetchone()
        last_month_label = row[0] if row else None
        rule_breakdown = []
        if last_month_label:
            self.env.cr.execute(
                """
                SELECT sr.name->>'en_US' AS rule_name,
                       sr.code           AS code,
                       SUM(pl.total)     AS total
                  FROM hr_payslip_line pl
                  JOIN hr_payslip p     ON p.id = pl.slip_id
                  JOIN hr_salary_rule sr ON sr.id = pl.salary_rule_id
                 WHERE to_char(p.date_from, 'YYYY-MM') = %s
              GROUP BY sr.id, sr.name, sr.code
              ORDER BY ABS(SUM(pl.total)) DESC
                 LIMIT 12
                """,
                (last_month_label,),
            )
            rule_breakdown = [
                {"label": name or code, "code": code, "value": float(total)}
                for (name, code, total) in self.env.cr.fetchall()
            ]

        # ---- Top earners (last completed month, top 10) ----
        top_earners = []
        if last_month_label:
            self.env.cr.execute(
                """
                SELECT d.payslip_id, d.employee_id, d.employee_name,
                       d.project_allocation_id, d.total_to_pay
                  FROM hr_uae_payroll_dashboard d
                 WHERE to_char(d.date_from, 'YYYY-MM') = %s
              ORDER BY d.total_to_pay DESC
                 LIMIT 10
                """,
                (last_month_label,),
            )
            top_earners = [
                {
                    "payslip_id": pid,
                    "employee_id": eid,
                    "employee_name": name,
                    "project_id": proj,
                    "total_to_pay": float(total),
                }
                for (pid, eid, name, proj, total) in self.env.cr.fetchall()
            ]

        # ---- Held payslips list (top 15, oldest first) ----
        held_list = held_slips.sorted(lambda s: s.date_from)[:15]
        held_payslips = [
            {
                "id": s.id,
                "employee_id": s.employee_id.id,
                "employee_name": s.employee_id.name,
                "date_from": fields.Date.to_string(s.date_from),
                "date_to": fields.Date.to_string(s.date_to),
                "held_amount": float(s.hr_uae_held_amount or 0.0),
                "payable_now": float(s.hr_uae_payable_now or 0.0),
            }
            for s in held_list
        ]

        # ---- Pending salary adjustments (top 15) ----
        pending_adj = Adj.search(
            [("state", "=", "to_approve")],
            order="date_from desc",
            limit=15,
        )
        adjustments = [
            {
                "id": a.id,
                "employee_name": a.employee_id.name,
                "kind": a.kind,
                "mode": a.mode,
                "amount": float(a.amount),
                "period_from": fields.Date.to_string(a.date_from)
                if a.date_from
                else False,
                "period_to": fields.Date.to_string(a.date_to)
                if a.date_to
                else False,
            }
            for a in pending_adj
        ]

        currency = self.env.ref("base.AED").sudo()
        return {
            "kpis": kpis,
            "monthly_trend": monthly_trend,
            "net_by_project": net_by_project,
            "rule_breakdown": rule_breakdown,
            "top_earners": top_earners,
            "held_payslips": held_payslips,
            "adjustments": adjustments,
            "last_month_label": last_month_label,
            "today": fields.Date.to_string(today),
            "currency": {
                "id": currency.id,
                "name": currency.name,
                "symbol": currency.symbol or "AED",
                "position": currency.position or "after",
            },
        }

    @api.model
    def action_open_live_dashboard(self):
        return {
            "type": "ir.actions.client",
            "tag": "hr_uae_payroll_live_dashboard",
            "name": "HR UAE - Payroll Live Dashboard",
            "target": "current",
        }
