import logging
import os
import sys
from datetime import date
from uuid import UUID

import appeal

app = appeal.Appeal()

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

from .logic import (get_gocardless_transactions, prepare_ynab_transactions,
                    upload_to_ynab)


@app.command()
def upload(
    *,
    ynab_token: str = "",
    ynab_budget_id: str = "",
    ynab_account_id: str = "",
    gocardless_secret_id: str = "",
    gocardless_secret_key: str = "",
    gocardless_account_id: str = "",
    date_from: str = "",
    date_to: str = "",
):
    log = logging.getLogger("cli.upload")
    # TODO: Get this from appeal?
    params = {
        "ynab_budget_id": ynab_budget_id,
        "ynab_account_id": ynab_account_id,
        "gocardless_account_id": gocardless_account_id,
    }
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to

    log.info("Started with params: %s ", params)

    error = False
    for name, non_optional in {
        "ynab_token": ynab_token,
        "ynab_budget_id": ynab_budget_id,
        "ynab_account_id": ynab_account_id,
        "gocardless_secret_id": gocardless_secret_id,
        "gocardless_secret_key": gocardless_secret_key,
        "gocardless_account_id": gocardless_account_id,
    }.items():
        if not non_optional:
            print(f"`{name}` parameter should be specified.")
            error = True

    if error:
        return

    gocardless_bank_account_data = get_gocardless_transactions(
        secret_key=gocardless_secret_key,
        secret_id=gocardless_secret_id,
        account_id=UUID(gocardless_account_id),
        date_from=date.fromisoformat(date_from) if date_from else None,
        date_to=date.fromisoformat(date_to) if date_to else None,
    )

    ynab_transactions = prepare_ynab_transactions(
        gocardless_bank_data=gocardless_bank_account_data,
        ynab_account_id=UUID(ynab_account_id),
    )

    upload_to_ynab(
        transactions=ynab_transactions, token=ynab_token, budget_id=UUID(ynab_budget_id)
    )
