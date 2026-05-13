from odoo import _, api, fields, models
from odoo.exceptions import UserError


PURPOSE_SELECTION = [
    ("hire", "Hire"),
    ("vacation", "Vacation"),
    ("special_permit", "Special Permit"),
    ("termination", "Termination"),
    ("medical", "Medical"),
    ("other", "Other"),
]

BOOKING_STATE_SELECTION = [
    ("draft", "Draft"),
    ("booked", "Booked"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("rescheduled", "Rescheduled"),
]


class HrUaeFlight(models.Model):
    _name = "hr.uae.flight"
    _description = "Flight Ticket"
    _inherit = ["mail.thread", "hr.uae.audit.mixin"]
    _order = "departure_date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        tracking=True,
        ondelete="restrict",
    )
    passport_no = fields.Char(related="employee_id.passport_id", store=True, readonly=True)
    date_of_joining = fields.Date(related="employee_id.first_contract_date", store=True, readonly=True)
    time_of_service = fields.Char(related="employee_id.time_of_service")
    date_of_birth = fields.Date(related="employee_id.birthday", store=True, readonly=True)

    requested_date = fields.Date(tracking=True)
    ticket_no = fields.Char(string="Ticket No.", tracking=True)
    from_country_id = fields.Many2one(
        "res.country", string="From", tracking=True, ondelete="restrict"
    )
    to_country_id = fields.Many2one(
        "res.country", string="To", tracking=True, ondelete="restrict"
    )
    ticket_price = fields.Monetary(
        currency_field="currency_id", tracking=True
    )
    extra_charges = fields.Monetary(
        currency_field="currency_id", tracking=True
    )
    total = fields.Monetary(
        compute="_compute_total",
        store=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.AED"),
        required=True,
    )

    departure_date = fields.Date(tracking=True)
    departure_time = fields.Char(string="Departure Time", tracking=True)
    arrival_date = fields.Date(tracking=True)
    arrival_time = fields.Char(string="Arrival Time", tracking=True)
    month = fields.Char(
        string="Month",
        compute="_compute_month",
        store=True,
    )

    sent_ticket = fields.Boolean(string="Sent Ticket", tracking=True)
    purpose = fields.Selection(
        PURPOSE_SELECTION, string="Purpose", default="hire", tracking=True
    )
    booking_state = fields.Selection(
        BOOKING_STATE_SELECTION,
        string="Booking Status",
        default="draft",
        tracking=True,
        copy=False,
    )
    agency = fields.Char(tracking=True)
    refundable = fields.Boolean(tracking=True)
    updated_master = fields.Boolean(string="Master Updated", tracking=True)
    notes = fields.Text()

    project_allocation_id = fields.Many2one(
        "account.analytic.account",
        string="Project Allocation",
        tracking=True,
    )

    payment_mode = fields.Selection(
        [
            ("company_account", "Paid by Company"),
            ("own_account", "Paid by Employee"),
        ],
        string="Paid By",
        default="company_account",
        tracking=True,
        required=True,
    )

    expense_id = fields.Many2one(
        "hr.expense",
        string="Linked Expense",
        readonly=True,
        copy=False,
    )

    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Ticket Files",
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    # ---------- Computes ----------

    @api.depends("ticket_price", "extra_charges")
    def _compute_total(self):
        for f in self:
            f.total = (f.ticket_price or 0.0) + (f.extra_charges or 0.0)

    @api.depends("departure_date")
    def _compute_month(self):
        for f in self:
            f.month = f.departure_date.strftime("%B") if f.departure_date else ""

    # ---------- Defaults / sync ----------

    @api.onchange("employee_id")
    def _onchange_employee(self):
        if self.employee_id:
            self.project_allocation_id = self.employee_id.project_allocation_id

    @api.model_create_multi
    def create(self, vals_list):
        Sequence = self.env["ir.sequence"].sudo()
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("New"):
                vals["name"] = Sequence.next_by_code("hr.uae.flight") or _("New")
        return super().create(vals_list)

    def _hr_uae_audit_employee_id(self):
        return self.employee_id

    # ---------- Workflow ----------

    def action_book(self):
        for f in self:
            if not f.employee_id:
                raise UserError(_("Set the employee before booking."))
            f.booking_state = "booked"
            f._sync_or_create_expense()

    def action_complete(self):
        for f in self:
            f.booking_state = "completed"

    def action_cancel(self):
        for f in self:
            f.booking_state = "cancelled"
            if f.expense_id and f.expense_id.state == "draft":
                f.expense_id.with_context(hr_uae_skip_audit=True).unlink()
                f.expense_id = False

    def action_reschedule(self):
        for f in self:
            f.booking_state = "rescheduled"

    def action_reset_to_draft(self):
        for f in self:
            f.booking_state = "draft"

    # ---------- Expense integration ----------

    def _flight_product(self):
        product = self.env.ref(
            "hr_uae_flights.product_flight_ticket", raise_if_not_found=False
        )
        if not product:
            raise UserError(
                _("Flight expense product missing. Please reinstall hr_uae_flights.")
            )
        return product

    def _prepare_expense_vals(self):
        self.ensure_one()
        product = self._flight_product()
        analytic = {}
        if self.project_allocation_id:
            analytic[str(self.project_allocation_id.id)] = 100.0
        return {
            "name": self.name + " - " + (self.employee_id.name or ""),
            "employee_id": self.employee_id.id,
            "product_id": product.id,
            "total_amount_currency": self.total,
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
            "payment_mode": self.payment_mode,
            "date": self.departure_date or fields.Date.context_today(self),
            "analytic_distribution": analytic or False,
        }

    def _sync_or_create_expense(self):
        for f in self.filtered(lambda r: r.total and r.employee_id):
            vals = f._prepare_expense_vals()
            if f.expense_id:
                f.expense_id.with_context(hr_uae_skip_audit=True).write(vals)
            else:
                f.expense_id = self.env["hr.expense"].create(vals).id
