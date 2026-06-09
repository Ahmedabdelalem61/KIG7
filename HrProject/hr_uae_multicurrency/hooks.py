import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Back-fill the foreign (contract-currency) amounts from the current
    company-currency amounts for existing contracts.

    Payroll now reads the foreign fields, so they must equal the existing AED
    figures for company-currency contracts (the default). The company-currency
    fields themselves are never modified, so live wages are never at risk.
    """
    contracts = env["hr.contract"].with_context(
        active_test=False, hr_uae_skip_audit=True
    ).search([])
    for contract in contracts:
        company_currency = contract.company_id.currency_id or env.company.currency_id
        vals = {}
        if not contract.contract_currency_id:
            vals["contract_currency_id"] = company_currency.id
        for company_field, foreign_field in contract._hr_uae_money_map().items():
            vals[foreign_field] = contract[company_field]
        contract.write(vals)
    _logger.info(
        "hr_uae_multicurrency: back-filled currency fields for %s contract(s)",
        len(contracts),
    )
