import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

DEFAULT_EXCLUDED = {
    "write_date",
    "write_uid",
    "create_date",
    "create_uid",
    "__last_update",
    "message_main_attachment_id",
    "message_ids",
    "message_follower_ids",
    "message_partner_ids",
    "message_attachment_count",
    "message_has_error",
    "message_has_error_counter",
    "message_has_sms_error",
    "message_needaction",
    "message_needaction_counter",
    "message_unread",
    "message_unread_counter",
    "activity_ids",
    "activity_state",
    "activity_user_id",
    "activity_type_id",
    "activity_date_deadline",
    "activity_summary",
    "activity_exception_decoration",
    "activity_exception_icon",
    "access_token",
    "access_url",
    "access_warning",
}


class HrUaeAuditMixin(models.AbstractModel):
    """Mixin that auto-logs field-level create/write/unlink to ``hr.uae.audit.log``.

    Models that want auditing add this mixin to their ``_inherit`` list.
    Records can opt-out per call via ``with_context(hr_uae_skip_audit=True)``.
    """

    _name = "hr.uae.audit.mixin"
    _description = "HR UAE Audit Mixin"

    # ---------- Hooks subclasses can override ----------

    def _hr_uae_audit_employee_id(self):
        self.ensure_one()
        if self._name == "hr.employee":
            return self
        for fname in ("employee_id", "employee", "emp_id"):
            field = self._fields.get(fname)
            if field and field.type == "many2one" and field.comodel_name == "hr.employee":
                return self[fname]
        return self.env["hr.employee"].browse()

    def _hr_uae_audit_excluded_fields(self):
        explicit = set(getattr(self, "_hr_uae_audit_extra_excluded", ()) or ())
        return DEFAULT_EXCLUDED | explicit

    def _hr_uae_audit_field_label(self, field_name):
        field = self._fields.get(field_name)
        return field.string if field else field_name

    def _hr_uae_audit_format(self, field, value):
        if value in (None, False) and field.type != "boolean":
            return ""
        if field.type == "boolean":
            return _("Yes") if value else _("No")
        if field.type == "many2one":
            if isinstance(value, models.BaseModel):
                return value.display_name or ""
            try:
                rec = self.env[field.comodel_name].browse(int(value))
                return rec.display_name or str(value)
            except Exception:
                return str(value)
        if field.type in ("many2many", "one2many"):
            if isinstance(value, models.BaseModel):
                return ", ".join(value.mapped("display_name"))
            return str(value)
        if field.type == "selection":
            try:
                selection = dict(field._description_selection(self.env))
            except Exception:
                selection = dict(field.selection or [])
            return str(selection.get(value, value))
        if field.type == "date":
            return fields.Date.to_string(value) or ""
        if field.type == "datetime":
            return fields.Datetime.to_string(value) or ""
        if field.type == "monetary":
            return "%.2f" % float(value)
        if field.type == "binary":
            return _("(binary)")
        return str(value)

    # ---------- Logging primitive ----------

    def _hr_uae_log(self, field_name, field_label, old_disp, new_disp, change_type):
        self.ensure_one()
        emp = self._hr_uae_audit_employee_id()
        try:
            self.env["hr.uae.audit.log"].sudo().create(
                {
                    "model": self._name,
                    "res_id": self.id,
                    "employee_id": emp.id if emp else False,
                    "field_name": field_name or "",
                    "field_label": field_label or "",
                    "old_display": old_disp or "",
                    "new_display": new_disp or "",
                    "change_type": change_type,
                }
            )
        except Exception:
            _logger.exception(
                "hr_uae_audit_trail: failed to log %s on %s/%s",
                change_type,
                self._name,
                self.id,
            )

    # ---------- ORM overrides ----------

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if self.env.context.get("hr_uae_skip_audit"):
            return records
        for rec in records:
            rec._hr_uae_log(
                "",
                _("Record Created"),
                "",
                rec.display_name or "",
                "create",
            )
        return records

    def write(self, vals):
        if not vals or self.env.context.get("hr_uae_skip_audit"):
            return super().write(vals)
        excluded = self._hr_uae_audit_excluded_fields()
        tracked_keys = [
            k for k in vals if k in self._fields and k not in excluded
        ]
        if not tracked_keys:
            return super().write(vals)
        snapshots = {}
        for rec in self:
            snapshots[rec.id] = {k: rec[k] for k in tracked_keys}
        result = super().write(vals)
        for rec in self:
            old_data = snapshots.get(rec.id, {})
            for fname in tracked_keys:
                old_val = old_data.get(fname)
                new_val = rec[fname]
                if old_val == new_val:
                    continue
                field = rec._fields[fname]
                rec._hr_uae_log(
                    fname,
                    rec._hr_uae_audit_field_label(fname),
                    rec._hr_uae_audit_format(field, old_val),
                    rec._hr_uae_audit_format(field, new_val),
                    "write",
                )
        return result

    def unlink(self):
        if not self.env.context.get("hr_uae_skip_audit"):
            for rec in self:
                rec._hr_uae_log(
                    "",
                    _("Record Deleted"),
                    rec.display_name or "",
                    "",
                    "unlink",
                )
        return super().unlink()
