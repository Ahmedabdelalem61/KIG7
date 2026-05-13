# -*- coding: utf-8 -*-
"""Copy UAE duplicate columns into standard hr.employee columns before ORM drops them."""

import logging

_logger = logging.getLogger(__name__)


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())


def migrate(cr, version):
    if not _column_exists(cr, "hr_employee", "passport_no"):
        _logger.info("hr_uae_master_data 18.0.1.0.1: passport_no column absent, skip passport merge")
    else:
        cr.execute(
            """
            UPDATE hr_employee
            SET passport_id = passport_no
            WHERE passport_no IS NOT NULL
              AND btrim(passport_no) <> ''
              AND (passport_id IS NULL OR btrim(passport_id) = '')
            """
        )
        _logger.info("hr_uae_master_data 18.0.1.0.1: merged passport_no -> passport_id (%s rows)", cr.rowcount)

    if not _column_exists(cr, "hr_employee", "nationality_id"):
        _logger.info("hr_uae_master_data 18.0.1.0.1: nationality_id column absent, skip country merge")
    else:
        cr.execute(
            """
            UPDATE hr_employee
            SET country_id = nationality_id
            WHERE nationality_id IS NOT NULL
              AND country_id IS NULL
            """
        )
        _logger.info("hr_uae_master_data 18.0.1.0.1: merged nationality_id -> country_id (%s rows)", cr.rowcount)

    if not _column_exists(cr, "hr_employee", "visa_expiry"):
        _logger.info("hr_uae_master_data 18.0.1.0.1: visa_expiry column absent, skip visa merge")
    else:
        cr.execute(
            """
            UPDATE hr_employee
            SET visa_expire = visa_expiry
            WHERE visa_expiry IS NOT NULL
              AND visa_expire IS NULL
            """
        )
        _logger.info("hr_uae_master_data 18.0.1.0.1: merged visa_expiry -> visa_expire (%s rows)", cr.rowcount)
