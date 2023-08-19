import decimal
import logging
import os
import sys
from datetime import date
from uuid import UUID

import appeal
from tabulate import tabulate

from ynab_sync.constants import (
    ENV_GOCARDLESS_ACCOUNT_ID,
    ENV_GOCARDLESS_SECRET_ID,
    ENV_GOCARDLESS_SECRET_KEY,
    ENV_YNAB_ACCOUNT_ID,
    ENV_YNAB_BUDGET_ID,
    ENV_YNAB_TOKEN,
)

app = appeal.Appeal()

import logging

from .quickstart import quickstart  # noqa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

from .logic import (
    create_gocardless_requisition,
    get_gocardless_banks,
    get_gocardless_requisition,
    get_gocardless_transactions,
    get_ynab_budget,
    get_ynab_budgets,
    prepare_ynab_transactions,
    upload_to_ynab,
)


@app.command()
def upload(
    *,
    date_from: str = "",
    date_to: str = "",
    ynab_token: str = os.getenv(ENV_YNAB_TOKEN, ""),
    ynab_budget_id: str = os.getenv(ENV_YNAB_BUDGET_ID, ""),
    ynab_account_id: str = os.getenv(ENV_YNAB_ACCOUNT_ID, ""),
    gocardless_secret_id: str = os.getenv(ENV_GOCARDLESS_SECRET_ID, ""),
    gocardless_secret_key: str = os.getenv(ENV_GOCARDLESS_SECRET_KEY, ""),
    gocardless_account_id: str = os.getenv(ENV_GOCARDLESS_ACCOUNT_ID, ""),
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


@app.command()
def ynab():
    ...


@app.command("ynab").command()
def budgets(
    *,
    ynab_token: str = os.getenv(ENV_YNAB_TOKEN),
):
    budgets = get_ynab_budgets(token=ynab_token)

    table = tabulate(
        [(budget.id, budget.name, budget.currency) for budget in budgets],
        headers=["ID", "NAME", "CURRENCY"],
        tablefmt="github",
    )
    print(table)


@app.command("ynab").command()
def accounts(
    *,
    ynab_token: str = os.getenv(ENV_YNAB_TOKEN),
    ynab_budget_id: str = os.getenv(ENV_YNAB_BUDGET_ID),
):
    budget = get_ynab_budget(token=ynab_token, budget_id=UUID(ynab_budget_id))

    table = tabulate(
        [
            (
                account.id,
                account.name,
                account.type,
                f"{budget.currency_symbol}{account.balance / decimal.Decimal(1000)}",
                account.closed,
                account.deleted,
            )
            for account in budget.accounts
        ],
        headers=["ID", "NAME", "TYPE", "BALANCE", "CLOSED", "DELETED"],
        tablefmt="github",
    )
    print(table)


@app.command()
def gocardless():
    ...


@app.command("gocardless").command()
def banks(
    country: str,
    *,
    gocardless_secret_id: str = os.getenv(ENV_GOCARDLESS_SECRET_ID, ""),
    gocardless_secret_key: str = os.getenv(ENV_GOCARDLESS_SECRET_KEY, ""),
):
    banks = get_gocardless_banks(
        secret_id=gocardless_secret_id,
        secret_key=gocardless_secret_key,
        country=country,
    )
    table = tabulate([(bank.id, bank.name) for bank in banks], headers=["ID", "NAME"])

    print(table)


@app.command("gocardless").command()
def generate_bank_auth_link(
    institution_id: str,
    *,
    gocardless_secret_id: str = os.getenv(ENV_GOCARDLESS_SECRET_ID, ""),
    gocardless_secret_key: str = os.getenv(ENV_GOCARDLESS_SECRET_KEY, ""),
):
    requisition = create_gocardless_requisition(
        secret_id=gocardless_secret_id,
        secret_key=gocardless_secret_key,
        redirect="",
        institution_id=institution_id,
    )

    print("GOCARDLESS_REQUISITION_ID: ", requisition.id)
    print(
        "Open this link in your browser and proceed with authorization:",
        requisition.link,
    )
    print(
        "Run `gocardless list_requisition_accounts` afterwards to get GOCARDLESS_ACCOUNT_ID"
    )


@app.command("gocardless").command()
def list_requisition_accounts(
    requisition_id: str,
    *,
    gocardless_secret_id: str = os.getenv(ENV_GOCARDLESS_SECRET_ID, ""),
    gocardless_secret_key: str = os.getenv(ENV_GOCARDLESS_SECRET_KEY, ""),
):
    requisition = get_gocardless_requisition(
        secret_id=gocardless_secret_id,
        secret_key=gocardless_secret_key,
        requisition_id=requisition_id,
    )

    table = tabulate(
        [(requisition.id, account) for account in requisition.accounts],
        headers=["GOCARDLESS_REQUISITION_ID", "GOCARDLESS_ACCOUNT_ID"],
    )
    print(table)
