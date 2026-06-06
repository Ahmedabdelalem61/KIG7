from datetime import timedelta

from odoo import api, fields, models


class HrUaeDashboard(models.TransientModel):
    _inherit = "hr.uae.dashboard"

    @api.model
    def fetch_dashboard_data(self):
        data = super().fetch_dashboard_data()
        today = fields.Date.context_today(self)

        self.env.cr.execute(
            """
            SELECT d.id,
                   COALESCE(d.name->>'en_US', '(unassigned)') AS project_name,
                   COUNT(e.id) AS n
              FROM hr_employee e
              JOIN hr_department d ON d.id = e.department_id
             WHERE e.active IS TRUE
          GROUP BY d.id, project_name
          ORDER BY n DESC
             LIMIT 8
            """
        )
        data["per_project"] = [
            {"project_id": project_id, "label": name, "value": count}
            for (project_id, name, count) in self.env.cr.fetchall()
        ]

        self.env.cr.execute(
            """
            SELECT d.id,
                   COALESCE(d.name->>'en_US', '(unassigned)') AS project_name,
                   COALESCE(SUM(f.total), 0) AS amount
              FROM hr_uae_flight f
              LEFT JOIN hr_department d ON d.id = f.department_id
             WHERE f.departure_date >= %s
               AND f.booking_state IN ('booked', 'completed')
          GROUP BY d.id, project_name
          ORDER BY amount DESC
             LIMIT 8
            """,
            (today - timedelta(days=365),),
        )
        data["flight_per_project"] = [
            {
                "project_id": project_id,
                "label": name or "(unassigned)",
                "value": float(amount),
            }
            for (project_id, name, amount) in self.env.cr.fetchall()
        ]

        data["upcoming_visas"] = self.env["hr.employee"].sudo().search_read(
            [
                ("active", "=", True),
                ("visa_expire", ">=", today),
                ("visa_expire", "<=", today + timedelta(days=60)),
            ],
            ["id", "name", "passport_id", "visa_expire", "department_id"],
            order="visa_expire asc",
            limit=10,
        )
        return data
