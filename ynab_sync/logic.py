import logging
from collections import defaultdict
from datetime import date
from uuid import UUID

from requests import HTTPError

from ynab_sync.gocardless.models import GoCardlessBankAccountData

from .gocardless.api import GoCardLessAPI
from .ynab.api import YnabAPI
from .ynab.models import YNABTransaction, YNABTransactions


def get_gocardless_transactions(
    secret_id: str,
    secret_key: str,
    account_id: UUID,
    date_from: date | None = None,
    date_to: date | None = None,
) -> GoCardlessBankAccountData:
    log = logging.getLogger("logic.get_gocardless_transactions")

    try:
        gocardless_api = GoCardLessAPI(secret_id=secret_id, secret_key=secret_key)

        return gocardless_api.get_transactions(
            account_id=account_id, date_from=date_from, date_to=date_to
        )
    except HTTPError as exc:
        log.exception("GoCardless returned HTTPError", exc_info=exc)
        raise


def prepare_ynab_transactions(
    gocardless_bank_data: GoCardlessBankAccountData, ynab_account_id: UUID
) -> YNABTransactions:
    log = logging.getLogger("logic.prepare_ynab_transactions")
    transactions = []
    occurances = defaultdict(int)
    for gocardless_transaction in gocardless_bank_data.transactions.booked:
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

    log.info("%s transactions reported by GoCardless", len(transactions))
    log.debug("transactions: %s", transactions)
    return YNABTransactions(transactions=transactions)


def upload_to_ynab(
    transactions: YNABTransactions,
    token: str,
    budget_id: UUID,
) -> None:
    log = logging.getLogger("logic.upload_to_ynab")

    if not transactions:
        log.info("Transactions are empty, nothing to upload")
        return

    ynab_api = YnabAPI(access_token=token)
    transactions_json = transactions.model_dump_json()

    try:
        response = ynab_api.post_transactions(
            budget_id=budget_id, json_data=transactions_json
        )
    except HTTPError as exc:
        log.exception(
            "YNAB returned HTTPError: payload: %s",
            transactions_json,
            exc_info=exc,
        )
        raise

    log.debug("YNAB response: %s", response)
