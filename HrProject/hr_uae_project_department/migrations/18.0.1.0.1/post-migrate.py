# -*- coding: utf-8 -*-
"""Backfill project code from linked cost centers."""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    departments = env["hr.department"].search(
        [("project_allocation_id", "!=", False), ("code", "=", False)]
    )
    for department in departments:
        code = (department.project_allocation_id.code or "").strip()
        if code:
            department.code = code
    _logger.info(
        "hr_uae_project_department 18.0.1.0.1: backfilled code on %s projects",
        len(departments),
    )

    Module = env["ir.module.module"].sudo()
    for module_name in ("hr_org_chart", "hr_skills"):
        module = Module.search(
            [("name", "=", module_name), ("state", "=", "installed")],
            limit=1,
        )
        if module:
            try:
                module.button_uninstall()
                _logger.info(
                    "hr_uae_project_department 18.0.1.0.1: uninstalled %s",
                    module_name,
                )
            except Exception as exc:
                _logger.warning(
                    "hr_uae_project_department 18.0.1.0.1: could not uninstall %s: %s",
                    module_name,
                    exc,
                )
