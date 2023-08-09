import logging
import sys
import uuid
from collections import defaultdict

import appeal
from requests import HTTPError

from gocardless.api import GoCardLessAPI
from ynab.api import YnabAPI
from ynab.models import YNABTransaction, YNABTransactions

app = appeal.Appeal()

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


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
    log = logging.getLogger("upload")
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

    try:
        gocardless_api = GoCardLessAPI(
            secret_id=gocardless_secret_id, secret_key=gocardless_secret_key
        )

        gocardless_transactions = gocardless_api.get_transactions(
            account_id=gocardless_account_id, date_from=date_from, date_to=date_to
        )
    except HTTPError as exc:
        log.exception("GoCardless returned HTTPError", exc_info=exc)
        return

    transactions = []
    occurances = defaultdict(int)
    for gocardless_transaction in gocardless_transactions.transactions.booked:
        amount = int(gocardless_transaction.transaction_amount.amount * 1000)
        ynab_import_key = f"YNAB:{amount}:{gocardless_transaction.booking_date}"

        memo = (
            gocardless_transaction.remittance_information_unstructured
            or gocardless_transaction.proprietary_bank_transaction_code
            or ""
        )
        occurances[ynab_import_key] += 1
        transactions.append(
            YNABTransaction(
                account_id=ynab_account_id,
                date=gocardless_transaction.booking_date,
                amount=amount,
                payee_name=gocardless_transaction.creditor_name
                or gocardless_transaction.debtor_name
                or "",
                memo=memo,
                cleared="cleared",
                approved=False,
                # import_id=gocardless_transaction.transaction_id,
                import_id=f"{ynab_import_key}:{occurances[ynab_import_key]}",
            )
        )

    if not transactions:
        log.info("No transactions reported by GoCardless, nothing to upload")
        return

    log.info("%s transactions reported by GoCardless", len(transactions))
    log.debug("transactions: %s", transactions)
    ynab_transactions = YNABTransactions(transactions=transactions)

    ynab_api = YnabAPI(access_token=ynab_token)
    transactions_json = ynab_transactions.model_dump_json()

    try:
        response = ynab_api.post_transactions(
            budget_id=ynab_budget_id, json_data=transactions_json
        )
    except HTTPError as exc:
        log.exception(
            "YNAB returned HTTPError: payload: %s",
            transactions_json,
            exc_info=exc,
        )
        return

    log.debug("YNAB response: %s", response)
