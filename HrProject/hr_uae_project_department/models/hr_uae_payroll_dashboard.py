from odoo import fields, models, tools


class HrUaePayrollDashboard(models.Model):
    _inherit = "hr.uae.payroll.dashboard"

    department_id = fields.Many2one("hr.department", string="Project", readonly=True)

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
                    e.department_id                        AS department_id,
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
