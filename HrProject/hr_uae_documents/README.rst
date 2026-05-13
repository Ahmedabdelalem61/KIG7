================
HR UAE Documents
================

Typed employee documents with expiry tracking.

Features
========

* Model ``hr.uae.document`` with fixed types: Passport / Visa / Medical /
  Photo / Contract / Other.
* Computed ``days_to_expiry`` and color-coded ``expiry_state``
  (Expired / <30 / <60 / <90 days / OK).
* Daily cron e-mails ``HR Manager`` users about documents expiring within 90
  days using a translatable ``mail.template``.
* ``Documents`` smart-button + tab on the employee form.
* Record rules:

  - ``Document Owner`` group sees only their own documents.
  - ``HR Manager`` and ``Finance`` see everything in their company.

* Auto-tracked through ``hr_uae_audit_trail``.
