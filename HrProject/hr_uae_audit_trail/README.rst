==================
HR UAE Audit Trail
==================

Field-level audit log for HR UAE records.

Features
========

* Reusable abstract mixin ``hr.uae.audit.mixin`` that any model can inherit
  to gain automatic ``create`` / ``write`` / ``unlink`` logging.
* Logs are stored in ``hr.uae.audit.log`` with old vs new value rendered
  human-readably (m2o -> ``display_name``, selection -> label, dates,
  monetary, booleans).
* Already applied to ``hr.employee`` and ``hr.contract``. Other ``hr_uae_*``
  modules apply it to their own models.
* Smart-button + ``Audit Trail`` tab on the employee form (HR Manager only).
* Wizard + QWeb PDF report for per-employee audit reporting with date range.
* Daily-friendly garbage collector ``_gc_old_logs(retention_days=730)``.

Opt-out per call::

    record.with_context(hr_uae_skip_audit=True).write(...)
