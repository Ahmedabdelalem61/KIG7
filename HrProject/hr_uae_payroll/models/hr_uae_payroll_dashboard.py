from odoo import api, fields, models, tools


class HrUaePayrollDashboard(models.Model):
    """Read-only dashboard reproducing the Payroll Excel table from the proposal."""

    _name = "hr.uae.payroll.dashboard"
    _description = "Payroll Dashboard Row"
    _auto = False
    _order = "date_from desc, employee_id"

    payslip_id = fields.Many2one("hr.payslip", readonly=True)
    employee_id = fields.Many2one("hr.employee", readonly=True)
    rank_id = fields.Many2one("hr.uae.rank", readonly=True)
    employee_name = fields.Char(readonly=True)
    passport_id = fields.Char(readonly=True)
    roster = fields.Char(readonly=True)
    position_id = fields.Many2one("hr.uae.position", readonly=True)
    project_allocation_id = fields.Many2one("account.analytic.account", readonly=True)
    location_id = fields.Many2one("res.country", readonly=True)
    hr_uae_status = fields.Char(readonly=True)
    salary = fields.Float(readonly=True)
    date_from = fields.Date(readonly=True)
    date_to = fields.Date(readonly=True)
    total_days = fields.Integer(readonly=True)
    worked_days = fields.Float(readonly=True)
    deducted_days = fields.Float(readonly=True)
    extra_payment = fields.Float(readonly=True)
    bonus = fields.Float(readonly=True)
    held_amount = fields.Float(readonly=True)
    deduction = fields.Float(readonly=True)
    total_to_pay = fields.Float(readonly=True)
    notes = fields.Char(readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verify", "Waiting"),
            ("done", "Done"),
            ("cancel", "Rejected"),
            ("on_hold", "On Hold"),
        ],
        readonly=True,
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    p.id                                   AS id,
                    p.id                                   AS payslip_id,
                    p.employee_id                          AS employee_id,
                    e.rank_id                              AS rank_id,
                    e.name                                 AS employee_name,
                    e.passport_id                          AS passport_id,
                    e.roster                               AS roster,
                    e.position_id                          AS position_id,
                    e.project_allocation_id                AS project_allocation_id,
                    e.location_id                          AS location_id,
                    e.hr_uae_status                        AS hr_uae_status,
                    COALESCE(c.wage, 0.0)                  AS salary,
                    p.date_from                            AS date_from,
                    p.date_to                              AS date_to,
                    (p.date_to - p.date_from + 1)          AS total_days,
                    COALESCE((
                        SELECT SUM(wd.number_of_days)
                        FROM hr_payslip_worked_days wd
                        WHERE wd.payslip_id = p.id
                    ), 0.0)                                AS worked_days,
                    GREATEST(
                        (p.date_to - p.date_from + 1) - COALESCE((
                            SELECT SUM(wd.number_of_days)
                            FROM hr_payslip_worked_days wd
                            WHERE wd.payslip_id = p.id
                        ), 0.0)
                    , 0.0)                                 AS deducted_days,
                    COALESCE((
                        SELECT SUM(pl.total)
                        FROM hr_payslip_line pl
                        JOIN hr_salary_rule sr ON sr.id = pl.salary_rule_id
                        WHERE pl.slip_id = p.id
                          AND sr.code = 'ADJUSTMENTS'
                          AND pl.total > 0
                    ), 0.0)                                AS extra_payment,
                    0.0                                    AS bonus,
                    COALESCE(p.hr_uae_held_amount, 0.0)    AS held_amount,
                    COALESCE((
                        SELECT ABS(SUM(pl.total))
                        FROM hr_payslip_line pl
                        JOIN hr_salary_rule sr ON sr.id = pl.salary_rule_id
                        JOIN hr_salary_rule_category rc2 ON rc2.id = sr.category_id
                        WHERE pl.slip_id = p.id AND rc2.code = 'DED'
                    ), 0.0)                                AS deduction,
                    CASE
                        WHEN p.hr_uae_hold_active
                            THEN COALESCE(p.hr_uae_payable_now, 0.0)
                        ELSE COALESCE((
                            SELECT pl.total
                            FROM hr_payslip_line pl
                            JOIN hr_salary_rule sr ON sr.id = pl.salary_rule_id
                            WHERE pl.slip_id = p.id AND sr.code = 'NET'
                            LIMIT 1
                        ), c.wage, 0.0)
                    END                                    AS total_to_pay,
                    p.note                                 AS notes,
                    p.state                                AS state
                FROM hr_payslip p
                JOIN hr_employee e ON e.id = p.employee_id
                LEFT JOIN hr_contract c ON c.id = p.contract_id
            );
            """
        )
