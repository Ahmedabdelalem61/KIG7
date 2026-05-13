==================
HR UAE Master Data
==================

Single source of truth for the UAE HR Admin platform.

What it adds
============

* New models ``hr.uae.rank`` and ``hr.uae.position`` (seed data included).
* Two analytic plans: **Project Allocation** and **Cost Center**.
* Cost center analytic accounts are auto-created on employee creation
  (same name as the employee), kept in sync on rename, and archived
  when the employee is archived.
* Extends ``hr.employee`` with passport, roster, position, rank,
  project allocation, cost center, location, nationality, age,
  date of joining, time of service, visa expiry & status, and a
  computed ``UAE Status`` (Active / Vacations / Special Permit /
  Sick Leave / Resignation / Cancellation / Terminated) with manual
  override.
* Daily cron recomputes UAE Status for non-overridden employees.

This module is the data backbone for every following ``hr_uae_*``
module.
