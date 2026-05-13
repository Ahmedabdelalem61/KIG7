from odoo import api, fields, models, tools


class HrUaeMovementTracking(models.Model):
    """Read-only union of relevant employee movements.

    Combines:
      * Validated leaves (vacations / special permits / sick / unpaid)
      * Contract end dates (resignation / termination)
      * Project allocation transfers (from audit log)
    """

    _name = "hr.uae.movement.tracking"
    _description = "Employee Movement Tracking"
    _auto = False
    _order = "movement_date desc, employee_id"

    employee_id = fields.Many2one("hr.employee", readonly=True)
    movement_type = fields.Selection(
        [
            ("vacation", "Vacation"),
            ("special_permit", "Special Permit"),
            ("sick_leave", "Sick Leave"),
            ("unpaid_leave", "Unpaid Leave"),
            ("contract_end", "Contract End"),
            ("project_transfer", "Project Transfer"),
        ],
        readonly=True,
    )
    movement_date = fields.Date(readonly=True)
    return_date = fields.Date(readonly=True)
    notes = fields.Char(readonly=True)
    project_allocation_id = fields.Many2one(
        "account.analytic.account", readonly=True
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                /* Leaves */
                SELECT
                    (l.id::bigint * 10 + 1) AS id,
                    l.employee_id           AS employee_id,
                    CASE
                        WHEN lt.hr_uae_status_code = 'vacations'      THEN 'vacation'
                        WHEN lt.hr_uae_status_code = 'special_permit' THEN 'special_permit'
                        WHEN lt.hr_uae_status_code = 'sick_leave'     THEN 'sick_leave'
                        WHEN lt.hr_uae_unpaid                         THEN 'unpaid_leave'
                        ELSE 'vacation'
                    END                     AS movement_type,
                    l.date_from::date       AS movement_date,
                    l.date_to::date         AS return_date,
                    lt.name->>'en_US'       AS notes,
                    NULL::int               AS project_allocation_id
                FROM hr_leave l
                JOIN hr_leave_type lt ON lt.id = l.holiday_status_id
                WHERE l.state = 'validate'

                UNION ALL

                /* Contract ends */
                SELECT
                    (c.id::bigint * 10 + 2) AS id,
                    c.employee_id           AS employee_id,
                    'contract_end'          AS movement_type,
                    c.date_end              AS movement_date,
                    c.date_end              AS return_date,
                    c.name                  AS notes,
                    NULL::int               AS project_allocation_id
                FROM hr_contract c
                WHERE c.date_end IS NOT NULL
                  AND c.state IN ('close','cancel')

                UNION ALL

                /* Project transfers from audit log */
                SELECT
                    (a.id::bigint * 10 + 3)         AS id,
                    a.employee_id                   AS employee_id,
                    'project_transfer'              AS movement_type,
                    a.change_date::date             AS movement_date,
                    a.change_date::date             AS return_date,
                    'From: ' || COALESCE(a.old_display, '-') ||
                        '  To: ' || COALESCE(a.new_display, '-') AS notes,
                    NULL::int                       AS project_allocation_id
                FROM hr_uae_audit_log a
                WHERE a.field_name = 'project_allocation_id'
                  AND a.change_type = 'write'
                  AND a.employee_id IS NOT NULL
            );
            """
        )
