import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Predefined template specification.
#
# Each entry seeds one `hr.uae.xlsx.template` plus its lines from plain field
# *names* (resolved against ir.model.fields at install time). Fields that do
# not exist on the target model are skipped with a warning, so the seed stays
# safe even if an optional module is absent.
#
# Per-field options:
#   required   -> required on import (create path)
#   match_key  -> used as a fallback key to find an existing record on update
#                 when no technical ID column is present
#   ref_only   -> exported for reference but never imported (related/computed)
# ---------------------------------------------------------------------------
PREDEFINED_TEMPLATES = [
    {
        "code": "employees",
        "name": "Employees",
        "model": "hr.employee",
        "sequence": 10,
        "note": "Employee master data. Re-import the exported file (keep the ID "
        "column) to update existing employees. Rows without an ID create new "
        "employees. Blank cells are left unchanged on update.",
        "fields": [
            ("name", {"required": True}),
            ("passport_id", {"match_key": True}),
            ("identification_id", {}),
            ("work_email", {}),
            ("work_phone", {}),
            ("mobile_phone", {}),
            ("job_title", {}),
            ("gender", {}),
            ("birthday", {}),
            ("marital", {}),
            ("country_id", {}),
            ("rank_id", {}),
            ("position_id", {}),
            ("roster", {}),
            ("department_id", {}),
            ("project_allocation_id", {}),
            ("location_id", {}),
            ("visa_no", {}),
            ("visa_expire", {}),
            ("permit_no", {}),
            ("hr_uae_status", {}),
            ("hr_uae_status_manual", {}),
            ("active", {}),
            ("contract_wage", {"ref_only": True}),
            ("housing_allowance", {"ref_only": True}),
            ("transportation_allowance", {"ref_only": True}),
            ("other_allowances", {"ref_only": True}),
            ("annual_ticket_amount", {"ref_only": True}),
        ],
    },
    {
        "code": "contracts",
        "name": "Contracts",
        "model": "hr.contract",
        "sequence": 20,
        "note": "Employment contracts. Update existing contracts by keeping the "
        "ID column; new rows create contracts. Wage and allowances are monthly.",
        "fields": [
            ("name", {"required": True, "match_key": True}),
            ("employee_id", {"required": True, "match_key": True}),
            ("date_start", {"required": True}),
            ("date_end", {}),
            ("wage", {"required": True}),
            ("state", {}),
            ("struct_id", {}),
            ("housing_allowance", {}),
            ("transportation_allowance", {}),
            ("other_allowances", {}),
            ("annual_ticket_amount", {}),
            ("currency_id", {}),
        ],
    },
    {
        "code": "flights",
        "name": "Flight Tickets",
        "model": "hr.uae.flight",
        "sequence": 30,
        "note": "Flight tickets. The Reference is auto-generated for new rows. "
        "Use the ID column to update existing tickets.",
        "fields": [
            ("name", {"ref_only": True}),
            ("employee_id", {"required": True}),
            ("requested_date", {}),
            ("ticket_no", {"match_key": True}),
            ("from_country_id", {}),
            ("to_country_id", {}),
            ("ticket_price", {}),
            ("extra_charges", {}),
            ("currency_id", {"required": True}),
            ("departure_date", {}),
            ("departure_time", {}),
            ("arrival_date", {}),
            ("arrival_time", {}),
            ("purpose", {}),
            ("booking_state", {}),
            ("payment_mode", {"required": True}),
            ("agency", {}),
            ("refundable", {}),
            ("sent_ticket", {}),
            ("project_allocation_id", {}),
            ("notes", {}),
            ("total", {"ref_only": True}),
            ("passport_no", {"ref_only": True}),
            ("month", {"ref_only": True}),
        ],
    },
    {
        "code": "documents",
        "name": "Employee Documents",
        "model": "hr.uae.document",
        "sequence": 40,
        "note": "Employee documents (passport, visa, ...). Attachments are not "
        "handled by import. Update by keeping the ID column.",
        "fields": [
            ("name", {"required": True, "match_key": True}),
            ("document_type", {"required": True}),
            ("employee_id", {"required": True, "match_key": True}),
            ("issue_date", {}),
            ("expiry_date", {}),
            ("active", {}),
            ("note", {}),
            ("days_to_expiry", {"ref_only": True}),
            ("expiry_state", {"ref_only": True}),
        ],
    },
    {
        "code": "salary_adjustments",
        "name": "Salary Adjustments",
        "model": "hr.uae.salary.adjustment",
        "sequence": 50,
        "note": "Salary adjustments / allowances / deductions. The reference and "
        "workflow state are export-only; new rows start in Draft.",
        "fields": [
            ("name", {"ref_only": True}),
            ("employee_id", {"required": True}),
            ("kind", {"required": True}),
            ("amount", {"required": True}),
            ("currency_id", {"required": True}),
            ("mode", {"required": True}),
            ("target_payslip_id", {}),
            ("date_from", {}),
            ("date_to", {}),
            ("recurring_interval", {}),
            ("recurring_until", {}),
            ("notes", {}),
            ("state", {"ref_only": True}),
            ("last_applied_period", {"ref_only": True}),
        ],
    },
    {
        "code": "terminations",
        "name": "Terminations",
        "model": "hr.uae.termination",
        "sequence": 60,
        "note": "Contract terminations. The reference and workflow state are "
        "export-only; new rows start in Draft.",
        "fields": [
            ("name", {"ref_only": True}),
            ("employee_id", {"required": True}),
            ("contract_id", {}),
            ("reason", {}),
            ("departure_date", {}),
            ("arrival_date", {}),
            ("note", {}),
            ("state", {"ref_only": True}),
        ],
    },
    {
        "code": "payroll_dashboard",
        "name": "Payroll Dashboard",
        "model": "hr.uae.payroll.dashboard",
        "sequence": 70,
        "allow_import": False,
        "allow_create": False,
        "allow_update": False,
        "note": "Payroll dashboard is EXPORT ONLY. Import is disabled for payroll.",
        "fields": [
            ("employee_name", {}),
            ("rank_id", {}),
            ("passport_id", {}),
            ("roster", {}),
            ("position_id", {}),
            ("department_id", {}),
            ("project_allocation_id", {}),
            ("location_id", {}),
            ("hr_uae_status", {}),
            ("salary", {}),
            ("basic_amount", {}),
            ("net_amount", {}),
            ("date_from", {}),
            ("date_to", {}),
            ("total_days", {}),
            ("worked_days", {}),
            ("deducted_days", {}),
            ("extra_payment", {}),
            ("bonus", {}),
            ("held_amount", {}),
            ("deduction", {}),
            ("total_to_pay", {}),
            ("state", {}),
            ("notes", {}),
        ],
    },
]


class HrUaeXlsxTemplate(models.Model):
    _name = "hr.uae.xlsx.template"
    _description = "Excel Import/Export Template"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(
        required=True,
        copy=False,
        help="Unique technical code. Predefined templates use a fixed code so "
        "upgrades can find them.",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        help="Any Odoo model. Pick the fields to expose in the lines below.",
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model Name",
        store=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        "hr.uae.xlsx.template.line",
        "template_id",
        string="Fields",
        copy=True,
    )
    allow_export = fields.Boolean(string="Allow Export", default=True)
    allow_import = fields.Boolean(string="Allow Import", default=True)
    allow_create = fields.Boolean(
        string="Allow Create on Import",
        default=True,
        help="If unset, import can only update existing records, never create.",
    )
    allow_update = fields.Boolean(
        string="Allow Update on Import",
        default=True,
        help="If unset, import can only create new records, never update.",
    )
    is_predefined = fields.Boolean(
        string="Predefined",
        default=False,
        copy=False,
        help="Seeded by the module. Predefined templates can be edited but are "
        "re-created if deleted on upgrade.",
    )
    note = fields.Text(string="Instructions")

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The template code must be unique."),
    ]

    # ------------------------------------------------------------------ helpers

    @api.constrains("line_ids", "model_id")
    def _check_lines_model(self):
        for tpl in self:
            for line in tpl.line_ids:
                if line.field_id and line.field_id.model_id != tpl.model_id:
                    raise ValidationError(
                        _(
                            "Field '%(field)s' does not belong to model "
                            "'%(model)s'.",
                            field=line.field_id.name,
                            model=tpl.model_name,
                        )
                    )

    def get_model(self):
        self.ensure_one()
        return self.env[self.model_name]

    def export_line_ids(self):
        self.ensure_one()
        return self.line_ids.filtered(lambda line_record: line_record.for_export)

    def import_line_ids(self):
        """Lines that are actually written on import."""
        self.ensure_one()
        if not self.allow_import:
            return self.line_ids.browse()
        return self.line_ids.filtered(
            lambda line_record: line_record.for_import and not line_record.ref_only
        )

    def match_key_line_ids(self):
        self.ensure_one()
        return self.import_line_ids().filtered(lambda line_record: line_record.is_match_key)

    # ------------------------------------------------------------------ seeding

    @api.model
    def _seed_predefined_templates(self):
        """Create any missing predefined templates from PREDEFINED_TEMPLATES.

        Idempotent and non-destructive: existing templates (matched by code)
        are left untouched so user edits survive upgrades.
        """
        IrModel = self.env["ir.model"]
        IrField = self.env["ir.model.fields"]
        for spec in PREDEFINED_TEMPLATES:
            existing = self.with_context(active_test=False).search(
                [("code", "=", spec["code"])], limit=1
            )
            if existing:
                continue
            model = IrModel.search([("model", "=", spec["model"])], limit=1)
            if not model:
                _logger.info(
                    "hr_uae_xlsx_io: skip template %s, model %s not found",
                    spec["code"],
                    spec["model"],
                )
                continue
            line_cmds = []
            seq = 0
            for field_name, opts in spec["fields"]:
                field = IrField.search(
                    [("model", "=", spec["model"]), ("name", "=", field_name)],
                    limit=1,
                )
                if not field:
                    _logger.info(
                        "hr_uae_xlsx_io: skip field %s.%s (not found)",
                        spec["model"],
                        field_name,
                    )
                    continue
                seq += 10
                ref_only = bool(opts.get("ref_only"))
                line_cmds.append(
                    (
                        0,
                        0,
                        {
                            "sequence": seq,
                            "field_id": field.id,
                            "for_export": True,
                            "for_import": not ref_only,
                            "ref_only": ref_only,
                            "is_required": bool(opts.get("required")),
                            "is_match_key": bool(opts.get("match_key")),
                        },
                    )
                )
            self.create(
                {
                    "code": spec["code"],
                    "name": spec["name"],
                    "sequence": spec.get("sequence", 10),
                    "model_id": model.id,
                    "is_predefined": True,
                    "allow_export": spec.get("allow_export", True),
                    "allow_import": spec.get("allow_import", True),
                    "allow_create": spec.get("allow_create", True),
                    "allow_update": spec.get("allow_update", True),
                    "note": spec.get("note", ""),
                    "line_ids": line_cmds,
                }
            )
            _logger.info("hr_uae_xlsx_io: seeded template %s", spec["code"])
        return True


class HrUaeXlsxTemplateLine(models.Model):
    _name = "hr.uae.xlsx.template.line"
    _description = "Excel Import/Export Template Field"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "hr.uae.xlsx.template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    model_id = fields.Many2one(related="template_id.model_id", store=True)
    sequence = fields.Integer(default=10)
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
        domain="[('model_id', '=', model_id)]",
    )
    name = fields.Char(related="field_id.name", string="Technical Name", store=True)
    field_type = fields.Selection(related="field_id.ttype", string="Type", store=True)
    relation = fields.Char(related="field_id.relation", string="Relation", store=True)
    column_label = fields.Char(
        string="Column Label",
        help="Header shown in the Excel file. Defaults to the field label.",
    )
    for_export = fields.Boolean(string="Export", default=True)
    for_import = fields.Boolean(string="Import", default=True)
    ref_only = fields.Boolean(
        string="Reference Only",
        help="Exported for context but never written on import (computed / "
        "related / read-only fields).",
    )
    is_required = fields.Boolean(
        string="Required",
        help="Required when creating a record on import.",
    )
    is_match_key = fields.Boolean(
        string="Match Key",
        help="Used to find an existing record on import when no ID column is "
        "present.",
    )

    @api.onchange("field_id")
    def _onchange_field_id(self):
        if self.field_id and not self.column_label:
            self.column_label = self.field_id.field_description

    @api.onchange("ref_only")
    def _onchange_ref_only(self):
        if self.ref_only:
            self.for_import = False
            self.is_required = False
            self.is_match_key = False

    def label(self):
        self.ensure_one()
        return self.column_label or self.field_id.field_description or self.name
