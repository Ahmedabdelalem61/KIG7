# -*- coding: utf-8 -*-
"""Backfill hr_uae_state_id for employees upgraded from pre-tag releases."""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    employees = env["hr.employee"].search([("hr_uae_state_manual", "=", False)])
    employees._compute_hr_uae_state_id()
    _logger.info(
        "hr_uae_master_data 18.0.1.0.3: backfilled hr_uae_state_id for %s employees",
        len(employees),
    )
