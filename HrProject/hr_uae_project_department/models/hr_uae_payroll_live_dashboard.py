from datetime import timedelta

from odoo import api, fields, models


class HrUaePayrollLiveDashboard(models.AbstractModel):
    _inherit = "hr.uae.payroll.live.dashboard"

    @api.model
    def fetch_data(self, options=None):
        data = super().fetch_data(options=options)
        options = options or {}
        today = fields.Date.context_today(self)
        months_back = int(options.get("months_back") or 6)
        date_from = (today.replace(day=1)) - timedelta(days=months_back * 31)

        self.env.cr.execute(
            """
            SELECT dpt.id                              AS project_id,
                   COALESCE(dpt.name->>'en_US', '(unassigned)') AS project_name,
                   COALESCE(SUM(d.total_to_pay),0)    AS net,
                   COUNT(*)                            AS slips
              FROM hr_uae_payroll_dashboard d
              LEFT JOIN hr_department dpt
                ON dpt.id = d.department_id
             WHERE d.date_from >= %s
          GROUP BY dpt.id, project_name
          ORDER BY net DESC
             LIMIT 8
            """,
            (date_from,),
        )
        data["net_by_project"] = [
            {
                "label": project_name,
                "value": float(net),
                "slips": int(slips),
                "project_id": project_id,
            }
            for (project_id, project_name, net, slips) in self.env.cr.fetchall()
        ]

        last_month_label = data.get("last_month_label")
        if last_month_label:
            self.env.cr.execute(
                """
                SELECT d.payslip_id, d.employee_id, d.employee_name,
                       d.department_id, d.total_to_pay
                  FROM hr_uae_payroll_dashboard d
                 WHERE to_char(d.date_from, 'YYYY-MM') = %s
              ORDER BY d.total_to_pay DESC
                 LIMIT 10
                """,
                (last_month_label,),
            )
            data["top_earners"] = [
                {
                    "payslip_id": payslip_id,
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "project_id": department_id,
                    "total_to_pay": float(total_to_pay),
                }
                for (
                    payslip_id,
                    employee_id,
                    employee_name,
                    department_id,
                    total_to_pay,
                ) in self.env.cr.fetchall()
            ]
        return data
