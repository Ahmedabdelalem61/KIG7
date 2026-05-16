from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


HR_UAE_STATUS_SELECTION = [
    ("active", "Active"),
    ("vacations", "Vacations"),
    ("special_permit", "Special Permit"),
    ("sick_leave", "Sick Leave"),
    ("resignation", "Resignation"),
    ("cancellation", "Cancellation"),
    ("terminated", "Terminated"),
]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    rank_id = fields.Many2one(
        "hr.uae.rank",
        string="Rank",
        tracking=True,
    )
    passport_expiry = fields.Date(string="Passport Expiry", tracking=True)
    roster = fields.Char(string="Roster", index=True, tracking=True)
    position_id = fields.Many2one(
        "hr.uae.position",
        string="Position",
        tracking=True,
    )
    project_allocation_id = fields.Many2one(
        "account.analytic.account",
        string="Project Allocation",
        domain=lambda self: self._project_allocation_domain(),
        tracking=True,
    )
    cost_center_id = fields.Many2one(
        "account.analytic.account",
        string="Cost Center",
        domain=lambda self: self._cost_center_domain(),
        tracking=True,
        copy=False,
    )
    location_id = fields.Many2one(
        "res.country",
        string="Location",
        tracking=True,
    )
    age = fields.Integer(
        string="Age",
        compute="_compute_age",
        store=True,
    )
    time_of_service = fields.Char(
        string="Time of Service",
        compute="_compute_time_of_service",
    )
    visa_status = fields.Selection(
        selection=[
            ("active", "Active Visa"),
            ("about_to_expire", "About to Expire"),
            ("expired", "Expired"),
            ("none", "Not Set"),
        ],
        string="Visa Status",
        compute="_compute_visa_status",
        store=True,
    )
    hr_uae_status = fields.Selection(
        selection=HR_UAE_STATUS_SELECTION,
        string="UAE Status",
        compute="_compute_hr_uae_status",
        store=True,
        readonly=False,
        tracking=True,
        help="Computed from active leaves and contract state. "
        "Set 'Manual override' to lock the value.",
    )
    hr_uae_status_manual = fields.Boolean(
        string="Manual Status Override",
        help="If set, the UAE Status above will not be auto-recomputed.",
        tracking=True,
    )
    contract_wage = fields.Monetary(
        string="Contract Wage",
        related="contract_id.wage",
        currency_field="currency_id",
        readonly=True,
    )
    housing_allowance = fields.Monetary(
        string="Housing Allowance",
        related="contract_id.housing_allowance",
        currency_field="currency_id",
        readonly=True,
    )
    transportation_allowance = fields.Monetary(
        string="Transportation Allowance",
        related="contract_id.transportation_allowance",
        currency_field="currency_id",
        readonly=True,
    )
    other_allowances = fields.Monetary(
        string="Other Allowances",
        related="contract_id.other_allowances",
        currency_field="currency_id",
        readonly=True,
    )
    annual_ticket_amount = fields.Monetary(
        string="Annual Ticket Amount",
        related="contract_id.annual_ticket_amount",
        currency_field="currency_id",
        readonly=True,
    )

    # ---------- Domains ----------

    @api.model
    def _project_allocation_plan_xmlid(self):
        return "hr_uae_master_data.account_analytic_plan_project_allocation"

    @api.model
    def _cost_center_plan_xmlid(self):
        return "hr_uae_master_data.account_analytic_plan_cost_center"

    @api.model
    def _project_allocation_domain(self):
        plan = self.env.ref(self._project_allocation_plan_xmlid(), raise_if_not_found=False)
        return [("plan_id", "=", plan.id)] if plan else []

    @api.model
    def _cost_center_domain(self):
        plan = self.env.ref(self._cost_center_plan_xmlid(), raise_if_not_found=False)
        return [("plan_id", "=", plan.id)] if plan else []

    # ---------- Computes ----------

    @api.depends("birthday")
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for emp in self:
            if emp.birthday:
                emp.age = relativedelta(today, emp.birthday).years
            else:
                emp.age = 0

    @api.depends("first_contract_date")
    def _compute_time_of_service(self):
        today = fields.Date.context_today(self)
        for emp in self:
            if emp.first_contract_date:
                delta = relativedelta(today, emp.first_contract_date)
                emp.time_of_service = _(
                    "%(years)s Years, %(months)s Months, %(days)s Days",
                    years=delta.years,
                    months=delta.months,
                    days=delta.days,
                )
            else:
                emp.time_of_service = ""

    @api.depends("visa_expire")
    def _compute_visa_status(self):
        today = fields.Date.context_today(self)
        for emp in self:
            if not emp.visa_expire:
                emp.visa_status = "none"
            elif emp.visa_expire < today:
                emp.visa_status = "expired"
            elif (emp.visa_expire - today).days <= 30:
                emp.visa_status = "about_to_expire"
            else:
                emp.visa_status = "active"

    @api.depends(
        "active",
        "contract_id",
        "contract_id.state",
        "contract_id.kanban_state",
    )
    def _compute_hr_uae_status(self):
        """Status derived from active leaves and contract state.

        Manual overrides win: if `hr_uae_status_manual` is set we keep the
        existing value untouched.
        """
        today = fields.Date.context_today(self)
        Leave = self.env["hr.leave"].sudo()
        for emp in self:
            if emp.hr_uae_status_manual:
                continue
            if not emp.active:
                emp.hr_uae_status = "terminated"
                continue
            current_leave = Leave.search(
                [
                    ("employee_id", "=", emp.id),
                    ("state", "=", "validate"),
                    ("date_from", "<=", today),
                    ("date_to", ">=", today),
                ],
                limit=1,
            )
            if current_leave:
                emp.hr_uae_status = self._map_leave_to_status(current_leave)
                continue
            contract = emp.contract_id
            if contract and contract.state == "close":
                emp.hr_uae_status = "resignation"
            elif contract and contract.state == "cancel":
                emp.hr_uae_status = "cancellation"
            else:
                emp.hr_uae_status = "active"

    @api.model
    def _map_leave_to_status(self, leave):
        """Map a leave type to a UAE status. Override hooks read leave_type code."""
        leave_type = leave.holiday_status_id
        code = (leave_type.hr_uae_status_code or "").strip() if hasattr(leave_type, "hr_uae_status_code") else ""
        if code:
            return code
        name = (leave_type.name or "").lower()
        if "sick" in name or "medical" in name:
            return "sick_leave"
        if "special" in name:
            return "special_permit"
        return "vacations"

    # ---------- Cost-center auto-creation ----------

    def _ensure_cost_center(self):
        plan = self.env.ref(self._cost_center_plan_xmlid(), raise_if_not_found=False)
        if not plan:
            return
        Analytic = self.env["account.analytic.account"].sudo()
        for emp in self:
            if emp.cost_center_id:
                continue
            existing = Analytic.search(
                [("plan_id", "=", plan.id), ("name", "=", emp.name or _("New Employee"))],
                limit=1,
            )
            if existing:
                emp.cost_center_id = existing.id
            else:
                emp.cost_center_id = Analytic.create(
                    {
                        "name": emp.name or _("New Employee"),
                        "plan_id": plan.id,
                        "company_id": emp.company_id.id,
                    }
                ).id

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        employees._ensure_cost_center()
        return employees

    def write(self, vals):
        result = super().write(vals)
        if "name" in vals:
            for emp in self:
                if emp.cost_center_id and emp.cost_center_id.name != emp.name:
                    emp.cost_center_id.sudo().name = emp.name
        if "active" in vals:
            for emp in self.filtered(lambda e: not e.active and e.cost_center_id):
                emp.cost_center_id.sudo().active = False
        return result

    @api.model
    def _hr_uae_recompute_status_cron(self):
        """Daily cron entrypoint - recompute UAE status for all employees that
        do not have manual override on."""
        emps = self.search([("hr_uae_status_manual", "=", False), ("active", "=", True)])
        emps._compute_hr_uae_status()
        emps.flush_recordset(["hr_uae_status"])
        return True
